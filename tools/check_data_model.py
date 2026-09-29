#!/usr/bin/env python3
"""Diagram check for data/data-model-MB360.md (section 5), run from the repository root:

    python3 tools/check_data_model.py

Checks, and exits with code 1 on any failure:
  1. every relationship line of the ERD (section 4) agrees with its forward and reverse sentence (section 4.1);
     Mermaid crow's-foot rule: the marker next to an entity says how many of THAT entity relate to one row
     of the other (CUSTOMER ||--o{ ORDER: a customer places zero or many orders; an order has exactly one customer);
  2. the attribute diagram (section 6.3) has the same relationship lines as the ERD;
  3. entities in the catalogue = tables in the schema; columns in section 6 = columns in the schema, name by name;
  4. every foreign key in the schema is one relationship of the ERD, and the other way round;
  5. the numbers written in the section 5 table equal the numbers counted here;
  6. every seed file loads (schema in memory, filename order, foreign keys on) — gate G3.
Standard library only.
"""
import csv, glob, io, os, re, sqlite3, sys

ROOT = os.getcwd()
DOC = os.path.join(ROOT, 'data', 'data-model-MB360.md')
SCHEMA = os.path.join(ROOT, 'data', 'schema', 'schema-MB360.sql')
SEED = os.path.join(ROOT, 'data', 'seed')
doc = open(DOC, encoding='utf-8').read()
sql = open(SCHEMA, encoding='utf-8').read()
errors = []

NEAR_LEFT = {'||': 'exactly one', '|o': 'zero or one', '}o': 'zero or many', '}|': 'one or many'}
NEAR_RIGHT = {'||': 'exactly one', 'o|': 'zero or one', 'o{': 'zero or many', '|{': 'one or many'}
REL = re.compile(r'^    (\w+) (\|\||\|o|\}o|\}\|)(--|\.\.)(\|\||o\||o\{|\|\{) (\w+) : "[^"]*"$', re.M)


def section(n):
    m = re.search(rf'^## {n}\. .*?(?=^## \d+\. |\Z)', doc, re.S | re.M)
    return m.group(0)


s4, s5, s6 = section(4), section(5), section(6)
erd = REL.findall(s4.split('### 4.1')[0])
attr = REL.findall(s6.split('### 6.3')[1])
if erd != attr:
    errors.append('section 6.3 relationship lines differ from section 4')

# 1. markers against the sentences of 4.1
rows = re.findall(r'^\| R\d+ \| (\w+) — (\w+) \| `([^`]*)` \| ([^|]*) \| ([^|]*) \|', s4, re.M)
if len(rows) != len(erd):
    errors.append(f'{len(erd)} relationship lines but {len(rows)} rows in 4.1')
for (left, lm, line, rm, right), (l2, r2, marker, fwd, rev) in zip(erd, rows):
    marker = marker.replace('\\|', '|')
    if (left, right, lm + line + rm) != (l2, r2, marker):
        errors.append(f'4.1 row order / marker differs: {left} {lm}{line}{rm} {right} vs {l2} {marker} {r2}')
    if NEAR_RIGHT[rm] not in fwd:
        errors.append(f'{left} {lm}{line}{rm} {right}: forward sentence should say "{NEAR_RIGHT[rm]}"')
    if NEAR_LEFT[lm] not in rev:
        errors.append(f'{left} {lm}{line}{rm} {right}: reverse sentence should say "{NEAR_LEFT[lm]}"')

# 3. catalogue vs schema
con = sqlite3.connect(':memory:')
con.executescript(sql)
tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY rowid")]
doc_tables = re.findall(r'^### ([A-Z_]+)$', s6, re.M)
if sorted(doc_tables) != sorted(tables):
    errors.append(f'tables differ: {sorted(set(doc_tables) ^ set(tables))}')
ncols = 0
for t in doc_tables:
    block = s6.split(f'### {t}\n', 1)[1].split('\n### ', 1)[0]
    phys = re.findall(r'^\| `\w+` \| `(\w+)` \|', block, re.M)
    real = [r[1] for r in con.execute(f'PRAGMA table_info({t})')]
    ncols += len(real)
    if phys != real:
        errors.append(f'{t}: section 6 columns {phys} != schema {real}')

# 4. foreign keys vs ERD relationships
fks = sorted((r[2], t) for t in tables for r in con.execute(f'PRAGMA foreign_key_list({t})'))
rels = sorted((l, r) for l, _, _, _, r in erd)
if fks != rels:
    errors.append(f'foreign keys and relationships differ: {sorted(set(fks) ^ set(rels))}')

# 6. seed load
con2 = sqlite3.connect(':memory:')
con2.executescript(sql)
con2.execute('PRAGMA foreign_keys = ON')
files = sorted(glob.glob(os.path.join(SEED, '*.csv')))
nrows = 0
for p in files:
    t = re.match(r'\d\d_([A-Z_]+)\.csv$', os.path.basename(p)).group(1)
    data = list(csv.reader(open(p, encoding='utf-8', newline='')))
    try:
        con2.executemany(f'INSERT INTO {t} ({", ".join(data[0])}) VALUES ({", ".join("?" * len(data[0]))})',
                         [[None if v == '' else v for v in r] for r in data[1:]])
    except sqlite3.Error as e:
        errors.append(f'seed {os.path.basename(p)}: {e}')
    nrows += len(data) - 1
if con2.execute('PRAGMA foreign_key_check').fetchall():
    errors.append('foreign_key_check reports errors')

# 5. numbers written in section 5
want = {
    'Stored entities / tables': [len(tables)] * 3,
    'Attributes / columns': [ncols, ncols],
    'Relationships / foreign keys': [len(fks), len(erd), len(fks)],
}
for label, nums in want.items():
    m = re.search(rf'^\| {re.escape(label)} \| (.*) \|$', s5, re.M)
    got = [int(x) for x in re.findall(r'\b\d+\b', m.group(1))] if m else []
    if got[:len(nums)] != nums:
        errors.append(f'section 5 "{label}": written {got[:len(nums)]}, counted {nums}')
m = re.search(r'(\d+) tables, (\d+) files, (\d+) rows', s5)
if not m or [int(x) for x in m.groups()] != [len(tables), len(files), nrows]:
    errors.append(f'section 5 seed numbers differ: counted {len(tables)} tables, {len(files)} files, {nrows} rows')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'OK — {len(tables)} tables, {ncols} columns, {len(erd)} relationships = {len(fks)} foreign keys; '
      f'every marker agrees with both sentences; section 5 numbers agree; {len(files)} seed files, {nrows} rows load in filename order')
