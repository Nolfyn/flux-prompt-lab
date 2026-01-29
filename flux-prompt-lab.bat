@echo off

cd /d "%~dp0"

set "VENV_PY=%~dp0venv\Scripts\python.exe"
set "HOST=127.0.0.1"
set "PORT=7860"
set "URL=http://%HOST%:%PORT%/"

REM Проверка наличия app.py
if not exist "%~dp0app.py" (
  echo Ошибка: не найден app.py в директории "%~dp0"
  pause
  exit /b 1
)

REM Запускаем сервер в новом окне (чтобы текущий батник продолжил выполнение)
if exist "%VENV_PY%" (
  echo Starting server with virtualenv python: "%VENV_PY%"
  start "Flux Prompt Lab" "%VENV_PY%" "%~dp0app.py"
) else (
  echo Virtualenv not found at "%VENV_PY%". Starting with system python...
  start "Flux Prompt Lab" python "%~dp0app.py"
)

echo Waiting for server at %HOST%:%PORT% ...

REM Ждём появления открытого TCP-порта и затем открываем браузер.
powershell -NoProfile -Command ^
  "$h = '%HOST%'; $p = %PORT%; while ($true) { try { $c = New-Object System.Net.Sockets.TcpClient; $c.Connect($h,$p); $c.Close(); break } catch { Start-Sleep -Milliseconds 200 } }; Start-Process '%URL%'"

pause
