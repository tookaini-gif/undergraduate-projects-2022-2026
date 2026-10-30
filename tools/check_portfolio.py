"""Check the publishable source tree, README navigation and excluded artifacts."""
import ast
import re
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
errors=[];sources=0;links=0
for path in ROOT.rglob('*'):
    rel=path.relative_to(ROOT)
    if '.git' in rel.parts or '__pycache__' in rel.parts:continue
    if not path.is_file():continue
    if path.suffix=='.py':
        try:ast.parse(path.read_text(encoding='utf-8-sig'),filename=rel.as_posix());sources+=1
        except (SyntaxError,UnicodeError) as e:errors.append(f'{rel}: {e}')
    if path.suffix=='.md':
        text=path.read_text(encoding='utf-8')
        for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)',text):
            if target.startswith(('https://','http://','mailto:','#')):continue
            target=unquote(target.split('#',1)[0]);links+=1
            if not (path.parent/target).exists():errors.append(f'{rel}: broken link {target}')
    if path.suffix.lower() in {'.sqlite','.db','.pt','.pth','.task','.ckpt','.zip','.rar','.exe','.dll','.pkl','.pickle','.h5'}:
        errors.append(f'{rel}: local data/model/build artifact in publish tree')
    if path.stat().st_size>50*1024*1024:errors.append(f'{rel}: unexpectedly large file')
projects=[p for p in ROOT.glob('*/*') if p.is_dir() and p.name.startswith('项目')]
for project in projects:
    if not (project/'README.md').is_file():errors.append(f'{project}: README missing')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print(f'OK: {len(projects)} projects, {sources} Python files parsed, {links} local document links checked')
