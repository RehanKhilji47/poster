#!/usr/bin/env python3
"""Match docx-embedded images to WhatsApp uploads by colour signature.

Usage: python3 scripts/match_images.py <docx_media_dir> <uploads_dir>

Uses globally optimal assignment, not greedy — near-identical variants
(same character, different hair colour) break greedy matching.
"""
import sys, os, glob, re
import numpy as np
from PIL import Image
from scipy.optimize import linear_sum_assignment

def sig(path, w=160, h=112):
    a = np.asarray(Image.open(path).convert('RGB').resize((w, h), Image.LANCZOS),
                   dtype=np.float32)
    return ((a - a.mean(axis=(0, 1))) / (a.std(axis=(0, 1)) + 1e-6)).ravel()

def main(dxdir, updir):
    key = lambda x: int(re.search(r'(\d+)\.', os.path.basename(x)).group(1))
    dx = sorted(glob.glob(os.path.join(dxdir, '*')), key=key)
    up = sorted(glob.glob(os.path.join(updir, '*')))
    D = np.stack([sig(f) for f in dx]); U = np.stack([sig(f) for f in up])
    C = np.abs(D[:, None, :] - U[None, :, :]).mean(axis=2)
    r, c = linear_sum_assignment(C)
    greedy = [int(np.argmin(C[i])) for i in range(len(dx))]
    for i, j in zip(r, c):
        second = np.partition(C[i], 1)[1]
        flag = '' if greedy[i] == j else '  <-- greedy disagreed, inspect'
        conf = 'MATCH' if C[i, j] < 0.05 else 'NO UPLOAD?'
        print(f"{os.path.basename(dx[i]):14} -> {os.path.basename(up[j]):48} "
              f"cost={C[i,j]:.4f} 2nd={second:.4f} {conf}{flag}")
    print(f"\nbijection: {len(set(c)) == len(c)}   docx={len(dx)} uploads={len(up)}")

if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
