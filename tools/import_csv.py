#!/usr/bin/env python3
"""Legt aus einer CSV-Liste (z. B. Excel-Export) Gerätedateien im Katalog an.

Aufruf:
    python3 tools/import_csv.py geraeteliste.csv

Erwartete Spalten (Semikolon oder Komma getrennt, Kopfzeile erforderlich):
    titel; tag; wochenende; woche; kaution; beschreibung; kategorie
Nur "titel" ist Pflicht. Vorhandene Gerätedateien werden nie überschrieben.
"""

import csv
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ZIEL = ROOT / "katalog" / "geraete"
STANDARD_KATEGORIE = "Haus & Garten > Heimwerken"


def slugify(text):
    text = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def zahl(wert):
    wert = (wert or "").strip().replace("€", "").replace(" ", "")
    if not wert:
        return None
    # Deutsches Format: "1.000" = tausend, "12,50" = zwölf fünfzig
    wert = float(wert.replace(".", "").replace(",", "."))
    return int(wert) if wert.is_integer() else wert


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    quelle = Path(sys.argv[1])
    inhalt = quelle.read_text(encoding="utf-8-sig")
    dialekt = csv.Sniffer().sniff(inhalt.splitlines()[0], delimiters=";,")
    zeilen = csv.DictReader(inhalt.splitlines(), dialect=dialekt)

    ZIEL.mkdir(parents=True, exist_ok=True)
    neu = uebersprungen = 0
    for zeile in zeilen:
        zeile = {(k or "").strip().lower(): (v or "").strip() for k, v in zeile.items()}
        titel = zeile.get("titel")
        if not titel:
            continue
        pfad = ZIEL / f"{slugify(titel)}.yaml"
        if pfad.exists():
            uebersprungen += 1
            continue
        preise = {k: zahl(zeile.get(k)) for k in ("tag", "wochenende", "woche")}
        geraet = {
            "titel": titel,
            "kategorie": zeile.get("kategorie") or STANDARD_KATEGORIE,
            "preise": {k: v for k, v in preise.items() if v is not None},
            "kaution": zahl(zeile.get("kaution")),
            "beschreibung": zeile.get("beschreibung") or "",
            "technische_daten": {},
            "zubehoer": [],
            "bilder": [],
            "kleinanzeigen": {"status": "entwurf", "anzeigen_id": None, "online_seit": None},
        }
        pfad.write_text(
            yaml.safe_dump(geraet, allow_unicode=True, sort_keys=False), encoding="utf-8")
        neu += 1
    print(f"{neu} Geräte angelegt, {uebersprungen} bereits vorhanden (übersprungen).")


if __name__ == "__main__":
    main()
