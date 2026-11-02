@echo off
rem Doppelklick: erzeugt alle Anzeigen und oeffnet die Uebersicht im Browser.
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"

set PY=
where py >nul 2>nul && set PY=py -3
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo Python wurde nicht gefunden.
  echo Bitte Python 3 von https://www.python.org/downloads/ installieren
  echo und dabei "Add python.exe to PATH" ankreuzen. Danach erneut starten.
  pause
  exit /b 1
)

%PY% -c "import yaml" 2>nul || (
  echo Einmalige Einrichtung: PyYAML wird installiert ...
  %PY% -m pip install --user -r requirements.txt || (
    echo Installation fehlgeschlagen. Bitte Internetverbindung pruefen.
    pause
    exit /b 1
  )
)

%PY% tools\generiere_anzeigen.py
if errorlevel 1 (
  echo.
  echo Beim Erzeugen ist ein Fehler aufgetreten, siehe Meldung oben.
  pause
  exit /b 1
)

start "" "ausgabe\uebersicht.html"
echo.
echo Fertig. Die Uebersicht wurde im Browser geoeffnet.
pause
