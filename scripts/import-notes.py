from pathlib import Path
import re,json,base64,html
root=Path(__file__).resolve().parents[1]
upload=root/'sources'
records=[
('6','spectral-theorem-pca','From the Spectral Theorem to PCA','SVD and Low-Rank Approximation','Mathematics of machine learning','March 2025','A derivation of singular value decomposition, optimal low-rank approximation, and principal component analysis from the spectral theorem.','Linear algebra, multivariable calculus, and basic proof techniques.'),
('3','gradient-descent','Gradient Descent','From Smooth Objectives to Stochastic Gradients','Mathematics of machine learning','March 2025','Convergence guarantees under smoothness, convexity, and strong convexity, followed by what changes with stochastic gradients.','Multivariable calculus, linear algebra, and basic probability.'),
('5','spectral-clustering','From K-Means to Spectral Clustering','Optimization, Graph Laplacians, and Random Walks','Mathematics of machine learning','March 2025','Lloyd’s algorithm, graph-partitioning relaxations, and the connection between graph Laplacians and random walks.','Linear algebra, eigenvalues, and basic optimization.'),
('7','linear-regression','Notes on Linear Regression','Ridge, Influence Diagnostics, and Autoregression','Mathematics of machine learning','March 2025','Least squares, ridge regularization, Cook’s distance, and the representation of autoregressive models as linear regressions.','Linear algebra, multivariable calculus, and introductory statistics.'),
('2','martingales-diffusions','From Martingales to Diffusions','','Probability and stochastic processes','December 2025','A path through conditional expectation, Brownian motion, Itô calculus, and diffusion generators.','Introductory probability and calculus.'),
('4','black-scholes','A First Pass at Black–Scholes','','Mathematical finance','March 2026','Geometric Brownian motion, risk-neutral pricing, replication, and American exercise problems.','Brownian motion, Itô’s formula, and basic martingales.')]
existing_path=root/'src/data/notes.json'
existing={n['slug']:n for n in json.loads(existing_path.read_text())} if existing_path.exists() else {}
data=[]
for num,slug,title,subtitle,group,date,summary,prereq in records:
 s=(upload/f'note-{num}.html').read_text()
 body=re.search(r'<body[^>]*>(.*)</body>',s,re.S).group(1)
 # Preserve mathematical content and source acknowledgments; remove runtime scripts.
 body=re.sub(r'<script\b[^>]*>.*?</script>','',body,flags=re.S)
 body=body.replace('William Gao','Will Gao')
 # Remove fixed/sidebar styles by retaining semantic source markup with shared CSS.
 body=re.sub(r'\sstyle="[^"]*"',lambda m:m.group(0),body)
 (root/'src/content'/f'{slug}.html').write_text(body)
 data.append(existing.get(slug, dict(slug=slug,title=title,subtitle=subtitle,group=group,date=date,summary=summary,prerequisites=prereq)))
(root/'src/data/notes.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))
print('Imported six complete notes.')
