#!/usr/bin/env python3
"""Erzeugt aus dem Katalog fertige Kleinanzeigen-Texte und eine Übersichtsseite.

Aufruf (im Projektordner):
    python3 tools/generiere_anzeigen.py

Ergebnis:
    ausgabe/uebersicht.html   – im Browser öffnen, Titel/Text per Knopf kopieren
    ausgabe/<geraet>.txt      – derselbe Anzeigentext als Textdatei
"""

import datetime
import html
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
KATALOG = ROOT / "katalog"
AUSGABE = ROOT / "ausgabe"

TITEL_MAX = 65          # Zeichenlimit Kleinanzeigen-Titel
BESCHREIBUNG_MAX = 4000  # Zeichenlimit Kleinanzeigen-Beschreibung
PREIS_LABEL = {"tag": "1 Tag", "wochenende": "Wochenende", "woche": "1 Woche"}


def lade(pfad):
    with open(pfad, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def euro(betrag):
    betrag = float(betrag)
    if betrag.is_integer():
        return f"{int(betrag)} €"
    return f"{betrag:.2f} €".replace(".", ",")


def baue_titel(geraet, firma):
    titel = geraet["titel"].strip()
    zusatz = (firma.get("titel_zusatz") or "").strip()
    if zusatz and zusatz.lower() not in titel.lower():
        mit_zusatz = f"{titel} {zusatz}"
        if len(mit_zusatz) <= TITEL_MAX:
            return mit_zusatz
    return titel


def abschnitt(text):
    text = (text or "").strip()
    return text if text and "TODO" not in text else ""


def baue_beschreibung(geraet, firma):
    teile = []
    teile.append(f"{geraet['titel'].strip()} zu vermieten – {firma['name']}")
    if e := abschnitt(firma.get("einleitung")):
        teile.append(e)
    if b := abschnitt(geraet.get("beschreibung")):
        teile.append(b)

    if daten := geraet.get("technische_daten"):
        teile.append("Technische Daten:\n" + "\n".join(f"• {k}: {v}" for k, v in daten.items()))
    if zub := geraet.get("zubehoer"):
        teile.append("Im Lieferumfang:\n" + "\n".join(f"• {z}" for z in zub))

    preise = geraet.get("preise") or {}
    zeilen = [f"• {PREIS_LABEL.get(k, k)}: {euro(v)}" for k, v in preise.items()]
    if geraet.get("kaution"):
        zeilen.append(f"• Kaution: {euro(geraet['kaution'])}")
    if zeilen:
        hinweis = (firma.get("preis_hinweis") or "inkl. MwSt.").strip()
        teile.append(f"Mietpreise ({hinweis}):\n" + "\n".join(zeilen))

    if h := abschnitt(geraet.get("hinweise")):
        teile.append(h)
    if m := abschnitt(firma.get("mietbedingungen")):
        teile.append("Mietbedingungen:\n" + m)
    if l := abschnitt(firma.get("lieferung")):
        teile.append(l)

    kontakt = [firma["name"]]
    for feld in ("adresse", "telefon", "oeffnungszeiten", "website"):
        wert = str(firma.get(feld) or "")
        if wert and "TODO" not in wert:
            kontakt.append(("Öffnungszeiten: " if feld == "oeffnungszeiten" else "") + wert)
    teile.append("\n".join(kontakt))

    if s := abschnitt(firma.get("schluss")):
        teile.append(s)
    return "\n\n".join(teile)


def pruefe(slug, geraet, titel, text, firma):
    warnungen = []
    if len(titel) > TITEL_MAX:
        warnungen.append(f"Titel zu lang ({len(titel)}/{TITEL_MAX} Zeichen)")
    if len(text) > BESCHREIBUNG_MAX:
        warnungen.append(f"Beschreibung zu lang ({len(text)}/{BESCHREIBUNG_MAX} Zeichen)")
    if not (geraet.get("preise") or {}).get("tag"):
        warnungen.append("Kein Tagespreis (wird im Preisfeld gebraucht)")
    if not geraet.get("bilder"):
        warnungen.append("Keine Bilder hinterlegt")
    for bild in geraet.get("bilder") or []:
        if not (ROOT / bild).exists():
            warnungen.append(f"Bild fehlt: {bild}")
    return warnungen


def faellig_am(geraet, firma):
    ka = geraet.get("kleinanzeigen") or {}
    seit = ka.get("online_seit")
    if ka.get("status") != "online" or not seit:
        return None
    if isinstance(seit, str):
        seit = datetime.date.fromisoformat(seit)
    return seit + datetime.timedelta(days=int(firma.get("laufzeit_tage", 60)))


def main():
    firma = lade(KATALOG / "firma.yaml")
    dateien = sorted((KATALOG / "geraete").glob("*.yaml"))
    if not dateien:
        sys.exit("Keine Geräte in katalog/geraete/ gefunden.")

    AUSGABE.mkdir(exist_ok=True)
    heute = datetime.date.today()
    eintraege = []
    for pfad in dateien:
        slug = pfad.stem
        geraet = lade(pfad)
        titel = baue_titel(geraet, firma)
        text = baue_beschreibung(geraet, firma)
        (AUSGABE / f"{slug}.txt").write_text(f"{titel}\n\n{text}\n", encoding="utf-8")
        eintraege.append({
            "slug": slug,
            "geraet": geraet,
            "titel": titel,
            "text": text,
            "warnungen": pruefe(slug, geraet, titel, text, firma),
            "faellig": faellig_am(geraet, firma),
        })

    firma_todos = [k for k, v in firma.items() if isinstance(v, str) and "TODO" in v]
    (AUSGABE / "uebersicht.html").write_text(
        render_html(eintraege, firma, firma_todos, heute), encoding="utf-8")

    print(f"{len(eintraege)} Anzeigen erzeugt → {AUSGABE / 'uebersicht.html'}")
    if firma_todos:
        print("Noch offen in katalog/firma.yaml: " + ", ".join(firma_todos))
    for e in eintraege:
        for w in e["warnungen"]:
            print(f"  ⚠ {e['slug']}: {w}")


def render_html(eintraege, firma, firma_todos, heute):
    def status_badge(e):
        ka = e["geraet"].get("kleinanzeigen") or {}
        status = ka.get("status") or "entwurf"
        if e["faellig"] and e["faellig"] <= heute + datetime.timedelta(days=7):
            return f'<span class="badge warn">verlängern bis {e["faellig"]:%d.%m.%Y}</span>'
        return f'<span class="badge {status}">{html.escape(status)}</span>'

    karten = []
    for i, e in enumerate(eintraege):
        g = e["geraet"]
        warn = "".join(f"<li>{html.escape(w)}</li>" for w in e["warnungen"])
        bilder = "".join(
            f'<li><code>{html.escape(b)}</code></li>' for b in g.get("bilder") or [])
        tag = (g.get("preise") or {}).get("tag")
        karten.append(f"""
<article data-status="{html.escape((g.get('kleinanzeigen') or {}).get('status') or 'entwurf')}">
  <header><h2>{html.escape(g['titel'])}</h2>{status_badge(e)}</header>
  {'<ul class="warn">' + warn + '</ul>' if warn else ''}
  <dl>
    <dt>Kategorie</dt><dd>{html.escape(str(g.get('kategorie', '–')))}</dd>
    <dt>Preisfeld</dt><dd>{euro(tag) + ' (Festpreis, pro Tag)' if tag else '–'}</dd>
    <dt>Bilder</dt><dd>{'<ul>' + bilder + '</ul>' if bilder else '–'}</dd>
  </dl>
  <div class="feld"><label>Titel ({len(e['titel'])}/{TITEL_MAX})</label>
    <button onclick="kopiere('t{i}', this)">Titel kopieren</button>
    <input id="t{i}" readonly value="{html.escape(e['titel'])}"></div>
  <div class="feld"><label>Beschreibung ({len(e['text'])}/{BESCHREIBUNG_MAX})</label>
    <button onclick="kopiere('b{i}', this)">Text kopieren</button>
    <textarea id="b{i}" readonly rows="12">{html.escape(e['text'])}</textarea></div>
</article>""")

    hinweis = ""
    if firma_todos:
        hinweis = ('<p class="todo">Noch auszufüllen in <code>katalog/firma.yaml</code>: '
                   + html.escape(", ".join(firma_todos)) + "</p>")

    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(firma['name'])} – Kleinanzeigen</title>
