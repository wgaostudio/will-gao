# Will Gao — personal website

An Astro static site with Home, Writing, Notes, Research, Teaching, About, and six complete mathematical notes. The design follows the supplied warm paper, moss, and serif reference.

## Build

Requires Node 22 and npm. Install with `npm ci`, then `npm run build`. Output is `dist/`.

Set `SITE_URL` to the final public origin when building for your domain. It controls canonical links, structured data, Open Graph URLs, robots.txt, and the sitemap. Its current fallback is the private review deployment.

## Editing

- Homepage: `src/pages/index.astro`
- Research: `src/pages/research.astro`
- Biography and experience: `src/pages/about.astro`
- Note titles, descriptions, dates, and prerequisites: `src/data/notes.json`
- Complete note bodies: `src/content/*.html`
- Shared article template: `src/pages/notes/[slug].astro`
- Theme and responsive layouts: `src/styles.css`
- Original photo: `public/portrait.jpg`

Original note HTML is preserved in `sources/`. To re-import after editing those originals, run, in order:

1. `python scripts/import-notes.py`
2. `node scripts/prepare-math.mjs`
3. `python scripts/normalize-notes.py`
4. `python scripts/typeset-martingale-additions.py`
5. `node scripts/render-martingale-additions.mjs`
6. `python scripts/unify-statements.py`
7. `npm run build`

Re-importing overwrites the processed note bodies and generated contents indexes. Edit either originals and re-import, or processed content directly; do not mix the two approaches without reconciling changes. The importer preserves existing editorial titles and descriptions in `src/data/notes.json`.

Math remains pre-rendered. Gradient descent includes build-time MathJax SVG and assistive MathML. Existing MathML is retained in the other source exports. Its native math layout must never be overridden with CSS `display: block`; overflow is handled by surrounding containers. The martingale source’s 83 plain-HTML expressions are transcribed and typeset with MathJax using `src/data/martingale-typesetting.json`. The PCA source supplied only SVG; its original vectors are preserved and given structured equation labels derived from MathJax's node tree. Original TeX would allow a stronger semantic MathML version of this note. Mathematical claims have not been independently audited.

## GitHub Pages

A deployment workflow is included in `.github/workflows/pages.yml`. It works whether the site is served at the root of an origin (a personal `<username>.github.io` repository, or a custom domain) or at a project subpath (`<username>.github.io/<repo>`). The workflow passes GitHub Pages' configured `base_url` and `base_path` into the build as `SITE_URL` and `BASE_PATH`; `astro.config.mjs` reads `BASE_PATH` into its `base` option, and internal links/assets go through the `withBase()` helper in `src/base.js` so they resolve correctly under either scheme.

Copy this project to the intended GitHub repository and enable GitHub Pages with GitHub Actions as the source. No further configuration is required for a project subpath deploy; add a custom domain later via a `public/CNAME` file if desired.

## Content decisions

The Writing page includes the two complete essays supplied by the author, with original publication links and credits. Musical theater is the primary writing focus. Teaching lists the upcoming Autumn 2026 CSE 422 assistantship without a historical course link. About reflects the user-confirmed fourth-year BS/MS status, pure mathematics double major, June 2027–June 2028 job-search window, and Autumn 2028 return for the master’s year. Add the actual CV at `public/cv.pdf` and rebuild to activate the CV link. No unpublished research methods or internal Madrona operational details are included. Dates shown on notes come from the supplied material; the undated Substack essay has no invented publication date.

## Verification

The production build completed. Statement and proof classes are normalized by `scripts/unify-statements.py`; the shared stylesheet owns their presentation. Motion only runs when reduced motion is not requested, and does not animate article pages. All internal page links, contents anchors, and portrait references were checked. Each page has one H1, unique canonical metadata, and a description. The site has responsive CSS and print styles; browser-based visual and screen-reader testing has not been performed.
