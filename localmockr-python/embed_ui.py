"""
embed_ui.py
Reads ui.html and injects its content into localmockr.py,
producing localmockr_embedded.py which PyInstaller packages into the .exe.

Run before building:
    python embed_ui.py
"""

import os, re, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(SCRIPT_DIR, 'localmockr.py')
UI   = os.path.join(SCRIPT_DIR, 'ui.html')
OUT  = os.path.join(SCRIPT_DIR, 'localmockr_embedded.py')

def main():
    if not os.path.exists(UI):
        print("ERROR: ui.html not found")
        sys.exit(1)

    with open(UI, 'r', encoding='utf-8') as f:
        html = f.read()

    with open(SRC, 'r', encoding='utf-8') as f:
        source = f.read()

    safe_html = html.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
    placeholder = 'UI_HTML = None  # injected by embed_ui.py'
    replacement = f'UI_HTML = """{safe_html}"""'

    if placeholder not in source:
        # fallback - replace the None assignment
        source = source.replace('UI_HTML = None', replacement)
    else:
        source = source.replace(placeholder, replacement)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(source)

    print(f"  Embedded ui.html ({len(html):,} bytes) -> {OUT}")

if __name__ == '__main__':
    main()
