#!/usr/bin/env python3
"""Join 2+ images side by side into one PNG (for before/after or triptych figures).

Usage: python3 scripts/composite.py out.png a.png b.png [c.png ...]
Resizes to the SMALLEST height so nothing is upscaled.
"""
import sys
from PIL import Image

def composite(out, paths, gap=24, bg=(255, 255, 255)):
    ims = [Image.open(p).convert('RGB') for p in paths]
    h = min(i.height for i in ims)
    ims = [i.resize((round(i.width*h/i.height), h), Image.LANCZOS) for i in ims]
    w = sum(i.width for i in ims) + gap*(len(ims)-1)
    canvas = Image.new('RGB', (w, h), bg)
    x = 0
    for i in ims:
        canvas.paste(i, (x, 0)); x += i.width + gap
    canvas.save(out, optimize=True)
    return canvas.size

if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    print(composite(sys.argv[1], sys.argv[2:]))
