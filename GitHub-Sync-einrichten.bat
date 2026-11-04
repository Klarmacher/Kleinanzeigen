@echo off
rem Doppelklick (einmalig): richtet den automatischen Abgleich mit GitHub ein - stuendlich.
chcp 65001 >nul
setlocal
cd /d "%~dp0"
where git >nul 2>nul || (
  echo Git wurde nicht gefunden. Bitte zuerst Git fuer Windows installieren:
  echo https://git-scm.com/download/win
  pause
  exit /b 1
)

echo Erster Abgleich (beim ersten Mal oeffnet sich ggf. ein GitHub-Anmeldefenster) ...
call "%~dp0GitHub-Synchronisieren.bat" /still
type "%~dp0sync-log.txt"

schtasks /Create /F /TN "Selbstbau-Verleih GitHub-Sync" /SC HOURLY /TR "\"%~dp0GitHub-Synchronisieren.bat\" /still"
if errorlevel 1 (
  echo Die geplante Aufgabe konnte nicht angelegt werden.
  pause
  exit /b 1
)
echo.
echo Eingerichtet: Der Ordner wird jetzt jede Stunde mit GitHub abgeglichen.
echo Protokoll: sync-log.txt in diesem Ordner.
echo Abschalten: Aufgabenplanung oeffnen und "Selbstbau-Verleih GitHub-Sync" loeschen,
echo oder in der Eingabeaufforderung: schtasks /Delete /TN "Selbstbau-Verleih GitHub-Sync" /F
pause
