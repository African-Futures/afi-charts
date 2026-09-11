# AFI chart system — working instructions

This repository holds the African Futures & Innovation (ISS) interactive chart
system: two working D3 templates, the design decisions behind them, and the
tooling. Charts built here are published to GitHub Pages and embedded as
iframes in OpenCMS articles on futures.issafrica.org.

**The conventions are settled. Do not re-derive colours, type or chart
furniture — read them from `docs/` and apply them.**

## Where things are

```
templates/   the two working templates — start from these, never rewrite them
docs/        the design system, the bar/column decisions, publishing, style guide
tools/       IFs extract decoder, layout harness, review-page builder
preview/     the live switchable preview of the bar template
.claude/     the afi-chart skill, as synced from the account
```

Read before building: `docs/afi-chart-conventions-from-flourish.md` for the
system, `docs/afi-bar-and-column-decisions.md` for the bar template's reasoning
and its CONFIG keys, `docs/publishing-an-afi-chart-github-pages.md` for how a
chart goes live.

## Non-negotiables

**Never invent provenance.** Model versions, scenario names, access dates,
institutional attributions: if it is not in the extract and the user has not
said it, ask. A fabricated version number in a source line is invisible in
review and wrong in publication. This has happened once.

**The filename is the public URL** and is baked into live articles. It can never
change once published. Lower case, hyphens, no accents.

**The iframe is a fixed box.** The chart cannot grow. Anything that would expand
the page is silently clipped and the article still looks fine, so nobody
notices. Three consequences, built into the templates: the table replaces the
chart and takes its exact box; the SVG height is constant at every width; the
iframe height is measured, never assumed.

**Series ramp**, in order, never cycled:
`#172859 #e67500 #004ea2 #389d63 #892e88 #e79f2b #9e234f #5791cd`
Eight slots for lines, bars, stacks, areas. Three (navy, orange, blue) for
scatter, bubble, choropleth, small multiples. A ninth series is never a new hue.

**Greyscale**: ink `#172859` · labels/ticks `#58585a` · muted `#7d8899` ·
gridlines `#d1d2d4` · panel `#eff0f1` · surface `#ffffff`.

**Type**: Open Sans throughout, titles at weight 400, tabular numerals on the
chart root. The site uses Open Sans for everything; a chart in another face is
the one foreign object on the page.

## Building a chart

1. **Ask only what the data cannot tell you** — the IFs model version, where the
   chart should end, which series are subject vs context, any group code the
   decoder flagged. Never ask about colour, fonts or hover behaviour.
2. **Decode the extract** with `tools/ifs-decoder.py`. It detects header rows
   rather than assuming them, and flags unverified group codes rather than
   guessing at expansions. When a variable or group is missing, add it and
   commit the decoder back.
3. **Start from the template** that fits the form. Everything per-chart lives in
   the `CONFIG` block. Everything below `CONFIG` is the shared system — a change
   there is a change to every chart, not a per-chart edit.
4. **Emit two files**: `<slug>.html` standalone for hosting, and
   `<slug>.artifact.html` with the outer document tags stripped, for review.

## Verifying a chart

Whatever the environment, some of this is doable without a browser: round-trip
every cell of the embedded payload against the source; spot-check values against
the literal file bypassing the decoder; confirm the year range after truncation;
confirm axis bounds do not clip real values; confirm series do not exceed the
ramp.

**The render check is not optional, and it is not bounds testing.** This was
learned the hard way building the bar template — six passes of "does anything
fall outside the SVG" found nothing while three collisions sat inside it.

1. **Assert the viewport is real before believing a number.** A collapsed
   browser pane once reported a 28px-wide chart and produced a width sweep that
   returned an identical height at every probe, which looked like proof the
   layout was stable. It was not.
2. **Test furniture against furniture.** Every text element against every other
   for overlap; titles against gridlines; each label against the mark it belongs
   to. Not only against the SVG's edges.
3. **Sweep widths and toggles.** 1040 / 860 / 700 / 560 / 440 / 360, and each
   label state and device on and off. Nearly every fault found lived at a narrow
   width or in a feature combination, never in the default view.
4. **Fix the sibling.** Three separate bugs were a fix applied to one case and
   not the identical one beside it — a fit test added to stack totals but not
   per-bar labels, one branch of a wrap function but not the other.
5. **Measure the height, don't compute it.** The SVG is constant across widths
   but the figure grows as the title and subtitle wrap. Take the max across the
   sweep and round up to the next 10. Known heights are in the decisions doc.

`tools/verify-bar-layout.js` runs the pure layout functions against exact
reimplementations of `scaleBand`/`scaleLinear` — useful where a browser is not
available, but it is not a substitute for the render check.

## Known work outstanding

- **The line template's table toggle changes the figure's height.** A table
  shorter than the chart shrinks the whole figure, leaving a hole in the
  article. The bar template's fix is to give the table container the plot's
  exact box, not just a max-height. Marked in the source; port it.
- The line template should also adopt the **axis-title row**, the **label fit
  rule** and the **PNG exporter's tspan support** from the bar template, so the
  two stay one system rather than drifting into two.
- On narrow screens D3 picks sparse x-ticks on the line chart, so the first year
  can go unlabelled. Worth forcing the first tick when next touching it.

**Not yet built:** stacked area, dot plot, treemap, sankey, choropleth. Build on
demand, not speculatively. When one is built and accepted, add its template here
and update the skill.
