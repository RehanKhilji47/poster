#!/usr/bin/env python3
"""Render a table to a PNG in the house style (dark header, zebra rows).

Usage: python3 scripts/table_png.py out.png tables.json <index>
       python3 scripts/table_png.py out.png -            (reads JSON rows on stdin)

Rows are a list of lists; the first row is the header. Matches the existing
published tables: #1F2937 header with white text, white / #F3F4F6 zebra body,
first column dark, remaining columns grey. Width defaults to 1248px.
"""
import sys, json
from PIL import Image, ImageDraw, ImageFont

HEADER_BG=(31,41,55); HEADER_FG=(255,255,255)
ROW_A=(255,255,255); ROW_B=(243,244,246)
COL0_FG=(17,24,39); COLN_FG=(75,85,99); RULE=(209,213,219)
FONT="/System/Library/Fonts/Avenir Next.ttc"
IDX_REGULAR=7; IDX_DEMIBOLD=2   # face indices inside the .ttc, verified with getname()

def load(sz, bold=False):
    try: return ImageFont.truetype(FONT, sz, index=IDX_DEMIBOLD if bold else IDX_REGULAR)
    except Exception: return ImageFont.load_default()

def wrap(draw, text, font, maxw):
    out=[]
    for para in text.split('\n'):
        line=''
        for word in para.split():
            t=(line+' '+word).strip()
            if draw.textlength(t, font=font) <= maxw: line=t
            else:
                if line: out.append(line)
                line=word
        out.append(line)
    return out or ['']

def render(rows, out, width=1248, pad=22, fs=25, lead=9):
    ncol=max(len(r) for r in rows)
    rows=[r+['']*(ncol-len(r)) for r in rows]
    scratch=ImageDraw.Draw(Image.new('RGB',(10,10)))
    reg, bold = load(fs), load(fs, True)
    # column widths from the longest single word plus content mass
    mass=[max(scratch.textlength(r[c], font=reg) for r in rows) for c in range(ncol)]
    # no column may be narrower than its longest single word, or text overflows
    floor=[max([scratch.textlength(word, font=reg)
                for r in rows for word in (r[c].split() or [''])] + [1]) + 6
           for c in range(ncol)]
    total=sum(mass); avail=width-pad*2-pad*(ncol-1)
    if ncol==2: floor[0]=max(floor[0], avail*0.26)   # keep the label column from over-wrapping
    w=[max(int(f), int(avail*m/total)) for f,m in zip(floor,mass)]
    over=sum(w)-avail
    while over>0:
        big=w.index(max(w)); take=min(over, int(w[big]-floor[big]))
        if take<=0: break
        w[big]-=take; over-=take
    lines=[]; heights=[]
    for ri,r in enumerate(rows):
        f = bold if ri==0 else reg
        cells=[wrap(scratch, r[c], f, w[c]) for c in range(ncol)]
        lines.append(cells)
        heights.append(max(len(c) for c in cells)*(fs+lead)+pad*2-lead)
    H=sum(heights)
    img=Image.new('RGB',(width,H),ROW_A); d=ImageDraw.Draw(img)
    y=0
    for ri,cells in enumerate(lines):
        h=heights[ri]
        d.rectangle([0,y,width,y+h], fill=HEADER_BG if ri==0 else (ROW_A if ri%2 else ROW_B))
        if ri>1: d.line([(0,y),(width,y)], fill=RULE, width=1)
        x=pad
        for ci,cl in enumerate(cells):
            f = bold if ri==0 else reg
            fg = HEADER_FG if ri==0 else (COL0_FG if ci==0 else COLN_FG)
            ty=y+pad
            for ln in cl:
                d.text((x,ty), ln, font=f, fill=fg); ty+=fs+lead
            x+=w[ci]+pad
        y+=h
    img.save(out, optimize=True)
    return img.size

if __name__=='__main__':
    if len(sys.argv)<3: sys.exit(__doc__)
    out=sys.argv[1]
    src=sys.stdin.read() if sys.argv[2]=='-' else open(sys.argv[2]).read()
    data=json.loads(src)
    if len(sys.argv)>3: data=data[int(sys.argv[3])]
    print(render(data, out))
