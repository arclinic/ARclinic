#!/usr/bin/env python3
"""Конвертирует MD-отчёт в PDF с помощью WeasyPrint."""

from weasyprint import HTML
import markdown
import os

def md_to_pdf(md_path: str, pdf_path: str):
    """Конвертирует Markdown в PDF."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Конвертируем MD в HTML
    html_content = markdown.markdown(
        md_content,
        extensions=["extra", "tables", "sane_lists"],
    )

    # Оборачиваем в HTML с CSS
    full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 2cm 1.5cm;
}}
body {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #333;
}}
h1 {{
    font-size: 20pt;
    color: #1a1a2e;
    border-bottom: 3px solid #e94560;
    padding-bottom: 8px;
}}
h2 {{
    font-size: 16pt;
    color: #16213e;
    border-bottom: 2px solid #0f3460;
    padding-bottom: 5px;
    margin-top: 25px;
}}
h3 {{
    font-size: 13pt;
    color: #0f3460;
    margin-top: 18px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 10pt;
}}
th {{
    background-color: #0f3460;
    color: white;
    padding: 8px 10px;
    text-align: left;
}}
td {{
    padding: 6px 10px;
    border-bottom: 1px solid #ddd;
}}
tr:nth-child(even) {{
    background-color: #f8f9fa;
}}
ul, ol {{
    margin: 6px 0;
    padding-left: 20px;
}}
li {{
    margin: 3px 0;
}}
code {{
    background-color: #f0f0f0;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 10pt;
}}
blockquote {{
    border-left: 4px solid #e94560;
    padding-left: 12px;
    margin: 10px 0;
    color: #555;
}}
hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}}
strong {{
    color: #1a1a2e;
}}
</style>
</head>
<body>
{html_content}
</body>
</html>"""

    # Генерируем PDF
    HTML(string=full_html).write_pdf(pdf_path)
    print(f"✅ PDF сохранён: {pdf_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "report_arclinic_yandex_maps.md")
    pdf_file = os.path.join(base_dir, "report_arclinic_yandex_maps.pdf")
    md_to_pdf(md_file, pdf_file)
