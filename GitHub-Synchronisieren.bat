@echo off
rem Doppelklick: gleicht diesen Ordner mit GitHub ab (eigene Aenderungen hoch, neue Aenderungen runter).
rem Mit dem Zusatz /still (fuer die geplante Aufgabe) ohne Pause, Ausgabe in sync-log.txt.
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if /i "%~1"=="/still" (
  call :sync >> "%~dp0sync-log.txt" 2>&1
  exit /b
)
call :sync
pause
exit /b

:sync
echo ===== %DATE% %TIME% =====
where git >nul 2>nul || (
  echo Git wurde nicht gefunden. Bitte Git fuer Windows installieren:
  echo https://git-scm.com/download/win
  exit /b 1
)
git config user.name >nul 2>nul || git config user.name "Heiko Klischke"
git config user.email >nul 2>nul || git config user.email "mail@selbstbau-verleih.de"

rem 1. Eigene Aenderungen auf diesem PC sichern
git add -A
git diff --cached --quiet || git commit -q -m "Aenderungen vom PC %COMPUTERNAME%"

rem 2. Neue Aenderungen von GitHub holen
git pull --no-rebase --no-edit -q
if errorlevel 1 (
  echo FEHLER beim Abholen von GitHub. Moegliche Ursachen: keine Internetverbindung,
  echo nicht angemeldet oder dieselbe Datei wurde hier und auf GitHub geaendert.
  echo Bitte Claude Bescheid geben und diese Meldung mitschicken.
  exit /b 1
)

rem 3. Eigene Aenderungen hochladen
git push -q
if errorlevel 1 (
  echo FEHLER beim Hochladen zu GitHub.
  exit /b 1
)
echo Fertig: Ordner und GitHub sind auf demselben Stand.
exit /b 0
