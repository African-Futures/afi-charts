# AFI charts

The African Futures & Innovation (ISS) interactive chart system: the working D3
templates, the design decisions behind them, the tooling, and the published
charts themselves.

Charts are served from GitHub Pages and embedded as iframes in OpenCMS articles
on futures.issafrica.org.

- Published chart: `https://african-futures.github.io/afi-charts/<slug>.html`
- Bar template preview: https://african-futures.github.io/afi-charts/bar-template-preview.html

## Start here

`CLAUDE.md` carries the working instructions — the house rules, the build steps,
the verification method and the outstanding work. It is read automatically when
this folder is opened in Claude Code or VS Code.

**The conventions are settled.** Do not re-derive colours, type or chart
furniture; read them from `docs/` and apply them.

## Layout

| Path | What it is |
|---|---|
| `CLAUDE.md` | Working instructions: the system, build steps, verification, outstanding work |
| `*.html` (root) | Published charts — the filename is the public URL |
| `templates/afi-line-chart-template.html` | The line chart template |
| `templates/afi-bar-chart-template.html` | The bar/column template — 2 orientations × 4 modes |
| `templates/afi-at-a-glance-template.html` | The "At a glance" summary block for the top of a country page — self-contained, no D3; renders with the Sudan block as its default |
| `docs/afi-chart-conventions-from-flourish.md` | The design system: ramp, greyscale, typography, sequential ramps, house grammar |
| `docs/afi-bar-and-column-decisions.md` | Why the bar template is shaped as it is; CONFIG keys; measured heights; verification method |
| `docs/afi-at-a-glance-decisions.md` | How the summary block fits a fixed iframe, the `fit()` order, design choices, making a new country |
| `docs/handover-at-a-glance.md` | Handover notes from the Claude app session that built the Sudan block, including problems found on the Sudan page |
| `docs/publishing-an-afi-chart-github-pages.md` | How a chart goes live and gets embedded |
| `docs/tableau-iss-today-style-guide.md` | The institutional Tableau guide, transcribed |
| `tools/ifs-decoder.py` | Decodes a raw International Futures CSV extract |
| `tools/verify-bar-layout.js` | Layout harness — runs the template's geometry functions against exact d3 scale reimplementations |
| `tools/verify-glance-fit.py` | Render check for a summary block — every tab at every iframe height and width (needs Playwright) |
| `tools/build-review-page.py` | Builds the preview page from the bar template, so the two cannot drift |
| `.claude/skills/afi-chart/SKILL.md` | The afi-chart skill |

Only files at the repository root are published as pages. `docs/`, `templates/`,
`tools/` and `.claude/` are source, not output.

`bar-template-preview.html` at the root is generated from
`templates/afi-bar-chart-template.html` by `tools/build-review-page.py`. Rebuild
it rather than editing it directly, or the two will drift.

## Two notes

**The line template does not run as-is.** Its data slot is a bare placeholder —
`const DATA = /*__DATA__*/;` — so the file is a syntax error until a payload is
substituted in. The bar template differs: its placeholder carries a working
default (`const DATA = /*__DATA__*/ { … }`), so it opens and renders straight
away. Worth aligning the two when the line template is next touched.

**The Tableau style guide is a transcription** of a .docx, not the original file.
It is the institutional guide for Tableau output; the D3 system diverges from it
deliberately in places, listed in the conventions doc, section 5.
