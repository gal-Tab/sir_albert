#!/usr/bin/env python3
"""Pack a visual-explainer template folder into ONE self-contained .html file.

Why: Zero to Hero (and email, Drive, a zip) loads the page without its sibling files, so relative paths like
`assets/hero.png` or `engine.js` break. This inlines local scripts, the Motion library and every `assets/...` image
(as data: URIs) so the page works anywhere and offline.

Usage:
  pack-single-file.py <template-dir> <out.html> [--motion motion.js] [--jpeg-quality 88] [--keep-png]

- <template-dir> holds index.html, story.js, engine.js and assets/.
- Motion: the pinned CDN script tag in index.html is replaced by a local copy. Pass --motion <file> to use a copy you
  already have; otherwise the pinned version is fetched once from the same CDN URL the page already uses.
- Big PNGs (> 400 KB) are re-encoded as JPEG with macOS `sips` unless --keep-png (PNG with transparency needs it).
"""
import argparse, base64, mimetypes, os, re, shutil, subprocess, sys, tempfile, urllib.request
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('template_dir'); ap.add_argument('out')
ap.add_argument('--motion'); ap.add_argument('--jpeg-quality', type=int, default=88); ap.add_argument('--keep-png', action='store_true')
a = ap.parse_args()
root = Path(a.template_dir).resolve()
html = (root / 'index.html').read_text()

def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    data = path.read_bytes()
    if path.suffix.lower() == '.png' and len(data) > 400_000 and not a.keep_png and shutil.which('sips'):
        tmp = Path(tempfile.mkdtemp()) / (path.stem + '.jpg')
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', str(a.jpeg_quality), str(path), '--out', str(tmp)], check=True, capture_output=True)
        data, mime = tmp.read_bytes(), 'image/jpeg'
        print(f'  {path.name}: PNG -> JPEG q{a.jpeg_quality} ({len(data) // 1024} KB)')
    return f'data:{mime};base64,' + base64.b64encode(data).decode()

IMG = re.compile(r"""(['"])((?:\./)?assets/[^'"]+\.(?:png|jpe?g|webp|gif|svg))\1""")
def inline_images(text: str) -> str:
    def sub(m):
        p = root / m.group(2)
        if not p.exists(): sys.exit(f'missing image: {p}')
        return m.group(1) + data_uri(p) + m.group(1)
    return IMG.sub(sub, text)

def script(js: str) -> str:
    return '<script>' + re.sub(r'</script', r'<\\/script', inline_images(js), flags=re.I) + '</script>'

# 1. Motion
m = re.search(r'<script src="(https://cdn\.jsdelivr\.net/npm/motion@[^"]+)"></script>', html)
if m:
    if a.motion: js = Path(a.motion).read_text()
    else:
        print('fetching pinned Motion from', m.group(1))
        js = urllib.request.urlopen(m.group(1), timeout=30).read().decode()
    html = html.replace(m.group(0), '<script>' + re.sub(r'</script', r'<\\/script', js, flags=re.I) + '</script>')   # the library has no assets: keep it verbatim

# 2. local scripts (story.js, engine.js)
def local(m):
    p = root / m.group(1)
    if not p.exists(): sys.exit(f'missing script: {p}')
    return script(p.read_text())
html = re.sub(r'<script src="((?!https?:)[^"]+\.js)"></script>', local, html)

# 3. images written directly in the HTML
html = inline_images(html)

left = re.findall(r'(?:src|href)="(?:\./)?(?:assets/|[^"]*\.js")', html)
# any quoted image path that is not a data: or http(s) URL is still a relative reference (Motion's own code has none)
left += re.findall(r"""['"]((?!data:|https?:|//)[^'"\s]*\.(?:png|jpe?g|webp|gif|svg))['"]""", html)
if left: sys.exit(f'unresolved local references (the page would break outside this folder): {left}')
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
Path(a.out).write_text(html)
size = os.path.getsize(a.out)
print(f'wrote {a.out}  {size / 1e6:.2f} MB' + ('   (large: consider a smaller hero image)' if size > 8e6 else ''))
