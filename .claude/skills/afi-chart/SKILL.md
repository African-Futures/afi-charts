---
name: afi-chart
description: "Build an interactive D3 chart in the AFI house style from a data extract, ready to embed on futures.issafrica.org. Use when someone asks for a line chart, bar chart, column chart, map or other data visualisation in the Data Visualisations project."
---

# AFI chart

Turn a data extract into one self-contained interactive HTML chart in the African Futures & Innovation house style, ready to upload to GitHub Pages and embed in OpenCMS as an iframe.

The conventions are already settled. Do not re-derive colours, type or chart furniture — read them from `docs/` and apply them.

## Repository files to read first

Paths are relative to the repository root.

| File | What it holds |
|---|---|
| `docs/afi-chart-conventions-from-flourish.md` | The full system: ramp, greyscale, typography, house grammar, sequential ramps, hosting |
| `templates/afi-line-chart-template.html` | The working line-chart template — start from this, do not rewrite it |
| `templates/afi-bar-chart-template.html` | The working bar/column template — two orientations, four modes |
| `docs/afi-bar-and-column-decisions.md` | Why the bar template is shaped as it is, its CONFIG keys, measured heights, and the verification method |
| `tools/ifs-decoder.py` | Decoder for raw International Futures extracts |
| `docs/publishing-an-afi-chart-github-pages.md` | How the finished file gets published and embedded |
| `tools/verify-bar-layout.js` | Layout harness — runs the template's geometry functions against exact d3 scale reimplementations |
| `tools/build-review-page.py` | Builds the preview page from the bar template, so the two cannot drift |

Read the relevant template and the decoder before building. Read the conventions doc when anything is unclear.

## Where charts live

Repository `african-futures/afi-charts`, served at `https://african-futures.github.io/afi-charts/<slug>.html`. The filename is the public URL and is embedded in live articles — it can never change once published.

## The iframe is a fixed box

Everything about these charts is shaped by one fact: the chart lives in an iframe of fixed pixel height inside an OpenCMS article. It cannot grow. Anything that would expand the page — a table opening, a legend appearing, a subtitle wrapping to another line — is silently clipped instead, and the article still looks fine, so nobody notices.

Three consequences, all already built into the templates:

- The **table replaces the chart** rather than stacking below it, and takes the plot's exact box — not just a max-height. A table *shorter* than the chart shrinks the figure and leaves a hole in the article.
- The **SVG keeps a constant height at every width**. Where a legend can wrap, either it takes its space from the plot (columns, lines) or the worst-case row count is reserved (bars).
- The **iframe height is measured, never assumed**. See Step 6.

## Never invent provenance

Model versions, scenario names, access dates, institutional attributions: if it is not in the extract and the user has not said it, **ask**. A fabricated version number in a source line is invisible in review and wrong in publication. This has happened once already.

## Citing International Futures

The house form, used for every IFs chart:

```js
source:    "International Futures version 8.71, Base scenario",
sourceUrl: "https://korbel.du.edu/pardee/",
```

Version number, then the scenario name taken from the extract's scenario row. The Pardee Institute is not named in the source text — the link carries that. **Ask for the version number** if it is not already known; the extract does not contain it. Version 8.71 was current in September 2026, but confirm rather than assume it still is.

## Step 1 — Ask before building

Ask only what the data cannot tell you. These come up nearly every time:

1. **Is this forecast data, and from which year?** Ask whenever the series extends beyond the current year or comes from IFs. The base year changes per chart and per model version — **never guess it**.
2. **Where should the chart end?** Extracts often run to 2100 when the argument stops at 2050. Compute endpoint separation at the candidate end years and say which ones crowd the end labels — that is real information for the decision, not a detail.
3. **Which series are the subject, and which are context?** Aggregates (Africa, Sub-Saharan Africa, World, income groups) default to grey dashed reference lines, because they usually contain the other series. Confirm it — sometimes the region *is* the subject.
4. **The IFs model version**, unless it is already known for this chart.
5. **Any series label the decoder flagged.** It flags unverified group codes rather than expanding them. A wrong expansion is a mislabelled chart nobody notices.

Do not ask about colour, fonts, hover behaviour, breakpoints or the table view. Those are settled.

## Step 2 — Read the data

For an IFs extract, use `tools/ifs-decoder.py`. It detects header row positions rather than assuming them, maps variable codes to readable labels, expands known group names, and flags unknown ones. When a variable code or group name is missing from its tables, add it and commit the decoder back so the next extract decodes cleanly.

