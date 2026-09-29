import fs from 'node:fs';
import path from 'node:path';
import { mathjax } from 'mathjax-full/js/mathjax.js';
import { TeX } from 'mathjax-full/js/input/tex.js';
import { SVG } from 'mathjax-full/js/output/svg.js';
import { liteAdaptor } from 'mathjax-full/js/adaptors/liteAdaptor.js';
import { RegisterHTMLHandler } from 'mathjax-full/js/handlers/html.js';
import { AssistiveMmlHandler } from 'mathjax-full/js/a11y/assistive-mml.js';
import { AllPackages } from 'mathjax-full/js/input/tex/AllPackages.js';

const slug = process.argv[2];
if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
  throw new Error('Usage: node scripts/render-note-math.mjs <note-slug>');
}

const adaptor = liteAdaptor();
AssistiveMmlHandler(RegisterHTMLHandler(adaptor));
const tex = new TeX({
  packages: AllPackages,
  inlineMath: [['\\(', '\\)']],
  displayMath: [['\\[', '\\]']],
  macros: {
    argmax: '\\operatorname*{arg\\,max}',
    norm: ['\\left\\lVert #1 \\right\\rVert_\\infty', 1],
  },
});
const svg = new SVG({ fontCache: 'local' });
const notePath = path.resolve(`src/content/${slug}.html`);
const doc = mathjax.document(fs.readFileSync(notePath, 'utf8'), {
  InputJax: tex,
  OutputJax: svg,
});
doc.render();
fs.writeFileSync(notePath, adaptor.innerHTML(adaptor.body(doc.document)));
console.log(`Rendered ${slug} mathematics with embedded MathML.`);
