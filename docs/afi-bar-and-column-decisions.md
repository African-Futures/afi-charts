# AFI bar and column charts — decisions and verification (resolved 2026-09-11)

Companion to *AFI chart conventions (from Flourish)*, which settles the palette,
greyscale, typography and sequential ramps. This doc covers what was decided
while building the bar/column template, and how it was verified.

Template: `claude/AFI bar chart template.html`
Live preview: https://african-futures.github.io/afi-charts/bar-template-preview.html

---

## 1. One template, eight forms

Two orientations × four modes, all from `CONFIG`:

| | `single` | `grouped` | `stacked` | `stacked100` |
|---|---|---|---|---|
| `orient: "bar"` | horizontal ranking | | top-10-by-origin pattern | share comparison |
| `orient: "column"` | time series | Africa–China pattern | AI-models pattern | |

Plus the devices the Flourish back-catalogue actually used: net-sum labels on
stacks, a dashed reference line, threshold bands, a forecast boundary on a year
axis, and a series carried as a line on a second axis.

## 2. Decisions that differ from the line template

**There is no `vMin`.** A bar encodes length, so its axis starts at zero. Negative
data opens the domain downward and draws a zero line. This is the one knob
deliberately removed — a truncated bar axis is a misread waiting to happen.

**`sort` warns on a year axis.** Ordering years by size is a lie about a time
series. `sort: "none"` is correct there and the template says so in the console.

**Long category names belong on `orient: "bar"`.** Columns wrap their labels
(below), but a 35px band cannot hold a country name at any angle.

**Angled x-axis labels were rejected.** A tilted label costs width as well as
height — the plot gives up space on both sides for the overhang — and reads
slower than two short stacked lines. Category labels wrap onto up to `catLines`
(default 2, max 3) horizontal lines, with overflow ellipsised. A fixed line
allowance also keeps the height constant across widths.

**Axis titles live in their own row** at the top of the SVG, above the legend and
outside the plot. Positioned inside the plot, relative to a margin that changed
size with the label settings, the title repeatedly landed on the top gridline and
through the topmost tick. A row of its own cannot collide with anything.

**The forecast annotation gets its own strip** immediately above the plot, with
the boundary line running up into it. Inside the plot it sat over whatever the
bars were doing — on a 100% stack, where every column fills the full height, it
landed on a segment label.

**Every label is fit-tested and dropped when it does not fit.** Segment labels,
stack totals and per-bar values all measure against their own slot and are simply
not drawn where they would collide. Partial labelling is the intended behaviour:
the tooltip and the table carry every value. The alternative — printing anyway —
produces the unreadable rows this template was repeatedly caught doing.

**Segment label colour is chosen per segment from the fill's luminance.** Ink on
light fills, white on dark. This is what keeps slot 6 amber readable; white on
amber at 2.24:1 would be worse than no label.

**Bars reserve legend rows for the narrow end (340px).** A column chart's height
is fixed by `CONFIG.height`, so a wrapped legend takes its row from the plot. A
bar chart's height is derived from its rows, so a wrapping legend pushed the
whole SVG taller — it grew 558 to 576 between 520px and 400px. Reserving costs a
little whitespace on a wide screen and buys one published iframe height that is
right everywhere.

## 3. CONFIG keys new to this template

| Key | Purpose |
|---|---|
| `orient`, `mode` | the form matrix above |
| `sort` | `"none"` / `"desc"` / `"asc"` by category total |
| `catLines` | lines a wrapped column label may use (1–3, default 2) |
| `segmentLabels` | value inside each stack segment, where it fits |
| `segmentLabelFormat` | `"value"` / `"share"`; null = share on 100%, value otherwise |
| `stackTotals` | net sum at the end of each stack |
| `highlight` | categories drawn orange while the rest grey back |
| `overlayLine` | `{series, title, decimals}` — a series as a line on a second axis |
| `refLines`, `valueBands` | dashed reference lines; shaded threshold regions |
| `rowHeight` | bars: px per category; null picks a default |

`valueLabels` governs the label at the bar's *end*; `segmentLabels` the values
*inside* a stack; `stackTotals` the net sum. They are independent.

## 4. Measured iframe heights

Maxima across 1040–360px, rounded up. The SVG is constant at every width; the
figure grows at narrow widths because the title and subtitle wrap, which is why
the protocol is measure-the-max rather than compute-it.

| | bar | column |
|---|---|---|
| 8 categories, single | 540 | 690 |
| 8 categories, stacked / 100% | 560 | 690 |
| 8 categories, grouped | 750 | 690 |
| 16 years, single | 760 | 660 |
| 16 years, stacked / 100% | 800 | 660 |
| 16 years, grouped | 1380 | 660 |

Past roughly 700px a bar chart stops being readable in an article. The template
warns above that; the 1380 case should be faceted or turned into columns.

## 5. How this was verified — and what did not work

D3 and every CDN are blocked from the sandbox, so nothing can be rendered before
publishing. The chart went live on GitHub Pages and was audited in a browser.

**What did not work.** Six passes of "does anything fall outside the SVG" found
nothing while three separate collisions sat *inside* it. Bounds testing cannot
see two labels on top of each other. A single-width audit missed every fault that
only appears when the plot is narrow. A single toggle-state audit missed a fault
that lived entirely in `valueLabels: false`.

**What worked**, and what to repeat on the next chart type:

1. **Furniture against furniture.** Test every text element against every other
   for overlap, titles against gridlines, and labels against the mark they
   belong to — not only against the SVG's edges.
2. **Sweep widths.** 1040 / 860 / 700 / 560 / 440 / 360. Most faults live at the
   narrow end, where bands shrink and ticks crowd.
3. **Sweep toggles, not just forms.** Label states and devices change the layout.
   The first collision a human spotted was reachable only with value labels off.
4. **Check the pane is real before believing a number.** A collapsed browser pane
   reported a 28px-wide chart and produced confident nonsense, including a width
   sweep that returned an identical height at every probe and looked like proof.
   Assert a sane width before measuring.
5. **Fix the sibling.** Three times, a fix applied to one case and not the
   identical one beside it: totals but not per-bar labels, one wrap branch but
   not the other. When you add a fit test or a trim, find its siblings.

The final audit was 32 configurations × 6 widths = 192 renders, zero faults.

## 6. Carry back to the line template

- **Its table toggle changes the figure's height** the same way this one did.
  Inside a fixed iframe a shorter table leaves a hole in the article. Fix: give
  the table container the plot's exact box rather than only a max-height.
- The **axis-title row**, the **label fit rule** and the **PNG exporter's tspan
  support** are improvements the line template should adopt when next touched, so
  the two stay one system rather than two.
