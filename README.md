# Selbstbau-Verleih auf Kleinanzeigen.de

Mietgeräte werden hier als **Katalog** gepflegt. Ein Skript erzeugt daraus
einheitliche Anzeigentexte und eine **Übersichtsseite**, von der aus Titel und
Beschreibung per Knopfdruck kopiert und bei Kleinanzeigen von Hand eingestellt
werden.

## Ordner

| Pfad | Inhalt |
|---|---|
| `katalog/firma.yaml` | Firmendaten und Standardtexte (Mietbedingungen, Lieferung …) – erscheinen in jeder Anzeige |
| `katalog/geraete/*.yaml` | Eine Datei pro Gerät (Titel, Preise, Kaution, Beschreibung, Bilder, Anzeigenstatus) |
| `bilder/` | Gerätefotos |
| `tools/generiere_anzeigen.py` | Erzeugt `ausgabe/uebersicht.html` und je Gerät eine `.txt` |
| `tools/import_csv.py` | Legt viele Geräte auf einmal aus einer CSV/Excel-Liste an |

## Einmalig: Einrichtung

1. Python 3 installieren, dann `pip install -r requirements.txt`.
2. `katalog/firma.yaml` ausfüllen – alle Stellen mit `TODO`.
   Solange dort `TODO` steht, wird der Abschnitt in den Anzeigen weggelassen.
3. Kleinanzeigen-Konto anlegen (siehe Checkliste unten).

## Starten per Doppelklick

- **Windows:** `Anzeigen-erstellen.bat` doppelklicken.
- **Mac:** `Anzeigen-erstellen.command` doppelklicken (beim ersten Mal ggf.
  Rechtsklick → „Öffnen“, weil die Datei aus dem Internet stammt).
- **Linux:** `./Anzeigen-erstellen.command` im Terminal.

Die Startdatei prüft, ob Python da ist, richtet beim ersten Start PyYAML ein,
erzeugt alle Anzeigen und öffnet `ausgabe/uebersicht.html` im Browser.

## Geräte übernehmen

Gerätedatei von Hand anlegen (Vorlage: `katalog/geraete/minibagger-1-5t.yaml`)
**oder** eine Liste importieren. In Excel eine Tabelle mit diesen Spalten anlegen
und als CSV speichern:

```
Titel;Tag;Wochenende;Woche;Kaution;Beschreibung;Kategorie
Rüttelplatte 90 kg;35;59;149;300;Für Pflaster und Schotter;
```

```
python3 tools/import_csv.py geraeteliste.csv
```

Danach Technische Daten, Zubehör und Bilder in den einzelnen Dateien ergänzen.
Die beiden mitgelieferten Geräte sind **Beispiele** – löschen oder überschreiben.

## Anzeige einstellen (pro Gerät ca. 2–3 Minuten)

1. `python3 tools/generiere_anzeigen.py` ausführen.
   Warnungen (Titel zu lang, Bild fehlt …) werden direkt angezeigt.
2. `ausgabe/uebersicht.html` im Browser öffnen.
3. Bei Kleinanzeigen „Anzeige aufgeben“: Kategorie wählen, Titel und Text
   kopieren, Tagespreis als Festpreis eintragen, Fotos hochladen.
4. In der Gerätedatei eintragen:
   ```yaml
   kleinanzeigen:
     status: online
     anzeigen_id: 2xxxxxxxxx      # steht in der Anzeigen-URL
     online_seit: 2026-10-20
   ```
5. Skript erneut ausführen – die Übersicht zeigt jetzt den Status und
   markiert Anzeigen, die in den nächsten 7 Tagen verlängert werden müssen
   (Laufzeit in `firma.yaml` → `laufzeit_tage`).

Empfehlung: mit 5–10 gefragten Geräten starten, Resonanz beobachten, dann
schrittweise erweitern.

## Checkliste Kleinanzeigen-Konto

