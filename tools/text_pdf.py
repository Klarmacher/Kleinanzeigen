#!/usr/bin/env python3
"""Setzt eine Textdatei aus rechtliches/ als schlichtes A4-PDF.

Aufruf: python3 tools/text_pdf.py rechtliches/datenschutzinformation.txt rechtliches/datenschutzinformation.pdf
Erster Absatz = Titel; einzeilige Absätze ohne Satzzeichen am Ende = Zwischenüberschriften;
ein Absatz, der mit einer Überschriftenzeile beginnt, bekommt diese als Überschrift.
Benötigt: pip install reportlab, Schrift DejaVu Sans.
"""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
body = ParagraphStyle("b", fontName="DV", fontSize=9, leading=12.5, spaceAfter=5)
bullet = ParagraphStyle("u", parent=body, leftIndent=10, firstLineIndent=-8, spaceAfter=2)
h1 = ParagraphStyle("h1", fontName="DVB", fontSize=15, leading=19, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="DVB", fontSize=10.5, leading=14, spaceBefore=7, spaceAfter=3)
esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
ist_ueberschrift = lambda z: len(z) < 70 and not z.startswith("•") and z[-1] not in ".:;,)"

src, out = sys.argv[1], sys.argv[2]
bloecke = [b.strip() for b in open(src, encoding="utf-8").read().split("\n\n") if b.strip()]
story = [Paragraph(esc(bloecke[0]), h1)]
for block in bloecke[1:]:
    zeilen = block.split("\n")
    if ist_ueberschrift(zeilen[0]) and (len(zeilen) > 1 or not zeilen[0].startswith("Stand")):
        story.append(Paragraph(esc(zeilen[0]), h2)); zeilen = zeilen[1:]
    absatz = []
    for z in zeilen:
        if z.startswith("• "):
            if absatz: story.append(Paragraph("<br/>".join(map(esc, absatz)), body)); absatz = []
            story.append(Paragraph(esc(z), bullet))
        else:
            absatz.append(z)
    if absatz: story.append(Paragraph("<br/>".join(map(esc, absatz)), body))

def fuss(c, d):
    c.setFont("DV", 7)
    c.drawString(20*mm, 12*mm, "Selbstbau-Verleih · Inh. Heiko Klischke · Margaretenhof 1 · 14774 Brandenburg an der Havel · Tel. 03381 4108040 · mail@selbstbau-verleih.de")
SimpleDocTemplate(out, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=18*mm, bottomMargin=20*mm,
                  title=bloecke[0], author="Selbstbau-Verleih").build(story, onFirstPage=fuss, onLaterPages=fuss)