For any other source, parse it directly, but report what you found before building: year range, series count, units, missing values. Never silently drop or interpolate a series.

Look at the data before drawing it. Peaks, turning points and crossovers are usually the story, and they change what the chart should emphasise and where it should end.

## Step 3 — Build

Start from the template that fits the form. Everything per-chart lives in the `CONFIG` block; everything below it is the shared system and changes only when the standard itself changes. A design-token change (colour, font) is one edit applied across both templates *and* every built chart — not a per-chart edit.

**Line template** — `title`, `subtitle`, `source`, `sourceUrl`, `yTitle`, `forecastFrom`, `forecastShade`, `yMin`/`yMax`, `yBands`, `excludeSeries`, `referenceSeries`, `decimals`, `xPad`, `height`.

**Bar/column template** — `orient` (bar/column) × `mode` (single/grouped/stacked/stacked100), plus `sort`, `catLines`, `valueLabels`, `segmentLabels`, `stackTotals`, `highlight`, `overlayLine`, `refLines`, `valueBands`, `forecastFrom`, `rowHeight`. The decisions doc has the full table and the reasoning.

Three bar rules worth knowing without opening the doc:

- **There is no `vMin`.** A bar encodes length, so its axis starts at zero. Negative data opens the domain downward.
- **Labels are fit-tested and dropped when they do not fit.** Partial labelling is intended; the tooltip and table carry every value. Never print a label row that collides.
- **Long category names go on `orient: "bar"`.** Column labels wrap onto two lines; they are never angled.

Emit two files: `<slug>.html` (standalone, with `<!DOCTYPE html>`, for hosting) and `<slug>.artifact.html` (outer document tags stripped, for review). Slugs are lowercase-with-hyphens.

Watch for literal `\uXXXX` escapes leaking into `<title>`: write real characters such as – directly.

## Step 4 — Verify (never skip)

**D3 and every CDN are blocked from the sandbox, so a chart cannot be rendered before publishing.** Verify everything that does not need a browser:

- Round-trip every cell of the embedded payload against the source and report the mismatch count.
- Spot-check four or five values against the literal file, bypassing the decoder.
- Confirm the year range matches the published range exactly after any truncation.
- Confirm every `referenceSeries` name exists in the data — a typo silently turns a reference line into a coloured series.
- Confirm `forecastFrom` falls inside the range, and that axis bounds do not clip real values.
- Confirm subject series do not exceed the eight ramp slots.
- Port the layout maths out and run it on the real data — stacks contiguous from zero and summing to the row total, 100% stacks topping out at 100, band positions ordered and non-overlapping.

Then say plainly that the chart has not been rendered and that the user is the first to see it.

## Step 5 — Review

Publish the `.artifact.html` version and list the interpretive decisions — which series became references, what base year was used, decimal places, anything inferred. Invite correction on each.

## Step 6 — Publish, then audit, then measure

Send the standalone `.html` file. The user uploads it to the `afi-charts` repository.

**Once it is live, open the URL in the browser — this is not optional.** It is the only real render check available, and estimating from a screenshot has produced published errors twice.

**Before believing any number, assert the browser pane is a real width.** A collapsed pane once reported a 28px-wide chart and produced confident nonsense, including a width sweep that returned an identical height at every probe and looked like proof the layout was stable. Read the chart's width first and refuse to measure below ~500px.

**Audit furniture against furniture, not just against the SVG's edges.** Bounds testing cannot see two labels sitting on top of each other. Six passes of "is anything outside the box" once found nothing while three collisions sat inside it. Test every text element against every other for overlap, titles against gridlines, and each label against the mark it belongs to.

**Sweep widths and toggles, not just chart forms.** 1040 / 860 / 700 / 560 / 440 / 360, and each label state and device on and off. Nearly every fault found in the bar template lived at a narrow width or in a feature combination, never in the default view.

**When you fix something, fix its sibling.** Repeatedly, a fit test was added to stack totals and not per-bar labels, or one branch of a wrap function and not the one beside it. Search for the identical case before moving on.

**Then measure the height rather than guessing it.** Set the viewport across a range of widths and read `.afi` height at each; take the largest and round up to the next 10. Measured heights for the standard forms are in the decisions doc — a line chart is around 660; an 8-category stacked bar 560. Too small silently clips the source line off the bottom.

