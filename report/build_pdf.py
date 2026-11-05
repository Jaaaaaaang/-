"""build_pdf.py — part1~3.html + style.css → output/예선결과물_SCX_NEXT.pdf (WeasyPrint)"""
import os, sys
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
ROOT = os.path.dirname(os.path.abspath(__file__))
parts = ''.join(open(os.path.join(ROOT, f'part{i}.html'), encoding='utf-8').read() for i in (1, 2, 3))
font_css = CSS(string="""
@font-face { font-family: 'NanumGothic'; src: url('file:///usr/share/fonts/truetype/nanum/NanumGothic.ttf'); font-weight: normal; }
@font-face { font-family: 'NanumGothic'; src: url('file:///usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'); font-weight: bold; }
""")
html = f"<!DOCTYPE html><html lang='ko'><head><meta charset='utf-8'><title>SCX NEXT 예선결과물</title></head><body>{parts}</body></html>"
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'output', '예선결과물_SCX_NEXT.pdf')
fc = FontConfiguration()
doc = HTML(string=html, base_url=ROOT).render(stylesheets=[font_css, CSS(os.path.join(ROOT, 'style.css'), font_config=fc)], font_config=fc)
doc.write_pdf(out)
print(f'PDF saved: {out} | pages: {len(doc.pages)}')
