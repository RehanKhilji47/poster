#!/usr/bin/env python3
"""Pre-delivery QA for a set of platform markdown files.

Usage:  python3 scripts/qa_check.py out/<slug>-*.md
Medium is the alignment baseline; it must be among the files.
"""
import re, sys, os

def base(u): return u.split('/')[-1].split('.')[0]

def sentences(text):
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    out = []
    for ln in text.split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('#') or re.match(r'^[-*\d"“]', ln):
            continue
        for s in re.split(r'(?<=[.!?])\s+', ln):
            if len(s.split()) >= 6:
                out.append(s.strip())
    return set(out)

def main(paths):
    files = {os.path.basename(p): open(p, encoding='utf-8').read() for p in paths}
    med = next((k for k in files if 'medium' in k), None)
    if not med:
        sys.exit("no medium file among inputs")
    canon = [base(u) for u in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', files[med])]

    problems = 0
    print("=== structure ===")
    for name, t in sorted(files.items()):
        lines = t.split('\n')
        seq = [base(u) for u in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', t)]
        checks = {
            'GLUED (no blank line before image)':
                sum(1 for i, l in enumerate(lines)
                    if l.startswith('![') and i > 0 and lines[i-1].strip() != ''),
            'nested image syntax': len(re.findall(r'!\[[^\]]*\]\(!\[', t)),
            'html tags':           len(re.findall(r'<[a-zA-Z/][^>]*>', t)),
            'markdown table rows': len(re.findall(r'^\|', t, re.M)),
            'stray ** after image':len(re.findall(r'!\[[^\]]*\]\([^)]+\)\*\*', t)),
            'triple asterisk':     len(re.findall(r'^\*\*\*', t, re.M)),
            'unbalanced bold':     t.count('**') % 2,
            'INSERT markers':      t.count('INSERT IMAGE'),
            'misaligned images':   0 if seq == canon else 1,
        }
        bad = {k: v for k, v in checks.items() if v}
        problems += len(bad)
        h = [len(re.findall(rf'^{"#"*n} ', t, re.M)) for n in (1, 2, 3)]
        print(f"  {name:46} imgs={len(seq):2} h={h} links="
              f"{len(re.findall(r'(?<!!)\[[^\]]*\]\(https?://', t)):2} "
              f"words={len(t.split()):5} {bad or 'clean'}")

    print("\n=== title uniqueness ===")
    titles = [re.match(r'^# (.+)$', t, re.M).group(1) for t in files.values()]
    dupes = {x for x in titles if titles.count(x) > 1}
    print(f"  {len(set(titles))}/{len(titles)} unique" + (f"  DUPES: {dupes}" if dupes else ""))
    problems += len(dupes)

    print("\n=== prose overlap (target < 20%) ===")
    S = {k: sentences(v) for k, v in files.items()}
    ks = sorted(S)
    worst = (0, None)
    for i in range(len(ks)):
        for j in range(i+1, len(ks)):
            a, b = ks[i], ks[j]
            pct = 100*len(S[a] & S[b])/max(1, min(len(S[a]), len(S[b])))
            if pct > worst[0]: worst = (pct, (a, b))
            if pct >= 20:
                print(f"  HIGH {a} vs {b}: {pct:.1f}%")
                problems += 1
    print(f"  worst pair: {worst[1]} = {worst[0]:.1f}%")

    print("\n" + ("PASS — ready to deliver" if problems == 0
                  else f"{problems} problem(s) — fix before delivering"))
    return 1 if problems else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
