import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class TradingDataPipeline:
    """
    Comprehensive trading data pipeline for USDCAD prediction
    """
    
    def __init__(self):
        self.primary_pairs = [
            'USDCAD', 'EURUSD', 'GBPUSD', 'AUDUSD', 
            'NZDUSD', 'USDCHF', 'USDJPY'
        ]
        
        self.commodities = [
            'XTIUSD',  # WTI Oil
            'XBRUSD',  # Brent Oil
            'XAUUSD',  # Gold
            'XAGUSD'   # Silver
        ]
        
        self.indices = [
            'US30', 'SPX500', 'NAS100', 'VIX'
        ]
        
        self.all_symbols = self.primary_pairs + self.commodities + self.indices
        
        # Strategy configurations
        self.strategies = {
            'EMACrossoverStrategy': {'fast_period': 12, 'slow_period': 26},
            'RSIStrategy': {'period': 14, 'overbought': 70, 'oversold': 30},
            'MACDStrategy': {'fast': 12, 'slow': 26, 'signal': 9},
            'BollingerStrategy': {'period': 20, 'std': 2},
            'ADXStrategy': {'period': 14, 'threshold': 25},
            'BreakoutStrategy': {'lookback': 20, 'volatility_factor': 2},
            'PriceActionStrategy': {'swing_lookback': 5},
            'VolumeStrategy': {'volume_ma': 20},
            'CarryTradeStrategy': {'yield_lookback': 252},
            'MeanReversionStrategy': {'lookback': 50, 'threshold': 2},
            'MomentumStrategy': {'lookback': 20, 'threshold': 0.02},
            'VolatilityStrategy': {'lookback': 20, 'regime_threshold': 1.5},
            'SeasonalityStrategy': {'lookback_years': 3},
            'IntermarketStrategy': {'correlation_window': 60},
            'SentimentStrategy': {'vix_levels': [15, 20, 30]},
        }
        
        # Lookback periods for features
        self.lookback_periods = list(range(0, 11))  # t, t-1, t-2, ..., t-10
        
    def initialize_mt5(self) -> bool:
        """Initialize MetaTrader 5 connection"""
        if not mt5.initialize():
            print("MT5 initialization failed")
            return False
        return True
    
    def get_historical_data(self, symbol: str, start_date: datetime, 
                          end_date: datetime, timeframe=mt5.TIMEFRAME_H1) -> pd.DataFrame:
        """
        Fetch historical data from MT5
        """
        try:
            rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
            if rates is None:
                print(f"No data for {symbol}")
                return pd.DataFrame()
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            df.columns = [f'{symbol}_{col}' for col in df.columns]
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_all_data(self, start_date: str = "2019-01-01", 
                      end_date: str = "2025-01-01") -> Dict[str, pd.DataFrame]:
        """
        Fetch all market data
        """
        if not self.initialize_mt5():
            return {}
            
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        data = {}
        
        for symbol in self.all_symbols:
            print(f"Fetching data for {symbol}...")
            df = self.get_historical_data(symbol, start_dt, end_dt)
            if not df.empty:
                data[symbol] = df
                print(f"✓ {symbol}: {len(df)} records")
            else:
                print(f"✗ {symbol}: No data")
        
        mt5.shutdown()
        return data
    
    def calculate_technical_indicators(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Calculate technical indicators for a symbol
        """
        result = df.copy()
        close_col = f'{symbol}_close'
        high_col = f'{symbol}_high'
        low_col = f'{symbol}_low'
        volume_col = f'{symbol}_tick_volume'
        
        if close_col not in result.columns:
            return result
            
        # Price features
        result[f'{symbol}_returns'] = result[close_col].pct_change()
        result[f'{symbol}_log_returns'] = np.log(result[close_col] / result[close_col].shift(1))
        result[f'{symbol}_volatility'] = result[f'{symbol}_returns'].rolling(20).std()
        
        # EMA Crossover
        config = self.strategies['EMACrossoverStrategy']
        result[f'{symbol}_ema_fast'] = result[close_col].ewm(span=config['fast_period']).mean()
        result[f'{symbol}_ema_slow'] = result[close_col].ewm(span=config['slow_period']).mean()
        result[f'{symbol}_ema_signal'] = np.where(
            result[f'{symbol}_ema_fast'] > result[f'{symbol}_ema_slow'], 1, -1
        )
        
        # RSI
        config = self.strategies['RSIStrategy']
        delta = result[close_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=config['period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=config['period']).mean()
        rs = gain / loss
        result[f'{symbol}_rsi'] = 100 - (100 / (1 + rs))
        result[f'{symbol}_rsi_signal'] = np.where(
            result[f'{symbol}_rsi'] > config['overbought'], -1,
            np.where(result[f'{symbol}_rsi'] < config['oversold'], 1, 0)
        )
        
        # MACD
        config = self.strategies['MACDStrategy']
        ema_fast = result[close_col].ewm(span=config['fast']).mean()
        ema_slow = result[close_col].ewm(span=config['slow']).mean()
        result[f'{symbol}_macd'] = ema_fast - ema_slow
        result[f'{symbol}_macd_signal_line'] = result[f'{symbol}_macd'].ewm(span=config['signal']).mean()
        result[f'{symbol}_macd_histogram'] = result[f'{symbol}_macd'] - result[f'{symbol}_macd_signal_line']
        result[f'{symbol}_macd_signal'] = np.where(
            result[f'{symbol}_macd'] > result[f'{symbol}_macd_signal_line'], 1, -1
        )
        
        # Bollinger Bands
        config = self.strategies['BollingerStrategy']
        sma = result[close_col].rolling(window=config['period']).mean()
        std = result[close_col].rolling(window=config['period']).std()
        result[f'{symbol}_bb_upper'] = sma + (std * config['std'])
        result[f'{symbol}_bb_lower'] = sma - (std * config['std'])
        result[f'{symbol}_bb_signal'] = np.where(
            result[close_col] > result[f'{symbol}_bb_upper'], -1,
            np.where(result[close_col] < result[f'{symbol}_bb_lower'], 1, 0)
        )
        
        # ADX (simplified version)
        config = self.strategies['ADXStrategy']
        if high_col in result.columns and low_col in result.columns:
            plus_dm = result[high_col].diff()
            minus_dm = result[low_col].diff()
            plus_dm = plus_dm.where(plus_dm > 0, 0)
            minus_dm = minus_dm.where(minus_dm < 0, 0).abs()
            
            tr = pd.concat([
                result[high_col] - result[low_col],
                (result[high_col] - result[close_col].shift(1)).abs(),
                (result[low_col] - result[close_col].shift(1)).abs()
            ], axis=1).max(axis=1)
            
            adx_approx = (plus_dm + minus_dm).rolling(config['period']).mean()
            result[f'{symbol}_adx'] = adx_approx
            result[f'{symbol}_adx_signal'] = np.where(
                result[f'{symbol}_adx'] > config['threshold'], 1, 0
            )
        
        # Volume analysis
        if volume_col in result.columns:
            config = self.strategies['VolumeStrategy']
            result[f'{symbol}_volume_ma'] = result[volume_col].rolling(config['volume_ma']).mean()
            result[f'{symbol}_volume_signal'] = np.where(
                result[volume_col] > result[f'{symbol}_volume_ma'], 1, -1
            )
        
        return result
    
    def create_lagged_features(self, df: pd.DataFrame, target_symbol: str = 'USDCAD') -> pd.DataFrame:
        """
        Create lagged features for all symbols
        """
        result = df.copy()
        
        for symbol in self.all_symbols:
            if symbol == target_symbol:
                continue
                
            # Create lagged features for related currencies
            close_col = f'{symbol}_close'
            if close_col in result.columns:
                for lag in self.lookback_periods:
                    if lag > 0:
                        result[f'{symbol}_close_lag_{lag}'] = result[close_col].shift(lag)
                        result[f'{symbol}_returns_lag_{lag}'] = result[f'{symbol}_returns'].shift(lag)
        
        return result
    
    def create_target_variable(self, df: pd.DataFrame, target_symbol: str = 'USDCAD', 
                             horizon: int = 1) -> pd.DataFrame:
        """
        Create target variable (future returns)
        """
        result = df.copy()
        close_col = f'{target_symbol}_close'
        
        if close_col in result.columns:
            # Future returns as target
            result['target'] = result[close_col].shift(-horizon).pct_change()
            
            # Classification target (up/down)
            result['target_class'] = np.where(result['target'] > 0, 1, 0)
            
            # Multi-class target (strong up, up, down, strong down)
            result['target_multiclass'] = pd.cut(
                result['target'], 
                bins=[-np.inf, -0.002, 0, 0.002, np.inf],
                labels=[0, 1, 2, 3]  # strong_down, down, up, strong_up
            )
        
        return result
    
    def prepare_features(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Combine all data and prepare features
        """
        # Start with USDCAD as base
        if 'USDCAD' not in data:
            raise ValueError("USDCAD data not found")
            
        combined_df = data['USDCAD'].copy()
        
        # Add other symbols
        for symbol, df in data.items():
            if symbol != 'USDCAD':
                combined_df = combined_df.join(df, how='left')
        
        # Calculate technical indicators for all symbols
        for symbol in self.all_symbols:
            if symbol in data:
                combined_df = self.calculate_technical_indicators(combined_df, symbol)
        
        # Create lagged features
        combined_df = self.create_lagged_features(combined_df)
        
        # Create target variable
        combined_df = self.create_target_variable(combined_df)
        
        # Add time features
        combined_df['hour'] = combined_df.index.hour
        combined_df['day_of_week'] = combined_df.index.dayofweek
        combined_df['month'] = combined_df.index.month
        combined_df['quarter'] = combined_df.index.quarter
        
        return combined_df
    
    def train_test_split(self, df: pd.DataFrame, train_ratio: float = 0.7, 
                        test_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train, test, and validation sets
        """
        df_clean = df.dropna()
        
        n = len(df_clean)
        train_end = int(n * train_ratio)
        test_end = int(n * (train_ratio + test_ratio))
        
        train_df = df_clean.iloc[:train_end]
        test_df = df_clean.iloc[train_end:test_end]
        val_df = df_clean.iloc[test_end:]
        
        print(f"Train set: {len(train_df)} samples ({train_df.index[0]} to {train_df.index[-1]})")
        print(f"Test set: {len(test_df)} samples ({test_df.index[0]} to {test_df.index[-1]})")
        print(f"Validation set: {len(val_df)} samples ({val_df.index[0]} to {val_df.index[-1]})")
        
        return train_df, test_df, val_df

# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = TradingDataPipeline()
    
    # Fetch data
    print("Fetching historical data...")
    data = pipeline.fetch_all_data("2019-01-01", "2025-01-01")
    
    # Prepare features
    print("Preparing features...")
    features_df = pipeline.prepare_features(data)
    
    # Split data
    train_df, test_df, val_df = pipeline.train_test_split(features_df)
    
    print(f"Feature matrix shape: {features_df.shape}")
    print(f"Available features: {len([col for col in features_df.columns if col not in ['target', 'target_class', 'target_multiclass']])}")