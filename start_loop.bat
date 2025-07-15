@echo off
echo =============================
echo ♻️ Bot de trading con reinicio automático
echo =============================

:loop
REM Activar entorno virtual
call "C:\Users\pbonafe\OneDrive - Getronics\Documents\programacion\proyecto_trader\venv310\Scripts\activate.bat"

REM Ejecutar el bot y capturar su código de salida
python "C:\Users\pbonafe\OneDrive - Getronics\Documents\programacion\proyecto_trader\trading_bot\main.py"
set EXIT_CODE=%ERRORLEVEL%

REM Verificar si se debe reiniciar
if "%EXIT_CODE%"=="42" (
    echo 🔒 El bot se cerró normalmente a las 23:00. No se reinicia.
    goto fin
)

echo ⚠️ El bot se detuvo inesperadamente. Reiniciando en 10 segundos...
timeout /t 10
goto loop

:fin
echo ✅ Proceso terminado.
pause
