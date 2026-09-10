#!/usr/bin/env python3
"""Pre-delivery QA for a set of platform markdown files.

Usage:  python3 scripts/qa_check.py out/<slug>-*.md [--links sources/<slug>/links.json]

Medium is the alignment baseline; it must be among the files.

--links enables link integrity: every URL in the manifest must appear in EVERY
platform file, byte-identical (query string and all), carrying non-empty
descriptive anchor text. Outbound URLs not in the manifest are flagged too, so a
rewrite cannot invent or drop a destination. Affiliate and UTM-tagged links are
revenue-critical: a silently stripped ?utm_ or a "smartened" apostrophe in the
anchor is a real loss, so this check is exact, not fuzzy.
"""
import re, sys, os, json, unicodedata

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

LINK_RE = re.compile(r'(?<!!)\[([^\]]*)\]\((https?://[^)\s]+)\)')

def check_links(files, manifest_path):
    """Every manifest URL present in every file, byte-identical, properly anchored."""
    man = json.load(open(manifest_path, encoding='utf-8'))
    want = {m['url'] for m in man}
    canon_anchor = {m['url']: m['anchor'] for m in man}
    problems = 0
    print(f"\n=== link integrity ({len(want)} manifest URLs x {len(files)} files) ===")
    for name, t in sorted(files.items()):
        found = LINK_RE.findall(t)
        seen = {u for _, u in found}
        missing = want - seen
        extra = seen - want
        bad_anchor = []
        for anchor, url in found:
            a = anchor.strip()
            if url in want and (not a or a.lower().startswith('http') or
                                a.lower() in ('here', 'click here', 'link', 'this')):
                bad_anchor.append((a, url))
        # a bare URL pasted as text is a link that lost its anchor
        stripped = t
        for _, u in found:
            stripped = stripped.replace(f']({u})', ']()')
        naked = [u for u in want if u in stripped]
        # near-miss: manifest URL present only with its query string altered
        truncated = []
        for u in missing:
            base = u.split('?')[0]
            if base in t:
                truncated.append(base)
        issues = []
        if missing:   issues.append(f"MISSING {len(missing)}")
        if extra:     issues.append(f"UNKNOWN-URL {len(extra)}")
        if bad_anchor:issues.append(f"BAD-ANCHOR {len(bad_anchor)}")
        if naked:     issues.append(f"BARE-URL {len(naked)}")
        if truncated: issues.append(f"QUERY-STRIPPED {len(truncated)}")
        problems += len(issues)
        print(f"  {name:46} links={len(found):2} {', '.join(issues) or 'all 8 intact'}")
        for u in sorted(missing):    print(f"      MISSING:        {u}")
        for u in sorted(extra):      print(f"      NOT IN MANIFEST:{u}")
        for b in sorted(truncated):  print(f"      QUERY STRIPPED: {b}")
        for u in sorted(naked):      print(f"      BARE URL:       {u}")
        for a, u in bad_anchor:      print(f"      WEAK ANCHOR:    {a!r} -> {u}")
    # anchor drift across files is allowed (prose is rewritten) but reported
    print("  anchor text per URL:")
    for m in man:
        anchors = set()
        for t in files.values():
            for a, u in LINK_RE.findall(t):
                if u == m['url']: anchors.add(a.strip())
        src = canon_anchor[m['url']]
        mark = 'source' if anchors == {src} else 'rewritten'
        print(f"    {mark:9} {src[:38]:38} -> {sorted(anchors)}")
    return problems

def main(paths):
    manifest = None
    if '--links' in paths:
        i = paths.index('--links'); manifest = paths[i+1]; paths = paths[:i] + paths[i+2:]
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

    if manifest:
        problems += check_links(files, manifest)

    print("\n" + ("PASS — ready to deliver" if problems == 0
                  else f"{problems} problem(s) — fix before delivering"))
    return 1 if problems else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