```js
// run in the browser on the live chart page
const afi = document.querySelector('.afi'); const hs = [];
for (const w of [1100,960,860,760,640,560,480,400]) {
  document.documentElement.style.width = document.body.style.width = w+'px';
  render(); await new Promise(r=>setTimeout(r,150));
  hs.push(Math.ceil(afi.getBoundingClientRect().height));
}
document.documentElement.style.width = document.body.style.width = ''; render();
Math.ceil(Math.max(...hs)/10)*10;   // the iframe height to use
```

The SVG is constant across widths, but the *figure* grows at narrow widths because the title and subtitle wrap. That is why the protocol is measure-the-max rather than compute-it.

**Give the embed as a `<div>`-wrapped iframe.** OpenCMS wraps a bare iframe in a `<p>`, which indents the chart and adds paragraph spacing; a `<div>` is left alone and aligns flush with the body text.

```html
<div style="width:100%;margin:1.6em 0 0.9em;">
<iframe src="https://african-futures.github.io/afi-charts/<slug>.html"
        title="<chart title>"
        loading="lazy" scrolling="no"
        style="display:block;width:100%;height:<measured>px;border:0;padding:0;margin:0;"></iframe>
</div>
```

Do not use an aspect-ratio wrapper of the kind Canva embeds use. A slide scales with width; a chart does not — its height is constant across desktop widths, so a fixed pixel height is correct and a ratio would leave a growing gap on wide screens.

## The design system

**Series ramp**, in fixed order, never cycled:

```
#172859  #e67500  #004ea2  #389d63  #892e88  #e79f2b  #9e234f  #5791cd
```

Eight slots for lines, bars, stacks and areas. **Only three** (navy, orange, blue) for scatter, bubble, choropleth and small multiples, where any two marks can sit side by side. Past the cap: fold into "Other", facet, or stop colouring by category. A ninth series is never a new hue.

Slot 6 amber is 2.24:1 on white — wherever it appears it must carry a direct label or the table view. Text drawn *on* a fill picks ink or white from that fill's luminance, which is what keeps amber readable.

**Greyscale**: ink `#172859` · labels and ticks `#58585a` · muted `#7d8899` · gridlines `#d1d2d4` · panel `#eff0f1` · surface `#ffffff`.

**Type: Open Sans throughout**, matching futures.issafrica.org, which uses it for body and headings alike with no second family. Titles at weight 400 — the site sets headings at 300–400, so 500 or 600 shouts next to the surrounding article. `font-variant-numeric: tabular-nums` on the chart root. Open Sans has tabular figures by default and the largest x-height of the candidates tested, and the parent article already loads it, so the iframe takes it from cache. *(This supersedes an earlier Jost + IBM Plex Sans pairing; do not reintroduce it.)*

**Sequential ramps** for choropleths are chosen per chart but always built from a style-guide colour — never a stock ramp. Method and six worked ramps are in the conventions doc.

## House rules

- No y-axis line. Gridlines only. No chart-library logo.
- The chart container fills the iframe — no max-width, no centring — so its text aligns with the article body.
- Axis titles sit in their own row above the plot, not inside it.
- Direct end labels on the series that carry the argument, not a legend to decode. Below 560px, drop end labels for a legend under the plot.
- Dashed stroke is reserved for reference series and threshold annotations.
- Units in the tick formatter, short axis title at the side.
- Tick counts follow the room available; six value ticks do not fit a narrow plot.
- Caveats in the subtitle; definitions in a footnote.
- Padded domain minimum for lines; a hard zero baseline for bars.
- Text never wears a series colour, except a label drawn inside its own mark.
- Table view on every chart — accessibility, and the relief channel amber needs.

## Settled, and not

**Settled:** the line chart; the bar and column chart in both orientations and four modes; the ramp, greyscale, typography, hosting, embedding and height measurement.

**Not yet built:** stacked area, dot plot, treemap, sankey, choropleth. Build on demand rather than speculatively. When one is built and the user is happy with it, update this skill and add its template to `templates/`.

**Known rough edges:**

- The **line template's table toggle changes the figure's height** — a table shorter than the chart shrinks the whole figure, which inside a fixed iframe leaves a hole in the article. The bar template's fix is to give the table container the plot's exact box; port it when next touching the line template.
- The line template should also adopt the **axis-title row**, the **label fit rule** and the **PNG exporter's tspan support** from the bar template, so the two stay one system.
- On narrow screens D3 picks sparse x-ticks on the line chart, so the first year can go unlabelled. Worth forcing the first tick when next touching it.

Bespoke work needs no template. Design it in the conversation; if it works well, fold it in.