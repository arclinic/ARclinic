#!/usr/bin/env python3
"""Конвертирует MD-отчёт в PDF с помощью ReportLab."""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, ListFlowable, ListItem, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable


def md_to_pdf(md_path: str, pdf_path: str):
    """Конвертирует Markdown в PDF с помощью ReportLab."""
    
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        topMargin=2*cm,
        bottomMargin=2*cm,
        leftMargin=1.8*cm,
        rightMargin=1.8*cm,
    )

    styles = getSampleStyleSheet()
    
    # Кастомные стили
    styles.add(ParagraphStyle(
        'Title1', parent=styles['Heading1'],
        fontSize=18, textColor=HexColor('#1a1a2e'),
        spaceAfter=10, spaceBefore=6,
        borderWidth=0, borderPadding=0,
        borderColor=HexColor('#e94560'),
    ))
    styles.add(ParagraphStyle(
        'Title2', parent=styles['Heading2'],
        fontSize=14, textColor=HexColor('#16213e'),
        spaceAfter=8, spaceBefore=16,
    ))
    styles.add(ParagraphStyle(
        'Title3', parent=styles['Heading3'],
        fontSize=12, textColor=HexColor('#0f3460'),
        spaceAfter=6, spaceBefore=12,
    ))
    styles.add(ParagraphStyle(
        'Normal2', parent=styles['Normal'],
        fontSize=10, leading=14,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'Bullet2', parent=styles['Normal'],
        fontSize=10, leading=14,
        leftIndent=15, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontSize=9, leading=12,
    ))
    styles.add(ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontSize=9, leading=12,
        textColor=white,
    ))
    styles.add(ParagraphStyle(
        'CodeStyle', parent=styles['Normal'],
        fontSize=8, leading=10,
        fontName='Courier',
        leftIndent=10,
        backColor=HexColor('#f0f0f0'),
    ))

    elements = []
    in_table = False
    table_rows = []
    in_code = False
    code_lines = []
    in_list = False
    list_items = []

    def flush_code():
        nonlocal in_code, code_lines
        if code_lines:
            text = '<br/>'.join(code_lines)
            elements.append(Paragraph(text, styles['CodeStyle']))
            elements.append(Spacer(1, 4))
            code_lines = []

    def flush_list():
        nonlocal in_list, list_items
        if list_items:
            for item in list_items:
                elements.append(Paragraph(f"• {item}", styles['Bullet2']))
            list_items = []

    def flush_table():
        nonlocal in_table, table_rows
        if table_rows and len(table_rows) > 1:
            # Первая строка — заголовок
            header = table_rows[0]
            data_rows = table_rows[1:]
            
            # Определяем кол-во колонок
            ncols = max(len(r) for r in table_rows)
            
            # Подготавливаем данные
            table_data = []
            # Заголовок
            hdr = []
            for c in header:
                hdr.append(Paragraph(f"<b>{c}</b>", styles['TableHeader']))
            while len(hdr) < ncols:
                hdr.append(Paragraph("", styles['TableHeader']))
            table_data.append(hdr)
            
            # Данные
            for row in data_rows:
                r = []
                for c in row:
                    r.append(Paragraph(c, styles['TableCell']))
                while len(r) < ncols:
                    r.append(Paragraph("", styles['TableCell']))
                table_data.append(r)
            
            col_widths = [doc.width / ncols] * ncols
            
            t = Table(table_data, colWidths=col_widths, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8f9fa'), white]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 8))
        
        table_rows = []
        in_table = False

    for line in lines:
        stripped = line.rstrip()
        
        # Пропускаем разделители
        if re.match(r'^---+$', stripped):
            flush_code()
            flush_list()
            flush_table()
            elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#dddddd')))
            elements.append(Spacer(1, 6))
            continue
        
        # Заголовки
        if stripped.startswith('# '):
            flush_code(); flush_list(); flush_table()
            elements.append(Paragraph(stripped[2:], styles['Title1']))
            continue
        if stripped.startswith('## '):
            flush_code(); flush_list(); flush_table()
            elements.append(Paragraph(stripped[3:], styles['Title2']))
            continue
        if stripped.startswith('### '):
            flush_code(); flush_list(); flush_table()
            elements.append(Paragraph(stripped[4:], styles['Title3']))
            continue
        
        # Таблицы
        if stripped.startswith('|') and stripped.endswith('|'):
            flush_code(); flush_list()
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            
            # Пропускаем разделительную строку
            if re.match(r'^[\s|:\-]+$', stripped):
                continue
            
            table_rows.append(cells)
            in_table = True
            continue
        else:
            if in_table:
                flush_table()
        
        # Код
        if stripped.startswith('```'):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_list()
                in_code = True
            continue
        if in_code:
            code_lines.append(stripped)
            continue
        
        # Списки
        if stripped.startswith('- [') or stripped.startswith('- '):
            flush_code()
            # Чекбокс
            if '[ ]' in stripped:
                item = stripped.replace('- [ ]', '⬜').strip()
            elif '[x]' in stripped:
                item = stripped.replace('- [x]', '✅').strip()
            else:
                item = stripped[2:].strip()
            list_items.append(item)
            in_list = True
            continue
        else:
            if in_list:
                flush_list()
        
        # Пустые строки
        if not stripped:
            elements.append(Spacer(1, 4))
            continue
        
        # Обычный текст
        # Жирный
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', stripped)
        # Курсив
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        
        elements.append(Paragraph(text, styles['Normal2']))

    # Финализируем
    flush_code()
    flush_list()
    flush_table()

    doc.build(elements)
    print(f"✅ PDF сохранён: {pdf_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "report_arclinic_yandex_maps.md")
    pdf_file = os.path.join(base_dir, "report_arclinic_yandex_maps.pdf")
    md_to_pdf(md_file, pdf_file)
