#!/usr/bin/env python3
"""Environment check for the DBIZ3 team repository (Session 6 test T1), run from the repository root:

    uv run tools/check_env.py                 # workstation only
    uv run tools/check_env.py --repo          # workstation + repository (T1)
    uv run tools/check_env.py --repo --path A # Path A members: also checks Claude Code

Every line is PASS, WARN or FAIL. The script exits with code 1 when any line is FAIL.
A WARN is acceptable only when it is explained in docs/env/readiness-report.md.

This is the team's own version of the Session 6 starter-kit check (the starter kit was not in the repository
when it was set up). If the instructors provide the official tools/check_env.py, replace this file with it.
Standard library only; Python 3.11 or later (uv downloads it when needed).
"""
import argparse, glob, os, re, shutil, subprocess, sys

ROOT = os.getcwd()
SPEC_KIT_VERSION = '1.0.1'
results = []


def report(status, name, detail=''):
    results.append(status)
    print(f'{status:<5} {name:<34} {detail}')


def run(cmd):
    """Run a command; return (exit code, combined output). Exit code 127 when it cannot start."""
    exe = shutil.which(cmd[0])
    if exe is None:
        return 127, 'not found on PATH'
    try:
        p = subprocess.run([exe] + cmd[1:], capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=120, cwd=ROOT)
        return p.returncode, (p.stdout + p.stderr).strip()
    except OSError as e:  # for example blocked by an application-control policy
        return 126, str(e).splitlines()[0]
    except subprocess.TimeoutExpired:
        return 124, 'timed out'


def version(text):
    m = re.search(r'(\d+)\.(\d+)\.(\d+)', text)
    return tuple(int(x) for x in m.groups()) if m else None


