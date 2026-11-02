#!/bin/bash
# Doppelklick (Mac) bzw. ./Anzeigen-erstellen.command (Linux):
# erzeugt alle Anzeigen und öffnet die Übersicht im Browser.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 wurde nicht gefunden. Bitte von https://www.python.org/downloads/ installieren."
  read -r -p "Enter zum Schließen …"; exit 1
fi

if ! python3 -c "import yaml" 2>/dev/null; then
  echo "Einmalige Einrichtung: PyYAML wird installiert …"
  python3 -m pip install --user -r requirements.txt || {
    echo "Installation fehlgeschlagen. Bitte Internetverbindung prüfen."
    read -r -p "Enter zum Schließen …"; exit 1; }
fi

python3 tools/generiere_anzeigen.py || { read -r -p "Fehler, siehe oben. Enter zum Schließen …"; exit 1; }

if command -v open >/dev/null 2>&1; then open ausgabe/uebersicht.html
elif command -v xdg-open >/dev/null 2>&1; then xdg-open ausgabe/uebersicht.html >/dev/null 2>&1 &
fi
echo; echo "Fertig. Die Übersicht liegt unter ausgabe/uebersicht.html"
