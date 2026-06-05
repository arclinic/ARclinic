#!/usr/bin/env python3
"""GEO-ANALISIS PDF dlya ARclinic na russkom"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Cyrillic fonts
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))

# Colors
RED = HexColor("#e10b13")
DARK = HexColor("#333333")
LIGHT = HexColor("#f5f5f5")
GRAY = HexColor("#666666")
GREEN = HexColor("#27ae60")
ORANGE = HexColor("#f39c12")
BLUE = HexColor("#2980b9")

output = r"C:\Users\Пользователь\Desktop\Ксения\GEO-ANALYSIS-ARCLINIC-2.pdf"

doc = SimpleDocTemplate(output, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
    title="GEO-анализ ARclinic", author="ARclinic")

styles = getSampleStyleSheet()

def S(name, parent='Normal', **kw):
    s = ParagraphStyle(name, parent=styles[parent], **kw)
    styles.add(s)
    return s

S('T', fontSize=28, leading=34, textColor=RED, alignment=TA_CENTER, spaceAfter=6, fontName='ArialBold')
S('Sub', fontSize=14, leading=18, textColor=GRAY, alignment=TA_CENTER, spaceAfter=20, fontName='Arial')
S('H1', fontSize=18, leading=22, textColor=DARK, spaceBefore=16, spaceAfter=10, fontName='ArialBold')
S('H2', fontSize=14, leading=18, textColor=DARK, spaceBefore=12, spaceAfter=8, fontName='ArialBold')
S('B', fontSize=10, leading=14, textColor=DARK, spaceAfter=6, fontName='Arial')
S('BL', fontSize=10, leading=14, textColor=DARK, leftIndent=16, spaceAfter=4, fontName='Arial')
S('SM', fontSize=9, leading=12, textColor=GRAY, fontName='Arial')
S('BIG', fontSize=48, leading=56, textColor=RED, alignment=TA_CENTER, fontName='ArialBold')

story = []

def tbl(data, widths, hdr_color=DARK):
    t = Table(data, colWidths=widths)
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), hdr_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
    ]
    t.setStyle(TableStyle(style))
    return t

def bold(text):
    return f"<b>{text}</b>"

def color(text, clr):
    return f"<font color='{clr}'>{text}</font>"

def col_bold(text, clr):
    return f"<font color='{clr}'><b>{text}</b></font>"

# ===== ОБЛОЖКА =====
story.append(Spacer(1, 3*cm))
story.append(Paragraph("GEO-АНАЛИЗ", styles['T']))
story.append(Paragraph("Видимость ARclinic в ИИ-поиске", styles['Sub']))
story.append(Spacer(1, 0.5*cm))
story.append(HRFlowable(width="60%", thickness=2, color=RED, spaceAfter=20))
story.append(Spacer(1, 1*cm))

# Блок скоринга
score = Table([
    [Paragraph(bold("ИТОГОВЫЙ СКОРИНГ"), styles['H2'])],
    [Paragraph(bold("43/100"), styles['BIG'])],
    [Paragraph("Дата: 1 июня 2026 (обновлено)", styles['SM'])],
], colWidths=[14*cm])
score.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
    ('BOX', (0, 0), (-1, -1), 1, RED),
    ('TOPPADDING', (0, 0), (-1, -1), 12),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
]))
story.append(score)
story.append(Spacer(1, 2*cm))

# Инфо
info = Table([
    [Paragraph(bold("URL:"), styles['SM']), Paragraph("https://arclinic.ru", styles['SM'])],
    [Paragraph(bold("Направление:"), styles['SM']), Paragraph("Антивозрастная медицина и косметология", styles['SM'])],
    [Paragraph(bold("Платформа:"), styles['SM']), Paragraph("1С-Битрикс 25.750.0", styles['SM'])],
    [Paragraph(bold("Инструмент:"), styles['SM']), Paragraph("Ручной аудит по 5 критериям GEO", styles['SM'])],
], colWidths=[4*cm, 10*cm])
info.setStyle(TableStyle([
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
    ('BOX', (0, 0), (-1, -1), 0.5, GRAY),
]))
story.append(info)
story.append(PageBreak())

# ===== СТРАНИЦА 2: ТАБЛИЦА СКОРОВ =====
story.append(Paragraph(bold("Итоговый скоринг"), styles['H1']))
story.append(Spacer(1, 0.5*cm))

story.append(tbl([
    [Paragraph(bold("Критерий"), styles['B']), Paragraph(bold("Вес"), styles['B']),
     Paragraph(bold("Оценка"), styles['B']), Paragraph(bold("Баллы"), styles['B'])],
    [Paragraph("1. Цитируемость", styles['B']), Paragraph("25%", styles['B']),
     Paragraph("4/10", styles['B']), Paragraph("10", styles['B'])],
    [Paragraph("2. Структурная читаемость", styles['B']), Paragraph("20%", styles['B']),
     Paragraph("3/10", styles['B']), Paragraph("6", styles['B'])],
    [Paragraph("3. Мультимедиа", styles['B']), Paragraph("15%", styles['B']),
     Paragraph("2/10", styles['B']), Paragraph("3", styles['B'])],
    [Paragraph("4. Authority и бренд-сигналы", styles['B']), Paragraph("20%", styles['B']),
     Paragraph("5/10", styles['B']), Paragraph("10", styles['B'])],
    [Paragraph("5. Техническая доступность", styles['B']), Paragraph("20%", styles['B']),
     Paragraph("7/10", styles['B']), Paragraph("14", styles['B'])],
    [Paragraph(bold("ИТОГО"), styles['B']), Paragraph(bold("100%"), styles['B']),
     Paragraph("", styles['B']), Paragraph(bold("43"), styles['B'])],
], [7*cm, 2.5*cm, 2.5*cm, 2.5*cm]))
story.append(Spacer(1, 1*cm))

story.append(Paragraph(bold("Статус изменений"), styles['H2']))
story.append(tbl([
    [Paragraph(bold("Действие"), styles['B']), Paragraph(bold("Статус"), styles['B'])],
    [Paragraph("Разблокировка AI-краулеров в robots.txt", styles['B']), Paragraph(col_bold("СДЕЛАНО", GREEN), styles['B'])],
    [Paragraph("Исправлен Sitemap URL (sitemap_index.xml)", styles['B']), Paragraph(col_bold("СДЕЛАНО", GREEN), styles['B'])],
    [Paragraph("Удалён Disallow: *utm*=", styles['B']), Paragraph(col_bold("СДЕЛАНО", GREEN), styles['B'])],
    [Paragraph("Создание /llms.txt", styles['B']), Paragraph(col_bold("В РАБОТЕ", ORANGE), styles['B'])],
    [Paragraph("Article/BlogPosting schema", styles['B']), Paragraph(col_bold("НЕ СДЕЛАНО", RED), styles['B'])],
    [Paragraph("Автор + дата в статьях", styles['B']), Paragraph(col_bold("НЕ СДЕЛАНО", RED), styles['B'])],
    [Paragraph("Страница в Wikipedia", styles['B']), Paragraph(col_bold("НЕ СДЕЛАНО", RED), styles['B'])],
    [Paragraph("Реструктуризация статей (H2, FAQ)", styles['B']), Paragraph(col_bold("НЕ СДЕЛАНО", RED), styles['B'])],
    [Paragraph("Видео на YouTube/Rutube", styles['B']), Paragraph(col_bold("НЕ СДЕЛАНО", RED), styles['B'])],
], [10*cm, 4.5*cm], hdr_color=DARK))
story.append(PageBreak())

# ===== СТРАНИЦА 3: AI-КРАУЛЕРЫ =====
story.append(Paragraph(bold("1. Доступность для AI-краулеров"), styles['H1']))
story.append(tbl([
    [Paragraph(bold("Краулер"), styles['B']), Paragraph(bold("Владелец"), styles['B']),
     Paragraph(bold("Статус"), styles['B'])],
    [Paragraph("GPTBot", styles['B']), Paragraph("OpenAI", styles['B']),
     Paragraph(col_bold("Allow: /", GREEN), styles['B'])],
    [Paragraph("OAI-SearchBot", styles['B']), Paragraph("OpenAI", styles['B']),
     Paragraph(col_bold("Allow: /", GREEN), styles['B'])],
    [Paragraph("ClaudeBot", styles['B']), Paragraph("Anthropic", styles['B']),
     Paragraph(col_bold("Allow: /", GREEN), styles['B'])],
    [Paragraph("PerplexityBot", styles['B']), Paragraph("Perplexity", styles['B']),
     Paragraph(col_bold("Allow: /", GREEN), styles['B'])],
    [Paragraph("CCBot", styles['B']), Paragraph("Common Crawl", styles['B']),
     Paragraph("Default (*)", styles['B'])],
    [Paragraph("Bytespider", styles['B']), Paragraph("ByteDance", styles['B']),
     Paragraph("Default (*)", styles['B'])],
], [5*cm, 4*cm, 5.5*cm]))
story.append(Spacer(1, 1*cm))

story.append(Paragraph(bold("2. Анализ по платформам"), styles['H1']))
story.append(Paragraph(bold("Google AI Overviews") + " — прогноз: НИЗКИЙ (20%)", styles['B']))
story.append(Paragraph("92% цитат AIO — из топ-10 страниц. Нужен хороший SEO + цитируемый контент. Слабые места: нет структуры H2, нет FAQ, нет дат/авторов.", styles['BL']))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(bold("ChatGPT Web Search") + " — прогноз: НИЗКИЙ (15%)", styles['B']))
story.append(Paragraph("ChatGPT чаще цитирует Wikipedia (48%), Reddit (11%). У ARclinic нет страницы в Wikipedia.", styles['BL']))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(bold("Perplexity") + " — прогноз: НИЗКИЙ (15%)", styles['B']))
story.append(Paragraph("Perplexity опирается на Reddit (47%) и Wikipedia. Без присутствия на этих платформах — не будет цитироваться.", styles['BL']))
story.append(PageBreak())

# ===== СТРАНИЦА 4: ЦИТИРУЕМОСТЬ =====
story.append(Paragraph(bold("3. Цитируемость (Citability)"), styles['H1']))
story.append(Paragraph(bold("Балл: 10/25"), styles['H2']))
story.append(Paragraph("На сайте нет контента, оптимизированного для цитирования ИИ.", styles['B']))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(bold("Выявленные проблемы:"), styles['B']))
for p in [
    "Нет чётких, цитируемых предложений с фактами",
    "Нет самодостаточных ответ-блоков (134-167 слов)",
    "Нет определений в формате «X — это...»",
    "Нет уникальных данных (исследований, статистики)",
    "Meta-description общая для всей клиники",
]:
    story.append(Paragraph(f"  •  {p}", styles['BL']))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph(bold("Структурная читаемость: 6/20"), styles['H2']))
for p in [
    "Плоская структура заголовков: H1 -> H3, нет H2",
    "Нет FAQ-секций ни на одной странице",
    "Нет таблиц для сравнения процедур",
    "Длинные абзацы без рубрикации",
    "Нет вопросных H2 («Что такое...?», «Почему...?»)",
]:
    story.append(Paragraph(f"  •  {p}", styles['BL']))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph(bold("Мультимедиа: 3/15"), styles['H2']))
for p in [
    "Изображения без alt-текстов и подписей",
    "Нет видео на страницах услуг",
    "Нет инфографик",
    "Нет интерактивных элементов (калькуляторы, тесты)",
]:
    story.append(Paragraph(f"  •  {p}", styles['BL']))
story.append(PageBreak())

# ===== СТРАНИЦА 5: AUTHORITY =====
story.append(Paragraph(bold("4. Authority и бренд-сигналы"), styles['H1']))
story.append(Paragraph(bold("Балл: 10/20"), styles['H2']))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(bold("Положительные сигналы:"), styles['B']))
for p in [
    "Личный бренд (Анна Резник) — к.м.н., геронтолог, Telegram @av_reznik",
    "Отзывы на агрегаторах: ПроДокторов, Google Maps, Яндекс",
    "На ПроДокторов: 71 отзыв, 14 специалистов",
    "На НаПоправку: 160 отзывов, 13 специалистов",
    "MedicalBusiness schema на всех страницах",
    "SSR (серверный рендеринг) — Битрикс PHP",
]:
    story.append(Paragraph(f"  +  {p}", styles['BL']))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph(bold("Отрицательные сигналы:"), styles['B']))
for p in [
    "Нет автора в статьях (анонимный контент)",
    "Нет дат публикации/обновления",
    "Нет ссылок на исследования/источники",
    "Нет страницы в Wikipedia",
    "Нет канала YouTube/Rutube",
    "Нет присутствия на Reddit",
    "Article/BlogPosting schema отсутствует",
    "Person schema для врачей отсутствует",
]:
    story.append(Paragraph(f"  −  {p}", styles['BL']))
story.append(PageBreak())

# ===== СТРАНИЦА 6: ПЛАН =====
story.append(Paragraph(bold("5. План действий"), styles['H1']))

story.append(Paragraph(bold("Быстрые изменения (highest impact):"), styles['H2']))
story.append(tbl([
    [Paragraph(bold("#"), styles['B']), Paragraph(bold("Действие"), styles['B']),
     Paragraph(bold("Сложность"), styles['B']), Paragraph(bold("Статус"), styles['B'])],
    [Paragraph("1", styles['B']), Paragraph("Разблокировать AI-краулеров в robots.txt", styles['B']),
     Paragraph("5 мин", styles['B']), Paragraph(col_bold("СДЕЛАНО", GREEN), styles['B'])],
    [Paragraph("2", styles['B']), Paragraph("Исправить Sitemap URL", styles['B']),
     Paragraph("2 мин", styles['B']), Paragraph(col_bold("СДЕЛАНО", GREEN), styles['B'])],
    [Paragraph("3", styles['B']), Paragraph("Убрать Disallow: *utm*=", styles['B']),
     Paragraph("1 мин", styles['B']), Paragraph(col_bold("СДЕЛАНО", GREEN), styles['B'])],
    [Paragraph("4", styles['B']), Paragraph("Article/BlogPosting schema в блоге", styles['B']),
     Paragraph("30 мин", styles['B']), Paragraph(col_bold("НЕ СДЕЛАНО", RED), styles['B'])],
    [Paragraph("5", styles['B']), Paragraph("Автор и дата в статьях блога", styles['B']),
     Paragraph("30 мин", styles['B']), Paragraph(col_bold("НЕ СДЕЛАНО", RED), styles['B'])],
], [1.2*cm, 7*cm, 3*cm, 3.3*cm]))
story.append(Spacer(1, 1*cm))

story.append(Paragraph(bold("Среднесрочные изменения:"), styles['H2']))
story.append(tbl([
    [Paragraph(bold("#"), styles['B']), Paragraph(bold("Действие"), styles['B']),
     Paragraph(bold("Сложность"), styles['B'])],
    [Paragraph("6", styles['B']), Paragraph("Создать страницу в Wikipedia", styles['B']),
     Paragraph("2-4 нед", styles['B'])],
    [Paragraph("7", styles['B']), Paragraph("Реструктуризировать статьи (H2, FAQ, таблицы)", styles['B']),
     Paragraph("2-3 дня", styles['B'])],
    [Paragraph("8", styles['B']), Paragraph("Создать /llms.txt", styles['B']),
     Paragraph("30 мин", styles['B'])],
    [Paragraph("9", styles['B']), Paragraph("Добавить конкретные цифры и статистику", styles['B']),
     Paragraph("1-2 дня", styles['B'])],
    [Paragraph("10", styles['B']), Paragraph("Видео на YouTube/Rutube с брендом", styles['B']),
     Paragraph("1 день", styles['B'])],
], [1.2*cm, 9.5*cm, 3.8*cm], hdr_color=BLUE))
story.append(PageBreak())

# ===== СТРАНИЦА 7: ВЫВОД =====
story.append(Paragraph(bold("Вывод"), styles['H1']))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    "ARclinic <b>частично виден для ИИ-поиска</b> в текущем состоянии. "
    "Три критических изменения в robots.txt применены 01.06.2026 — "
    "AI-краулеры теперь могут сканировать сайт.",
    styles['B']))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph(bold("Осталось сделать (приоритет):"), styles['B']))
for i, item in enumerate([
    "Создать /llms.txt (нужен доступ к серверу или URL rewrite)",
    "Добавить Article/BlogPosting schema",
    "Добавить автора и даты в статьи блога",
    "Создать страницу в Wikipedia (2-4 недели)",
    "Реструктуризировать статьи: добавить H2, FAQ, таблицы",
    "Загрузить видео на YouTube/Rutube",
], 1):
    story.append(Paragraph(f"  {i}.  {item}", styles['BL']))

story.append(Spacer(1, 1.5*cm))
final = Table([
    [Paragraph(
        bold("СЛЕДУЮЩИЙ ШАГ:") + " Первые 3 изменения в robots.txt применены. "
        "Остальное — контент-план на июнь-июль 2026. Самый большой вклад — "
        "реструктуризация статей (H2, FAQ, таблицы) и создание Wikipedia-страницы.",
        styles['B'])],
], colWidths=[14*cm])
final.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), HexColor("#fff9c4")),
    ('BOX', (0, 0), (-1, -1), 1, ORANGE),
    ('TOPPADDING', (0, 0), (-1, -1), 12),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ('LEFTPADDING', (0, 0), (-1, -1), 12),
]))
story.append(final)

story.append(Spacer(1, 2*cm))
story.append(HRFlowable(width="100%", thickness=1, color=GRAY, spaceAfter=10))
story.append(Paragraph(
    "Документ создан AI-ассистентом для ARclinic. Дата: 01.06.2026",
    styles['SM']))

doc.build(story)
print(f"PDF создан: {output}")