def read(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return f.read()


def first_line(path):
    return read(path).splitlines()[0].strip() if os.path.getsize(os.path.join(ROOT, path)) else ''


# ---------------------------------------------------------------- workstation

def check_workstation(path):
    v = sys.version_info
    report('PASS' if v >= (3, 11) else 'FAIL', 'Python >= 3.11', f'{v.major}.{v.minor}.{v.micro}')

    code, out = run(['git', '--version'])
    report('PASS' if code == 0 else 'FAIL', 'git', out.splitlines()[0] if out else '')
    if code == 0:
        _, name = run(['git', 'config', '--global', 'user.name'])
        _, mail = run(['git', 'config', '--global', 'user.email'])
        report('PASS' if name and mail else 'FAIL', 'git identity (user.name / email)',
               'set' if name and mail else 'run git config --global user.name / user.email')

    code, out = run(['gh', '--version'])
    report('PASS' if code == 0 else 'FAIL', 'GitHub CLI', out.splitlines()[0] if code == 0 else out)
    if code == 0:
        code, _ = run(['gh', 'auth', 'status'])
        report('PASS' if code == 0 else 'FAIL', 'GitHub CLI login', 'logged in' if code == 0 else 'run gh auth login')

    code, out = run(['uv', '--version'])
    report('PASS' if code == 0 else 'FAIL', 'uv', out if code == 0 else out)

    code, out = run(['node', '--version'])
    nv = version(out) if code == 0 else None
    if nv is None:
        report('FAIL', 'Node.js 24 LTS', out)
    else:
        report('PASS' if nv[0] >= 24 else 'WARN', 'Node.js 24 LTS', out)

    # Spec Kit: `specify version`, or `uv tool list` when the executable cannot be started
    # (Windows application-control policies sometimes block uv tool shims).
    code, out = run(['specify', 'version'])
    sv = version(out) if code == 0 else None
    how = 'specify version'
    if sv is None:
        code2, out2 = run(['uv', 'tool', 'list'])
        m = re.search(r'specify-cli v(\d+\.\d+\.\d+)', out2) if code2 == 0 else None
        sv = version(m.group(1)) if m else None
        how = f'uv tool list (specify could not run: {out[:60]})'
    if sv is None:
        report('FAIL', f'Spec Kit {SPEC_KIT_VERSION}', 'not installed: see Setup Guide step 6')
    else:
        found = '.'.join(map(str, sv))
        status = 'PASS' if found == SPEC_KIT_VERSION else 'FAIL'
        if status == 'PASS' and how != 'specify version':
            status = 'WARN'
        report(status, f'Spec Kit {SPEC_KIT_VERSION}', f'{found} via {how}')

    if path == 'A':
        code, out = run(['claude', '--version'])
        report('PASS' if code == 0 else 'FAIL', 'Claude Code (Path A)', out.splitlines()[0] if out else '')


# ---------------------------------------------------------------- repository

PLACEHOLDER = re.compile(r'<(?:[a-z][^<>\n]{1,60})>')
HTML_TAGS = {'br', 'br/', 'details', 'summary', 'sup', 'sub', 'b', 'i', 'u', 'kbd', 'p'}


def placeholders(text):
    found = []
    for m in PLACEHOLDER.finditer(text):
        inner = m.group(0)[1:-1].strip().lower()
        if inner.split()[0].rstrip('/') in HTML_TAGS or inner.startswith('!--'):
            continue
        found.append(m.group(0))
    return found


def files_with_heading(prefix):
    hits = []
    for p in glob.glob(os.path.join(ROOT, '**', '*.md'), recursive=True):
        rel = os.path.relpath(p, ROOT).replace(os.sep, '/')
        if rel.startswith(('.specify/', '.agents/', '.claude/', '.git/')):
            continue
        if first_line(rel).startswith(prefix):
            hits.append(rel)
    return sorted(hits)


def check_repo():
    if not os.path.isfile(os.path.join(ROOT, 'AGENTS.md')):
        report('FAIL', 'repository root', 'AGENTS.md not found: run from the repository root')
        return

    agents = read('AGENTS.md')
    ph = placeholders(agents)
    report('FAIL' if ph else 'PASS', 'AGENTS.md has no <...>', ', '.join(ph[:3]) if ph else 'complete')
    report('PASS' if re.search(r'generate_seed\.py', agents) else 'FAIL', 'AGENTS.md states the seed command')
    report('FAIL' if os.path.exists(os.path.join(ROOT, 'CLAUDE.md')) else 'PASS', 'no CLAUDE.md',
           'Claude Code reads AGENTS.md')

    try:
        integ = read('.specify/integration.json')
        ok = f'"version": "{SPEC_KIT_VERSION}"' in integ
        report('PASS' if ok else 'FAIL', f'.specify/ (Spec Kit {SPEC_KIT_VERSION})',
               'agy' + (' + claude' if '"claude"' in integ else ''))
    except OSError:
        report('FAIL', '.specify/', 'missing: specify init (Setup Guide C5)')

    rules = glob.glob(os.path.join(ROOT, '.agents', 'rules', '*.md'))
    ok = any('AGENTS.md' in open(r, encoding='utf-8').read() for r in rules)
    report('PASS' if ok else 'FAIL', '.agents/rules/ always-on rule', 'reads AGENTS.md' if ok else 'missing (C6)')

    constitution = '.specify/memory/constitution.md'
    if os.path.exists(os.path.join(ROOT, constitution)):
        left = re.findall(r'\[[A-Z_0-9]{4,}\]', read(constitution))
        report('WARN' if left else 'PASS', 'constitution filled', ', '.join(left[:3]) if left else 'no [PLACEHOLDER]')

    # the chain (Session 7 rubric section 3.1), found by first heading
    if os.path.exists(os.path.join(ROOT, 'docs/prd.md')):
        h = first_line('docs/prd.md')
        report('PASS' if h.startswith(('# PRD:', '# MVP Scope v3:')) else 'FAIL', 'docs/prd.md heading', h[:40])
    else:
        report('FAIL', 'docs/prd.md', 'missing')

    specs = files_with_heading('# Spec Document:')
    report('PASS' if specs else 'FAIL', 'Spec Document(s)', f'{len(specs)} found')
    models = files_with_heading('# Data Model and Mockup Data:')
    report('PASS' if models else 'FAIL', 'Data model', ', '.join(models) or 'none')
    for m in models:
        report('PASS' if 'erDiagram' in read(m) else 'FAIL', '  Mermaid ERD', m)
    screens = files_with_heading('# Screen Spec:')
    report('PASS' if screens else 'WARN', 'Screen Specs (recommended)', f'{len(screens)} found')

    schemas = glob.glob(os.path.join(ROOT, 'data', 'schema', 'schema-*.sql'))
    report('PASS' if schemas else 'FAIL', 'data/schema/schema-<ID>.sql', f'{len(schemas)} found')
    seeds = glob.glob(os.path.join(ROOT, 'data', 'seed', '*.csv'))
    gen = glob.glob(os.path.join(ROOT, 'data', 'seed', 'generate*.py'))
    readme = os.path.exists(os.path.join(ROOT, 'data', 'seed', 'README.md'))
    report('PASS' if seeds and gen and readme else 'FAIL', 'data/seed/ (files, generator, README)',
           f'{len(seeds)} CSV, generator {"yes" if gen else "no"}, README {"yes" if readme else "no"}')

    for doc in ('docs/env/readiness-report.md', 'docs/ai-use-log.md'):
        report('PASS' if os.path.exists(os.path.join(ROOT, doc)) else 'FAIL', doc)

    # secrets (gate G5): tracked files only; the full history is checked with git log --all -p
    code, tracked = run(['git', 'ls-files'])
    if code == 0:
        bad = [f for f in tracked.splitlines() if re.search(r'(^|/)\.env(\.|$)|\.pem$|\.key$|id_rsa', f)]
        report('FAIL' if bad else 'PASS', 'no .env / key file committed', ', '.join(bad) or 'none tracked')
    report('PASS' if os.path.exists(os.path.join(ROOT, '.gitattributes')) else 'FAIL', '.gitattributes (line endings)')

    # seed reproducibility (T2 dry run: writes nothing)
    if gen:
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        p = subprocess.run([sys.executable, os.path.relpath(gen[0], ROOT), '--check'], cwd=ROOT, env=env,
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        last = (p.stdout.strip().splitlines() or [''])[-1]
        report('PASS' if p.returncode == 0 else 'FAIL', 'seed generator --check', last[:70])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--repo', action='store_true', help='also check the repository (run from its root)')
    ap.add_argument('--path', choices=['A', 'B', 'C'], default='B', help='your access path (Setup Guide 0.2)')
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    print(f'DBIZ3 environment check - path {args.path}' + (' - repository' if args.repo else ''))
    check_workstation(args.path)
    if args.repo:
        check_repo()
    fails, warns = results.count('FAIL'), results.count('WARN')
    print(f'\n{len(results)} checks: {results.count("PASS")} PASS, {warns} WARN, {fails} FAIL')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
