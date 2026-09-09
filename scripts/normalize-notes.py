from pathlib import Path
import re,json,html,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
def speech(e):
 kind=e.attrib.get('data-mml-node','')
 if 'data-c' in e.attrib:
  return chr(int(e.attrib['data-c'],16))
 children=[speech(c) for c in e];children=[x for x in children if x]
 if not children:return (e.text or '').strip()
 if kind=='mfrac' and len(children)==2:return f'(fraction {children[0]} over {children[1]})'
 if kind=='msup' and len(children)==2:return f'{children[0]} superscript ({children[1]})'
 if kind=='msub' and len(children)==2:return f'{children[0]} subscript ({children[1]})'
 if kind=='msubsup' and len(children)==3:return f'{children[0]} subscript ({children[1]}) superscript ({children[2]})'
 if kind=='msqrt':return 'square root of ('+' '.join(children)+')'
 if kind=='mover' and len(children)==2:return f'{children[0]} with {children[1]} above'
 if kind=='munder' and len(children)==2:return f'{children[0]} with {children[1]} below'
 if kind=='mtr':return 'row ('+', '.join(children)+')'
 return ' '.join(children)
f=root/'src/content/spectral-theorem-pca.html'
s=f.read_text()
def accessible(m):
 x=m.group(0)
 if 'data-mml-node="math"' not in x:return x
 label=speech(ET.fromstring(x))
 # Label the original vector image; do not alter its mathematical drawing.
 return x.replace('role="img"', 'role="img" aria-label="'+html.escape(label,quote=True)+'"',1)
def accessible_container(match):
 container=match.group(0)
 start=container.find('<svg');end=container.rfind('</svg>')+6
 if start<0:return container
 class VectorMatch:
  def group(self,number):return container[start:end]
 return container[:start]+accessible(VectorMatch())+container[end:]
s=re.sub(r'<mjx-container\b[^>]*>.*?</mjx-container>',accessible_container,s,flags=re.S)
f.write_text(s)
for f in (root/'src/content').glob('*.html'):
 s=f.read_text()
 s=re.sub(r'<nav\b[^>]*>.*?</nav>','',s,flags=re.S)
 s=re.sub(r'<h1\b[^>]*>.*?</h1>','',s,flags=re.S)
 s=re.sub(r'<p class="(?:ltx_)?(?:author|authors|date)"[^>]*>.*?</p>','',s,flags=re.S)
 s=s.replace('<main>','<div>').replace('</main>','</div>')
 toc=[];count=0
 def heading(m):
  global count
  level,attrs,body=m.groups()
  if body.strip()=='Abstract':return m.group(0)
  count+=1
  match=re.search(r'\bid="([^"]+)"',attrs)
  ident=match.group(1) if match else 'section-'+str(count)
  if not match:attrs+=' id="'+ident+'"'
  clean=re.sub(r'<svg\b.*?</svg>','',body,flags=re.S)
  clean=re.sub('<[^>]*>',' ',clean)
  clean=' '.join(html.unescape(clean).split())
  toc.append({'id':ident,'title':clean,'level':int(level)})
  return '<h'+level+attrs+'>'+body+'</h'+level+'>'
 s=re.sub(r'<h([23])([^>]*)>(.*?)</h\1>',heading,s,flags=re.S)
 f.write_text(s)
 (root/'src/data'/f'{f.stem}-toc.json').write_text(json.dumps(toc,ensure_ascii=False))
print('Normalized article headings, linked contents, and PCA equation labels.')
