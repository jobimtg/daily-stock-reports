from pathlib import Path

ROOT = Path('.')
ROOT_URL = '/daily-stock-reports/index.html'

TARGETS = [
    Path('canada/morning'),
    Path('taiwan/morning'),
    Path('taiwan/closing'),
]

changed = []
for folder in TARGETS:
    if not folder.exists():
        continue
    for html in folder.glob('*.html'):
        text = html.read_text(encoding='utf-8')
        new = text
        new = new.replace('href="../index.html" class="back-link"', f'href="{ROOT_URL}" class="back-link"')
        new = new.replace('href="../../index.html" class="back-link"', f'href="{ROOT_URL}" class="back-link"')
        new = new.replace('href="../../../index.html" class="back-link"', f'href="{ROOT_URL}" class="back-link"')
        new = new.replace('href="index.html" class="back-link"', f'href="{ROOT_URL}" class="back-link"')
        if new != text:
            html.write_text(new, encoding='utf-8')
            changed.append(str(html))

if changed:
    print('Fixed back links:')
    for p in changed:
        print(' -', p)
else:
    print('No back links needed changes.')
