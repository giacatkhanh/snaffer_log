#!/usr/bin/env python3
import sys, re, textwrap, hashlib
from collections import OrderedDict

COLORS = {'Red': '\033[1;31m', 'Yellow': '\033[1;33m',
          'Green': '\033[1;32m', 'Black': '\033[1;90m'}
RESET, BOLD, DIM = '\033[0m', '\033[1m', '\033[2m'

pattern = re.compile(
    r'^\[(?P<ctx>[^\]]+)\]\s+(?P<ts>\S+\s+\S+)\s+\[(?P<type>\w+)\]\s+'
    r'\{(?P<color>\w+)\}<(?P<meta>.*?)>\((?P<path>[^)]*)\)\s?(?P<content>.*)$'
)

logfile = sys.argv[1]
wanted = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None

def unescape(s):
    s = s.replace('\\r\\n', '\n').replace('\\n', '\n')
    return re.sub(r'\\(.)', r'\1', s)

entries = OrderedDict()  # key = (rule, content_hash)

with open(logfile, encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.rstrip('\n')
        m = pattern.match(line)
        if not m:
            continue
        color = m.group('color')
        if wanted and color not in wanted:
            continue
        meta = m.group('meta').split('|')
        rule = meta[0] if meta else ''
        size = meta[-2] if len(meta) >= 2 else ''
        date = meta[-1] if len(meta) >= 1 else ''
        path = m.group('path')
        content = unescape(m.group('content'))

        norm = re.sub(r'\s+', ' ', content).strip()
        chash = hashlib.md5(norm.encode('utf-8', 'ignore')).hexdigest()
        key = (rule, chash)

        if key not in entries:
            entries[key] = {'color': color, 'rule': rule, 'size': size,
                             'date': date, 'content': content, 'paths': [path]}
        else:
            entries[key]['paths'].append(path)

for e in entries.values():
    c = COLORS.get(e['color'], '')
    extra = e['paths'][1:]
    print(f"{c}{BOLD}[{e['color']}] {e['rule']}{RESET}  {DIM}{e['size']} {e['date']}{RESET}")
    print(f"{DIM}{e['paths'][0]}{RESET}")
    if extra:
        preview = ', '.join(extra[:3])
        more = f" (+{len(extra)-3} nữa)" if len(extra) > 3 else ""
        print(f"{DIM}    ↳ +{len(extra)} file khác cùng nội dung: {preview}{more}{RESET}")
    for para in e['content'].split('\n'):
        para = para.strip()
        if not para:
            continue
        for wrapped in (textwrap.wrap(para, width=100) or ['']):
            print(f"    {wrapped}")
    print()
