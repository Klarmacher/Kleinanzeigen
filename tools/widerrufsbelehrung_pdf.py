#!/usr/bin/env python3
"""Erzeugt rechtliches/widerrufsbelehrung.pdf aus der Textfassung.

Aufruf: python3 tools/widerrufsbelehrung_pdf.py rechtliches/widerrufsbelehrung.txt rechtliches/widerrufsbelehrung.pdf
Benötigt: pip install reportlab, Schrift DejaVu Sans.
"""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
src, out = sys.argv[1], sys.argv[2]
body = ParagraphStyle("b", fontName="DV", fontSize=9.5, leading=13.5, spaceAfter=6)
h1 = ParagraphStyle("h1", fontName="DVB", fontSize=15, leading=19, spaceAfter=10)
h2 = ParagraphStyle("h2", fontName="DVB", fontSize=11, leading=15, spaceBefore=6, spaceAfter=4)
field = ParagraphStyle("f", parent=body, spaceAfter=16)
esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
text = open(src, encoding="utf-8").read()
beleh, formular = text.split("\nMuster-Widerrufsformular\n", 1)
story = []
for i, block in enumerate(b.strip() for b in beleh.split("\n\n") if b.strip()):
    if i == 0: story.append(Paragraph(esc(block), h1))
    elif block in ("Widerrufsrecht", "Folgen des Widerrufs"): story.append(Paragraph(esc(block), h2))
    elif block == "Ende der Widerrufsbelehrung": story.append(Paragraph("<i>" + esc(block) + "</i>", body))
    else: story.append(Paragraph(esc(block), body))
story += [PageBreak(), Paragraph("Muster-Widerrufsformular", h1)]
for block in (b.strip() for b in formular.split("\n\n") if b.strip()):
    luecke = block.startswith("– ") and not block.startswith("– An ")
    story.append(Paragraph(esc(block) + ("<br/><br/>" + "_" * 70 if luecke else ""), field if luecke else body))
foot = lambda c, d: (c.setFont("DV", 7.5), c.drawString(20*mm, 12*mm, "Selbstbau-Verleih · Inh. Heiko Klischke · Margaretenhof 1 · 14774 Brandenburg an der Havel · Tel. 03381 4108040 · mail@selbstbau-verleih.de"))
SimpleDocTemplate(out, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm,
                  title="Widerrufsbelehrung Selbstbau-Verleih", author="Selbstbau-Verleih").build(story, onFirstPage=foot, onLaterPages=foot)