<style>
:root {{ --bg:#f6f6f4; --card:#fff; --text:#1c1c1c; --muted:#666; --line:#ddd;
  --accent:#2f6f3e; --warn:#b5560a; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#161616; --card:#222; --text:#eee;
  --muted:#aaa; --line:#3a3a3a; --accent:#6cc085; --warn:#f0a35e; }} }}
body {{ margin:0; padding:16px; background:var(--bg); color:var(--text);
  font:15px/1.5 system-ui, sans-serif; }}
main {{ max-width:860px; margin:auto; }}
article {{ background:var(--card); border:1px solid var(--line); border-radius:8px;
  padding:16px; margin:16px 0; }}
article header {{ display:flex; justify-content:space-between; align-items:center; gap:8px; }}
h2 {{ margin:0; font-size:1.15rem; }}
.badge {{ font-size:.8rem; padding:2px 8px; border-radius:99px; border:1px solid var(--line); }}
.badge.online {{ color:var(--accent); border-color:var(--accent); }}
.badge.warn, ul.warn, .todo {{ color:var(--warn); }}
dl {{ display:grid; grid-template-columns:max-content 1fr; gap:4px 12px; }}
dt {{ color:var(--muted); }} dd {{ margin:0; }} dd ul {{ margin:0; padding-left:18px; }}
.feld {{ margin-top:12px; }}
.feld label {{ color:var(--muted); font-size:.85rem; margin-right:8px; }}
input, textarea {{ box-sizing:border-box; width:100%; margin-top:4px; padding:8px;
  font:inherit; background:var(--bg); color:var(--text); border:1px solid var(--line);
  border-radius:6px; }}
button {{ font:inherit; font-size:.85rem; padding:3px 10px; cursor:pointer;
  border:1px solid var(--accent); color:var(--accent); background:transparent; border-radius:6px; }}
nav button.aktiv {{ background:var(--accent); color:var(--card); }}
</style></head><body><main>
<h1>{html.escape(firma['name'])} – Kleinanzeigen</h1>
<p>{len(eintraege)} Geräte · erzeugt am {heute:%d.%m.%Y}</p>
{hinweis}
<nav>Filter:
  <button class="aktiv" onclick="filter('', this)">alle</button>
  <button onclick="filter('entwurf', this)">entwurf</button>
  <button onclick="filter('online', this)">online</button>
  <button onclick="filter('pausiert', this)">pausiert</button>
</nav>
{''.join(karten)}
</main>
<script>
function kopiere(id, knopf) {{
  const el = document.getElementById(id);
  const fertig = () => {{ const t = knopf.textContent; knopf.textContent = 'Kopiert ✓';
    setTimeout(() => knopf.textContent = t, 1500); }};
  if (navigator.clipboard) navigator.clipboard.writeText(el.value).then(fertig);
  else {{ el.select(); document.execCommand('copy'); fertig(); }}
}}
function filter(status, knopf) {{
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('aktiv'));
  knopf.classList.add('aktiv');
  document.querySelectorAll('article').forEach(a =>
    a.style.display = !status || a.dataset.status === status ? '' : 'none');
}}
</script></body></html>
"""


if __name__ == "__main__":
    main()
