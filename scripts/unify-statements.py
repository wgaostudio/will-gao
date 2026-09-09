"""Attach common presentation classes without rewriting statement contents."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
for p in (root/'src/content').glob('*.html'):
 source=p.read_text()
 counts={'statement':0,'proof-block':0,'derivation-block':0}
 def replace(m):
  opening=m.group(0);classes=m.group(1).split();kind=None
  if set(classes)&{'ltx_theorem','thm','theorem'}:kind='statement'
  elif set(classes)&{'ltx_proof','proof'}:kind='proof-block'
  elif 'ltx_derivation' in classes:kind='derivation-block'
  if kind:
   counts[kind]+=1
   if kind not in classes:opening=opening.replace('class="'+m.group(1)+'"','class="'+m.group(1)+' '+kind+'"')
  return opening
 source=re.sub(r'<div\b[^>]*class="([^"]+)"[^>]*>',replace,source)
 p.write_text(source)
 print(p.stem,counts)
