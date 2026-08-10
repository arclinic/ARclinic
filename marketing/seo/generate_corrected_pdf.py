#!/usr/bin/env python3
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Preformatted, ListFlowable, ListItem
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re

pdfmetrics.registerFont(TTFont('ArialCyr', 'C:\\Windows\\Fonts\\arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialCyr-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))

MD_FILE = r'C:\Arclinic\marketing\seo\SEO-AUDIT-CORRECTED-2026-06-09.md'
PDF_FILE = r'C:\Arclinic\marketing\seo\SEO-AUDIT-CORRECTED-arclinic-2026-06-09.pdf'

with open(MD_FILE, 'r', encoding='utf-8-sig') as f:
    md_text = f.read()
lines = md_text.split('\n')

doc = SimpleDocTemplate(
    PDF_FILE, pagesize=A4,
    leftMargin=15*mm, rightMargin=15*mm,
    topMargin=15*mm, bottomMargin=15*mm,
)

h1s = ParagraphStyle('H1', fontSize=16, fontName='ArialCyr-Bold', textColor=HexColor('#1e3a5f'), spaceBefore=8*mm, spaceAfter=3*mm)
h2s = ParagraphStyle('H2', fontSize=13, fontName='ArialCyr-Bold', textColor=HexColor('#1e3a5f'), spaceBefore=5*mm, spaceAfter=2*mm)
h3s = ParagraphStyle('H3', fontSize=11, fontName='ArialCyr-Bold', textColor=HexColor('#2d6a4f'), spaceBefore=4*mm, spaceAfter=2*mm)
h4s = ParagraphStyle('H4', fontSize=10, fontName='ArialCyr-Bold', textColor=HexColor('#1e3a5f'), spaceBefore=3*mm, spaceAfter=1*mm)
body = ParagraphStyle('Body', fontSize=9, leading=12, fontName='ArialCyr', spaceAfter=2*mm)
code = ParagraphStyle('Code', fontSize=7, leading=9, fontName='Courier', backColor=HexColor('#f0f0f0'), leftIndent=3*mm, rightIndent=3*mm, spaceAfter=2*mm)
bullet = ParagraphStyle('Bullet', fontName='ArialCyr', fontSize=9, leading=12, leftIndent=5*mm, spaceAfter=1*mm)
center = ParagraphStyle('Center', fontName='ArialCyr', fontSize=8, alignment=TA_CENTER, textColor=HexColor('#888888'))
score = ParagraphStyle('Score', fontSize=28, fontName='ArialCyr-Bold', textColor=white, alignment=TA_CENTER, backColor=HexColor('#1e3a5f'), spaceBefore=4*mm, spaceAfter=8*mm, borderPadding=6*mm)
subtitle = ParagraphStyle('Subtitle', fontName='ArialCyr', alignment=TA_CENTER, fontSize=10, textColor=HexColor('#666666'))
title = ParagraphStyle('Title', fontSize=22, fontName='ArialCyr-Bold', textColor=HexColor('#1e3a5f'), spaceAfter=6*mm, alignment=TA_CENTER)
tcell = ParagraphStyle('TCell', fontName='ArialCyr', fontSize=7, leading=9)

flow = []
flow.append(Spacer(1, 30*mm))
flow.append(Paragraph('SEO-AUDIT ARclinic', title))
flow.append(Paragraph('arclinic.ru', ParagraphStyle('ST2', fontName='ArialCyr-Bold', fontSize=14, textColor=HexColor('#b8860b'), alignment=TA_CENTER, spaceBefore=0, spaceAfter=10*mm)))
flow.append(Paragraph('09.06.2026 | Исправленный отчёт', subtitle))
flow.append(Paragraph('Медицинская клиника (local service) | 1C-Bitrix', subtitle))
flow.append(Paragraph('Санкт-Петербург, ул. Верейская, 44 к.2', subtitle))
flow.append(Spacer(1, 15*mm))
flow.append(Paragraph('SEO Health Score: 53/100', score))
flow.append(Spacer(1, 5*mm))

i = 0
in_code = False
code_buf = []
table_data = []
in_table = False

while i < len(lines):
    line = lines[i].rstrip()
    
    if line.startswith('```'):
        if in_code:
            flow.append(Preformatted('\n'.join(code_buf), code))
            flow.append(Spacer(1, 2*mm))
            code_buf = []
            in_code = False
        else:
            in_code = True
        i += 1
        continue
    if in_code:
        code_buf.append(line)
        i += 1
        continue
    
    sline = line.strip()
    if sline in ('---', '___'):
        flow.append(HRFlowable(width="100%", thickness=1, color=HexColor('#b8860b')))
        i += 1
        continue
    if sline.startswith('\u2501'):
        i += 1
        continue
    if not sline:
        flow.append(Spacer(1, 1*mm))
        i += 1
        continue
    
    if line.startswith('## '):
        flow.append(Paragraph(line[3:], h2s))
    elif line.startswith('### '):
        flow.append(Paragraph(line[4:], h3s))
    elif line.startswith('# '):
        flow.append(Paragraph(line[2:], h1s))
    elif line.startswith('#### '):
        flow.append(Paragraph(line[5:], h4s))
    elif line.startswith('| '):
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if not cells:
            i += 1
            continue
        sep = line.replace('|', '').replace('-', '').replace(':', '').strip()
        if sep == '':
            i += 1
            continue
        next_line = lines[i+1].strip() if i + 1 < len(lines) else ''
        is_header = next_line.startswith('|') and next_line.replace('|', '').replace('-', '').replace(':', '').strip() == ''
        para_cells = [Paragraph(f'<b>{c}</b>' if is_header else c, tcell) for c in cells]
        table_data.append(para_cells)
        check_next = i + 1 < len(lines)
        if check_next:
            nl = lines[i+1].strip()
            if not (nl.startswith('|')):
                col_w = [190/len(cells)] * len(cells)
                t = Table(table_data, colWidths=[w*mm for w in col_w])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a5f')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ]))
                flow.append(t)
                flow.append(Spacer(1, 3*mm))
                table_data = []
    elif line.startswith('- '):
        text = line[2:]
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        flow.append(Paragraph(f'<bullet>&bull;</bullet>{text}', bullet))
    else:
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        text = re.sub(r'`(.*?)`', r'<tt>\1</tt>', text)
        flow.append(Paragraph(text, body))
    
    i += 1

flow.append(Spacer(1, 15*mm))
flow.append(Paragraph('Generated by SEO Agent for ARclinic', center))

doc.build(flow)
print(f'PDF saved: {PDF_FILE}')
