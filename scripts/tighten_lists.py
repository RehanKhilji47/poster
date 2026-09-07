#!/usr/bin/env python3
import re, sys
MARKER = re.compile(r'^(\s*)([-*+]|\d+[.)])(\s+)(.*)$')
def tighten(text):
    lines = text.split('\n'); out=[]
    for ln in lines:
        m = MARKER.match(ln)
        if m and len(m.group(3)) > 1:
            ln = f"{m.group(1)}{m.group(2)} {m.group(4)}"
        out.append(ln)
    res=[]; i=0
    while i < len(out):
        ln = out[i]
        if ln.strip() == '':
            prev = res[-1] if res else ''
            nxt = out[i+1] if i+1 < len(out) else ''
            if prev and MARKER.match(prev) and MARKER.match(nxt):
                i += 1; continue
        res.append(ln); i += 1
    return '\n'.join(res)
if __name__ == '__main__':
    for path in sys.argv[1:]:
        src = open(path, encoding='utf-8').read()
        new = tighten(src)
        if new != src:
            open(path,'w',encoding='utf-8').write(new); print(f"tightened: {path}")
        else: print(f"unchanged: {path}")
