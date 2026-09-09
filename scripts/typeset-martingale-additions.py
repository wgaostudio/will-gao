"""Convert the source's plain HTML math to TeX without changing its claims."""
from pathlib import Path
import re,html,json
root=Path(__file__).resolve().parents[1]
p=root/'sources/note-2.html'
s=p.read_text()
# Explicit transcriptions for fractions, integrals and aligned equations.
overrides={
2:r'X_t = M_t + A_t,',
8:r'\{X_\tau : \tau\le T\}',
11:r'M_t^2 = M_0^2 + N_t + \langle M\rangle_t,',
20:r'Y_t = Y_0 + \int_0^t H_s\,dX_s + L_t.',
24:r'\begin{aligned} H &= \frac{d\langle X,Y\rangle}{d\langle X\rangle},\\ L_t &= Y_t-Y_0-\int_0^t H_s\,dX_s.\end{aligned}',
25:r'd\langle X,\int H\,dX\rangle=H\,d\langle X\rangle',
33:r'M_t^f := f(X_t)-f(X_0)-\int_0^t Lf(X_s)\,ds',
37:r'M_t := X_t-X_0-\int_0^t \mu(X_s)\,ds',
38:r'X_t^2-X_0^2-\int_0^t [2X_s\mu(X_s)+\sigma^2(X_s)]\,ds',
40:r'\langle M\rangle_t = \int_0^t \sigma^2(X_s)\,ds.',
42:r'W_t := \int_0^t \frac{1}{\sigma(X_s)}\,dM_s.',
45:r'dX_t = \mu(X_t)\,dt + \sigma(X_t)\,dW_t.',
48:r'\int \mathbf{1}_{\{\sigma(X_s)=0\}}\,dW^{\prime}_s',
52:r'\begin{aligned}Z_t^{(\lambda)} := \exp\Bigl\{&\lambda(X_t-X_0)-\lambda\int_0^t\mu(X_s)\,ds\\&-\frac{\lambda^2}{2}\int_0^t\sigma^2(X_s)\,ds\Bigr\}.\end{aligned}',
53:r'N_t=X_t-X_0-\int_0^t\mu(X_s)\,ds',
54:r'dN_t=\sigma(X_t)\,dW_t',
55:r'd\langle N\rangle_t=\sigma^2(X_t)\,dt',
56:r'\exp(\lambda N-\lambda^2\langle N\rangle/2)',
57:r'dZ_t^{(\lambda)} = \lambda Z_t^{(\lambda)}\sigma(X_t)\,dW_t.',
59:r'\mathbb{E}\exp\left\{\frac{\lambda^2}{2}\int_0^T\sigma^2(X_s)\,ds\right\} < \infty.',
62:r'\mu(X_t)\,dt',
63:r'\sigma^2(X_t)\,dt',
64:r'Lf(x) = \frac{1}{m(x)}\frac{d}{dx}\left\{\frac{f^{\prime}(x)}{s(x)}\right\}.',
65:r'\frac{s^{\prime}}{s}=-\frac{2\mu}{\sigma^2}',
66:r'\frac{1}{m}=\frac{\sigma^2s}{2}',
68:r'\frac{d}{dx}\left\{\frac{f^{\prime}(x)}{s(x)}\right\} = -m(x)g(x).',
75:r'\frac{G^{\prime}(y+,y)}{s(y)}-\frac{G^{\prime}(y-,y)}{s(y)}=-1.',
76:r'g(y)m(y)\,dy',
80:r'\begin{aligned}\frac{d}{dt}\int\varphi(y)p(t,x,y)\,dy &= \frac{d}{dt}P_t\varphi(x)\\ &= P_tL\varphi(x)\end{aligned}',
81:r'\begin{aligned}&=\int L\varphi(y)p(t,x,y)\,dy\\&=\int\varphi(y)L_y^*p(t,x,y)\,dy.\end{aligned}',
}
chars={'−':'-','τ':r'\tau ','≤':r'\le ','⟨':r'\langle ','⟩':r'\rangle ','∫':r'\int ','μ':r'\mu ','σ':r'\sigma ','λ':r'\lambda ','∈':r'\in ','ℝ':r'\mathbb{R}','∞':r'\infty ','≠':r'\ne ','↦':r'\mapsto ','φ':r'\varphi ','∂':r'\partial ','′':"'"}
items=[]
for i,m in enumerate(re.finditer(r'<(span|div) class="math-(inline|display)">(.*?)</\1>',s,re.S)):
 raw=m.group(3)
 if i in overrides:tex=overrides[i]
 else:
  tex=html.unescape(raw).replace('{',r'\{').replace('}',r'\}')
  for a,b in chars.items():tex=tex.replace(a,b)
  while re.search(r'<(sub|sup)>((?:(?!<sub>|<sup>).)*?)</\1>',tex,re.S):
   tex=re.sub(r'<(sub|sup)>((?:(?!<sub>|<sup>).)*?)</\1>',lambda n:('_' if n[1]=='sub' else '^')+'{'+n[2]+'}',tex,flags=re.S)
  if '<sub>' in tex or '<sup>' in tex:raise ValueError(raw)
 items.append({'html':m.group(0),'tex':tex,'display':m.group(2)=='display'})
assert len(items)==83
(root/'src/data/martingale-typesetting.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print('Transcribed',len(items),'math fragments.')
