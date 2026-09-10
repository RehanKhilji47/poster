#!/usr/bin/env python3
"""Recover images pasted into a Claude Code chat, straight out of the session transcript.

Usage: python3 scripts/pull_pasted_images.py <out_dir> [session.jsonl]

With no transcript given, uses the most recently modified one for this project.
Only user-authored image blocks are pulled, so tool screenshots and PDF page
renders from the assistant side are ignored. Files are written as
pasted-NN-<width>x<height>.<ext> in paste order.
"""
import json, base64, io, os, sys, glob
from PIL import Image

PROJ = os.path.expanduser('~/.claude/projects')

def newest_transcript():
    c = sorted(glob.glob(f'{PROJ}/*/*.jsonl'), key=os.path.getmtime, reverse=True)
    if not c: sys.exit('no session transcripts found')
    return c[0]

def pull(transcript, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    found, n = [], 0
    for line in open(transcript, encoding='utf-8'):
        try: rec = json.loads(line)
        except Exception: continue
        msg = rec.get('message') or {}
        if (msg.get('role') or rec.get('type')) != 'user': continue
        content = msg.get('content')
        if not isinstance(content, list): continue
        for b in content:
            if not (isinstance(b, dict) and b.get('type') == 'image'): continue
            src = b.get('source') or {}
            if src.get('type') != 'base64': continue
            raw = base64.b64decode(src['data'])
            im = Image.open(io.BytesIO(raw))
            ext = {'image/jpeg': 'jpg', 'image/png': 'png'}.get(src['media_type'], 'bin')
            n += 1
            p = os.path.join(out_dir, f'pasted-{n:02d}-{im.width}x{im.height}.{ext}')
            open(p, 'wb').write(raw)
            found.append((p, im.size, len(raw)))
    return found

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    t = sys.argv[2] if len(sys.argv) > 2 else newest_transcript()
    print(f'transcript: {t}')
    for p, size, n in pull(t, sys.argv[1]):
        print(f'  {os.path.basename(p):34} {str(size):12} {n//1024:5}KB')
