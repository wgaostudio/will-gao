import fs from 'node:fs';
import { mathjax } from 'mathjax-full/js/mathjax.js';
import { TeX } from 'mathjax-full/js/input/tex.js';
import { SVG } from 'mathjax-full/js/output/svg.js';
import { liteAdaptor } from 'mathjax-full/js/adaptors/liteAdaptor.js';
import { RegisterHTMLHandler } from 'mathjax-full/js/handlers/html.js';
import { AssistiveMmlHandler } from 'mathjax-full/js/a11y/assistive-mml.js';
import { AllPackages } from 'mathjax-full/js/input/tex/AllPackages.js';
const adaptor=liteAdaptor();AssistiveMmlHandler(RegisterHTMLHandler(adaptor));
const tex=new TeX({packages:AllPackages});
const svg=new SVG({fontCache:'local'});
const path=new URL('../src/content/martingales-diffusions.html',import.meta.url);
let content=fs.readFileSync(path,'utf8');
const data=JSON.parse(fs.readFileSync(new URL('../src/data/martingale-typesetting.json',import.meta.url),'utf8'));
const doc=mathjax.document('',{InputJax:tex,OutputJax:svg});
let count=0;
for(const item of data){
 if(!content.includes(item.html))throw new Error('Source fragment missing; run import and normalization before typesetting.');
 const node=doc.convert(item.tex,{display:item.display});
 const rendered=adaptor.outerHTML(node);
 if(rendered.includes('data-mml-node="merror"'))throw new Error('Invalid TeX: '+item.tex);
 content=content.replace(item.html,rendered);count++;
}
fs.writeFileSync(path,content);
console.log(`Typeset ${count} inline and display expressions.`);
