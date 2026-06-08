#!/usr/bin/env python3
"""Конвертирует MD-отчёт в PDF с помощью fpdf2 (с поддержкой кириллицы)."""

import os
import re
from fpdf import FPDF


EMOJI_MAP = {
    '⭐': '[звезда]', '🌟': '[звезда]',
    '🏆': '[трофей]',
    '✅': '[да]', '✔️': '[да]',
    '❌': '[нет]', '✖️': '[нет]',
    '📊': '[график]', '📈': '[рост]', '📉': '[падение]',
    '📋': '[список]', '📝': '[заметки]',
    '📅': '[дата]', '📆': '[календарь]',
    '📌': '[маркер]', '📍': '[метка]',
    '🔴': '[красный]', '🟡': '[желтый]', '🟢': '[зеленый]',
    '🎯': '[цель]', '💡': '[идея]',
    '💰': '[деньги]', '💎': '[алмаз]',
    '🔍': '[поиск]', '🔎': '[поиск]',
    '⚡': '[молния]', '🔥': '[огонь]',
    '👎': '[плохо]', '👍': '[хорошо]',
    '❗': '[!]', '❓': '[?]', '❕': '[!]', '❔': '[?]',
    '➡️': '->', '⬅️': '<-',
    '▶️': '[>]', '⏩': '[>>]',
    '🔹': '*', '🔸': '*', '▪️': '*', '▫️': '*',
    '🔗': '[ссылка]', '🌐': '[сайт]',
    '📞': '[телефон]', '📱': '[мобильный]',
    '✏️': '[карандаш]', '🖊️': '[ручка]',
    '🗑️': '[удалить]', '🔄': '[обновить]',
    '🛠️': '[инструменты]', '⚙️': '[настройки]',
    '🚀': '[ракета]', '🎯': '[цель]',
    '📄': '[документ]', '📃': '[документ]',
    '🔑': '[ключ]', '🛡️': '[щит]',
    '🤖': '[робот]', '🧠': '[мозг]',
    '👁️': '[глаз]', '👀': '[глаза]',
    '📸': '[фото]', '📷': '[камера]',
    '🏅': '[медаль]', '🥇': '[золото]', '🥈': '[серебро]', '🥉': '[бронза]',
    '🎉': '[ура]', '🎊': '[праздник]',
    '🔔': '[колокольчик]', '🔕': '[колокольчик]',
    '📣': '[мегафон]', '📢': '[громкоговоритель]',
    '💬': '[чат]', '🗨️': '[диалог]',
    '🌍': '[мир]', '🌏': '[мир]', '🌎': '[мир]',
    '☀️': '[солнце]', '🌙': '[луна]',
    '⭐': '[звезда]', '✨': '[звезды]',
    '💪': '[сила]', '🏃': '[бег]',
    '🧹': '[чистка]', '🧽': '[уборка]',
    '🎨': '[дизайн]', '🖌️': '[кисть]',
    '📚': '[книги]', '📖': '[книга]',
    '🎬': '[видео]', '🎥': '[камера]',
    '🎵': '[музыка]', '🎶': '[ноты]',
    '🔝': '[топ]', '⬆️': '[вверх]', '⬇️': '[вниз]',
    'ℹ️': '[инфо]', '©️': '(c)', '®️': '(R)',
    '™️': '(TM)', '✅': '[галочка]',
    '➖': '-', '➕': '+',
    '✳️': '*', '❇️': '*',
    '〰️': '~', '➰': '~',
    '🔰': '[новичок]', '♻️': '[переработка]',
    '✅': '[готово]',
}

def replace_emoji(text):
    """Заменяет эмодзи на текстовые аналоги."""
    for emoji, replacement in EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    return text


class PDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        # Добавляем шрифт DejaVu с поддержкой кириллицы
        self.add_font('DejaVu', '', os.path.join(os.path.dirname(__file__), '..', 'fonts', 'DejaVuSans.ttf'), uni=True)
        self.add_font('DejaVu', 'B', os.path.join(os.path.dirname(__file__), '..', 'fonts', 'DejaVuSans-Bold.ttf'), uni=True)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font('DejaVu', '', 7)
            self.set_text_color(150, 150, 150)
            self.cell(0, 5, 'ARclinic — Отчёт по Яндекс Картам', align='C')
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'— {self.page_no()} —', align='C')


def md_to_pdf(md_path: str, pdf_path: str):
    """Конвертирует Markdown в PDF."""
    
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pdf = PDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    # Титульная страница
    pdf.set_font('DejaVu', 'B', 24)
    pdf.set_text_color(26, 26, 46)
    pdf.ln(40)
    pdf.cell(0, 15, 'ARclinic', align='C')
    pdf.ln(12)
    pdf.set_font('DejaVu', '', 14)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 10, 'Отчёт по Яндекс Картам', align='C')
    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Анализ карточки организации и рекомендации', align='C')
    pdf.ln(6)
    pdf.cell(0, 8, 'Дата: 8 июня 2026', align='C')
    pdf.ln(20)

    # Разделитель
    pdf.set_draw_color(233, 69, 96)
    pdf.set_line_width(0.5)
    y = pdf.get_y()
    pdf.line(15, y, 195, y)
    pdf.ln(10)

    # Основное содержание
    in_code = False
    in_table = False
    table_data = []
    in_list = False

    def write_table():
        nonlocal in_table, table_data
        if not table_data or len(table_data) < 2:
            table_data = []
            in_table = False
            return
        
        # Определяем кол-во колонок
        ncols = max(len(r) for r in table_data)
        col_width = 180 / ncols
        
        # Заголовок
        pdf.set_fill_color(15, 52, 96)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('DejaVu', 'B', 8)
        for i, cell in enumerate(table_data[0]):
            pdf.cell(col_width, 7, cell, border=1, fill=True, align='C')
        pdf.ln()
        
        # Данные
        pdf.set_text_color(51, 51, 51)
        for row in table_data[1:]:
            # Определяем высоту строки
            max_lines = 1
            for i, cell in enumerate(row):
                # Примерная оценка: ширина символа ~4мм
                chars_per_line = max(1, int(col_width / 3.5))
                lines_count = max(1, -(-len(cell) // chars_per_line))  # ceil division
                max_lines = max(max_lines, lines_count)
            
            h = max(6, max_lines * 5)
            
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
            # Проверка на разрыв страницы
            if y_start + h > 270:
                pdf.add_page()
                y_start = pdf.get_y()
            
            for i, cell in enumerate(row):
                x = x_start + i * col_width
                pdf.set_xy(x, y_start)
                pdf.set_font('DejaVu', '', 7)
                
                # Рисуем фон для чётных строк
                if table_data.index(row) % 2 == 0:
                    pdf.set_fill_color(248, 249, 250)
                    pdf.rect(x, y_start, col_width, h, 'F')
                
                # Пишем текст с переносом
                pdf.set_xy(x + 1, y_start + 1)
                pdf.multi_cell(col_width - 2, 4.5, cell, border=0)
            
            # Рисуем границы
            for i in range(ncols + 1):
                x = x_start + i * col_width
                pdf.line(x, y_start, x, y_start + h)
            pdf.line(x_start, y_start, x_start + ncols * col_width, y_start)
            pdf.line(x_start, y_start + h, x_start + ncols * col_width, y_start + h)
            
            pdf.set_xy(x_start, y_start + h)
        
        pdf.ln(4)
        table_data = []
        in_table = False

    for line in lines:
        stripped = replace_emoji(line.rstrip())
        
        # Разделители
        if re.match(r'^---+$', stripped):
            if in_table: write_table()
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.3)
            y = pdf.get_y()
            pdf.line(15, y, 195, y)
            pdf.ln(4)
            continue
        
        # Заголовок H1
        if stripped.startswith('# ') and not stripped.startswith('# '):
            if in_table: write_table()
            pdf.set_font('DejaVu', 'B', 16)
            pdf.set_text_color(26, 26, 46)
            # Красная линия под заголовком
            pdf.cell(0, 10, stripped[2:])
            pdf.ln(10)
            pdf.set_draw_color(233, 69, 96)
            pdf.set_line_width(0.8)
            y = pdf.get_y()
            pdf.line(15, y, 100, y)
            pdf.ln(6)
            continue
        
        if stripped.startswith('# '):
            if in_table: write_table()
            pdf.set_font('DejaVu', 'B', 16)
            pdf.set_text_color(26, 26, 46)
            pdf.cell(0, 10, stripped[2:])
            pdf.ln(10)
            pdf.set_draw_color(233, 69, 96)
            pdf.set_line_width(0.8)
            y = pdf.get_y()
            pdf.line(15, y, 100, y)
            pdf.ln(6)
            continue
        
        # Заголовок H2
        if stripped.startswith('## '):
            if in_table: write_table()
            pdf.set_font('DejaVu', 'B', 13)
            pdf.set_text_color(22, 33, 62)
            pdf.cell(0, 8, stripped[3:])
            pdf.ln(10)
            pdf.set_draw_color(15, 52, 96)
            pdf.set_line_width(0.5)
            y = pdf.get_y()
            pdf.line(15, y, 80, y)
            pdf.ln(4)
            continue
        
        # Заголовок H3
        if stripped.startswith('### '):
            if in_table: write_table()
            pdf.set_font('DejaVu', 'B', 11)
            pdf.set_text_color(15, 52, 96)
            pdf.cell(0, 7, stripped[4:])
            pdf.ln(9)
            continue
        
        # Таблицы
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if re.match(r'^[\s|:\-]+$', stripped):
                continue
            table_data.append(cells)
            in_table = True
            continue
        else:
            if in_table:
                write_table()
        
        # Код
        if stripped.startswith('```'):
            if in_code:
                in_code = False
                pdf.ln(2)
            else:
                in_code = True
                pdf.set_fill_color(240, 240, 240)
                pdf.set_text_color(51, 51, 51)
            continue
        
        if in_code:
            pdf.set_font('Courier', '', 7)
            pdf.set_x(20)
            pdf.cell(0, 4, stripped)
            pdf.ln()
            continue
        
        # Списки
        if stripped.startswith('- [') or stripped.startswith('- '):
            if in_table: write_table()
            pdf.set_font('DejaVu', '', 9)
            pdf.set_text_color(51, 51, 51)
            
            if '[ ]' in stripped:
                item = stripped.replace('- [ ]', '☐').strip()
            elif '[x]' in stripped:
                item = stripped.replace('- [x]', '☑').strip()
            else:
                item = stripped[2:].strip()
            
            # Жирный текст в списке
            item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
            
            pdf.set_x(20)
            pdf.cell(5, 5, '•')
            pdf.multi_cell(0, 5, item)
            pdf.ln(1)
            continue
        
        # Пустые строки
        if not stripped:
            if in_table: write_table()
            pdf.ln(3)
            continue
        
        # Обычный текст
        if in_table: write_table()
        pdf.set_font('DejaVu', '', 9)
        pdf.set_text_color(51, 51, 51)
        
        # Обработка жирного текста
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        
        pdf.set_x(15)
        pdf.multi_cell(0, 5, text)
        pdf.ln(1)

    # Финализируем таблицу если осталась
    if in_table:
        write_table()

    pdf.output(pdf_path)
    print(f"✅ PDF сохранён: {pdf_path} ({os.path.getsize(pdf_path)} байт)")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "report_arclinic_yandex_maps.md")
    pdf_file = os.path.join(base_dir, "report_arclinic_yandex_maps.pdf")
    md_to_pdf(md_file, pdf_file)