- [ ] Konto mit Firmen-E-Mail anlegen und als **gewerblicher Anbieter** einrichten.
      Für einen Verleih mit vielen Geräten lohnt sich wahrscheinlich ein
      PRO-Paket (mehr Anzeigen, Firmenseite, Logo) – aktuelle Konditionen bei
      Kleinanzeigen erfragen.
- [ ] **Impressum** hinterlegen (Pflicht für Gewerbetreibende).
- [ ] Logo und Profilbild hochladen, Firmenbeschreibung mit Link zur Website.
- [ ] Mietbedingungen und AGB-Hinweis in `firma.yaml` ergänzen;
      rechtliche Pflichtangaben (z. B. Widerrufsbelehrung bei Fernabsatz)
      ggf. vom Anwalt/IHK prüfen lassen.
- [ ] Passende Kategorie für Mietangebote beim ersten Einstellen prüfen und in
      den Gerätedateien (`kategorie`) vereinheitlichen.
- [ ] Anzeigen **nicht automatisiert** (per Bot) einstellen – das verstößt gegen
      die Nutzungsbedingungen und kann zur Kontosperrung führen.

## Auf dem eigenen PC speichern und mit GitHub abgleichen (Windows)

Einmalig einrichten:

1. **Git für Windows** installieren: https://git-scm.com/download/win
   (alle Voreinstellungen übernehmen).
2. **GitHub Desktop** installieren: https://desktop.github.com und mit dem
   GitHub-Konto anmelden.
3. In GitHub Desktop: *File → Clone repository* → `Klarmacher/Kleinanzeigen`
   wählen, als Ziel z. B. `C:\Selbstbau-Verleih` angeben → *Clone*.
4. Oben bei *Current branch* den Zweig `claude/adoring-dirac-80l6ro` wählen
   (dort liegen alle Anzeigen).
5. Im Ordner `C:\Selbstbau-Verleih\Kleinanzeigen` doppelt auf
   **GitHub-Sync-einrichten.bat** klicken. Beim ersten Mal öffnet sich ggf.
   ein Fenster zur GitHub-Anmeldung.

Danach gleicht Windows den Ordner **jede Stunde** automatisch mit GitHub ab:
eigene Änderungen werden hochgeladen, neue Anzeigen von Claude werden
heruntergeladen. Sofort abgleichen: **GitHub-Synchronisieren.bat**
doppelklicken. Protokoll: `sync-log.txt`.

Hinweis: Wird dieselbe Datei gleichzeitig am PC und von Claude geändert,
bricht der Abgleich mit einer Fehlermeldung ab, statt etwas zu überschreiben.
Dann Claude Bescheid geben.

## Preisspiegel (Konkurrenzpreise)

`preisspiegel/index.html` ist der Quelltext der Preisvergleichsseite, die als
claude.ai-Artifact veröffentlicht ist: https://claude.ai/artifact/7PdDiDHLmXudoia9Ej1X8X

- Eigene Geräte mit Tages-, Wochenend- und Wochenpreis anlegen.
- Wettbewerber (Firma, Website, Ort, Entfernung) eintragen.
- Preise je Wettbewerber von Hand erfassen **oder** den Text der Preisseite
  einfügen und per KI auslesen und zuordnen lassen (Ergebnis wird vor dem
  Speichern geprüft).
- KI-Vorschläge für Verleiher in der Region (aus KI-Wissen, ohne Live-Suche –
  bitte prüfen).
- Die Übersicht zeigt je Gerät den günstigsten Wettbewerber, den Durchschnitt
  und ob der eigene Tagespreis günstiger, im Markt (±5 %) oder teurer ist.
- Bei jedem Gerät mit fertiger Anzeige führt der Knopf **„Anzeige“** zu Titel,
  Preisfeld, Kategorie, Beschreibung und Fotos – mit Kopier- und Speicherknöpfen.
  Die Daten stammen aus `ausgabe/anzeigen.json` (vom Generator erzeugt) und
  werden von Claude in den Preisspiegel übertragen.
