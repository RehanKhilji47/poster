#!/usr/bin/env python3
"""Make the smaller web JPEGs that non-LinkedIn platforms hotlink.

Usage: python3 scripts/web_jpeg.py <out_web_dir> <img.png> [img.png ...]

Matches the existing published set: same pixel size as the PNG unless it is
wider than MAXW, then scaled to MAXW. Quality is stepped down until the file
lands under TARGET bytes, so pages stay light.
"""
import sys, os
from PIL import Image
MAXW = 1600
TARGET = 280 * 1024

def build(src, out_dir):
    im = Image.open(src).convert('RGB')
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    dst = os.path.join(out_dir, os.path.splitext(os.path.basename(src))[0] + '.jpg')
    for q in (88, 84, 80, 76, 72, 68, 64):
        im.save(dst, 'JPEG', quality=q, optimize=True, progressive=True)
        if os.path.getsize(dst) <= TARGET: break
    return dst, im.size, os.path.getsize(dst), q

if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for s in sys.argv[2:]:
        d, size, n, q = build(s, out)
        print(f'{os.path.basename(d):46} {str(size):13} {n//1024:5}KB  q={q}')
