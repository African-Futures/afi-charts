# AFI chart conventions, as built in Flourish

Derived from the underlying config of ten published AFI visualisations (Nov 2025 – Sep 2026), read from the live embeds rather than from screenshots. Palette, chart settings and rendered CSS are exact. Last updated 2026-09-08.

---

## 1. The ten reference charts

| ID | Title | Form | Author / date |
|---|---|---|---|
| 30132773 | Median age per region, 1960-2025 | Multi-line, shaded gap | Kyle Hiebert, 02.09.2026 |
| 29707410 | Fatalities in Sudan: April 2023 to June 2026 | Choropleth + proportional points | Enoch, 16.07.2026 |
| 29505908 | Top 10 countries of origin of immigrants residing in South Africa: 2001-2022 | Stacked bar (horizontal) | Blessing, 26.06.2026 |
| 29611546 | Number of notable AI models* by geographic region: 2010-2025 | Stacked column + net-sum labels | Jakkie, 07.07.2026 |
| 29495087 | African crude oil exports by destination: 2024 | Sankey | Blessing, 25.06.2026 |
| 29205156 | Size of acquired land through land deals by region | Treemap (nested, resquarify) | Bronwyn, 01.06.2026 |
| 28329222 | Africa-China trade, 2000-2025 | Grouped column + overlaid line | Marvellous, 01.04.2026 |
| 26599492 | Electricity generation by source in Africa: 2000-2023 | Stacked area, direct-labelled | Hiebert, 03.12.2025 |
| 26710711 | External debt by World Bank income group: 2024 | Dot plot / strip by category | Tumi, 09.12.2025 |
| 26045266 | Number of people per urban centre, 1990 vs 2030 | Map with spikes, two-period comparison | Burgert, 05.11.2025 |

Spread: six time-series or categorical comparisons, one flow, one hierarchy, one distribution, two maps. Naming convention throughout: `{Author} blog {DD.MM.YYYY} chart {n}`.

---

## 2. Palette as actually used

Charts override the Flourish categorical palette per chart. The first three slots are near-invariant:

| Slot | Hex | Name | Used as slot 1–3 in |
|---|---|---|---|
| 1 | `#172859` | ISS navy | 5 of 10 |
| 2 | `#f58220` | ISS orange | 6 of 10 |
| 3 | `#5cba60` | ISS green | 5 of 10 |

**House sequence: navy → orange → green.** Variants seen in slot 1–3: `#004ea2` (mid blue), `#389d63` (deeper green), `#213f7f`, `#04183e` (map points only).

Extended colours drawn on for slots 4+, all present in the Tableau ISS Today guide:
`#b72325` red · `#8064a2` purple · `#5791cd` light blue · `#eaa22f` amber · `#004ea2` blue · `#660066` aubergine · `#e6cf98` sand · `#7f0f3b` maroon · `#58585a` grey · `#213f7f` deep blue

Off-guide colours that have crept in:
`#a58ac7` (light purple, 30132773) · `#f2b90f` (yellow, used deliberately in 29495087 and 26599492) · `#ff7b00`, `#9852d9`, `#04183e` (26045266 map points) · `#4328e7` (Flourish default, set but not visibly used)

Never used from the guide: `#d1d2d4`, `#eff0f1`, `#8c1d1b`.

**Known weakness.** Beyond roughly slot 3–4, most charts leave the Flourish stock tail in place: `#f54e8b`, `#fa6502`, `#f2b90f`, `#058896`, `#09aa64`, `#de2c35`, `#a7abaf`, `#808080`. Any series that runs deep enough into the palette therefore renders in colours that are not ISS colours.

Only **29505908** is fully on-palette (11 of 11 from the guide). **29495087** is on-palette but for `#f2b90f`. **26599492** shows the failure mode concretely: its twelve energy sources are drawn against an eleven-colour palette whose last two entries are the Flourish stock greys `#a7abaf` and `#808080` — so the deepest series render in stock colours *and* one colour repeats. Verified in the live render.

Non-categorical colour:
- Sequential map ramp: Flourish stock `FlourishOranges`, not reversed (29707410)
- Point strokes: `#919191` at 0.5 (29707410), `#ffffff` (26045266)
- Mark strokes: `#2e2e2e` (26710711)

---

## 3. Typography and chrome, as rendered

No chart sets a font. All ten inherit the Flourish default theme, which currently renders as **Canva Sans Variable**, not Century Gothic.

Measured from the live embeds and verified on three charts across three different templates (30132773 line, 29505908 stacked bar, 26599492 stacked area) — identical in all three:

| Element | Value |
|---|---|
| Canvas background | `#ffffff` |
| Title | bold 700, `#333333` |
| Body / labels | `#333333` |
| Axis tick labels | `#4a4a4a` |
| Gridlines | `#eeeeee` |
| Y-axis line | hidden on every chart (`y.line_visible: false`) |
| X-axis line | hidden on 28329222 and 26710711, shown elsewhere |

Title size is set to custom on 9 of 10; the recurring value is **1.4** (1.45 once). Subtitle custom size sits at **1.1–1.25**.

---

## 4. The house grammar

Conventions that recur across enough charts to count as practice, not accident:

**Chrome**
- `layout.footer_logo_enabled: false` on all ten. The Flourish logo is always suppressed.
- Legend swatches customised to `width/height 0.7–0.8`, `radius 2` — small, slightly rounded. Consistent wherever a legend appears.
- `legend_categorical.order_override` used to force legend order to match visual stacking order (29611546, 26045266).

**Labelling over legends**
- Line and area charts turn on end labels (`line_end_labels: true`) and then restrict them to the two to four series that carry the argument (`line_labels.show_only_labels`). 26599492 goes further: legend off entirely, direct labels only.
- Stacked columns carry net-sum labels above the stack (`stack_labels: "net_sum"`).
- Bar labels sit above/right of the bar with a background plate (`labels_bg_mode: "on"`).

**Analytic devices**
- A dashed line marks the reference or average series (`line_dash_items: "Global average"`, dash 10 / gap 7).
- Shading between two lines makes the gap itself the subject (`shade_between_lines_config: "Africa :: Global average"`).

**Units and number formatting**
- Units live in the number format, not only the axis title: `prefix: "$"` + `suffix: "B"` (28329222), `suffix: "%"` (29505908), divide-by-1,000,000 with `suffix: "M"` (29205156).
- Y-axis title is short and positioned `side`: "Median age", "GWh", "US$", "Number of notable AI models".

**Axes**
- `x.linear_min` is set a little below the first data point rather than left to auto — 1958 for data from 1960, 1999 for 2000, 1998 for 2000, 2010 for 2010. Deliberate breathing room at the left edge.

**Sourcing**
- Every chart names its source and carries a URL. `layout.multiple_sources: true` where there are two; the second source is labelled with its role, e.g. "Simplemaps (points)", "(accessed 01 June 2026)".
- The source label itself is sometimes customised to carry a citation year: `"Source: Land Matrix, [2026]. "`.
- `layout.footer_note` carries long methodological definitions — what counts as a "notable AI model", how the Land Matrix defines a land deal. Definitions go in the footer, caveats go in the subtitle.

**Titles and subtitles**
- Title pattern: `{Measure} by {dimension} in {place}: {year range}`, colon before the range, occasionally a comma. Descriptive, never a claim.
- Subtitle carries the caveat or the unit: "Data from 2024 are forecasts", "Events sized by number of fatalities, ranging from 1 to 1000", "measured in millions of people".

---

## 5. Where this diverges from the Tableau ISS Today guide

| Item | Tableau guide | Flourish practice | Note |
|---|---|---|---|
| Font | Century Gothic | Flourish default (Canva Sans Variable) | No Flourish chart sets a font. Largest single inconsistency between the two output channels. |
| Text colour | Black | `#333333` title/body, `#4a4a4a` ticks | Flourish practice is softer and, for on-screen work, better. |
| Gridlines | `#f5f5f5` | `#eeeeee` | Flourish slightly darker. |
| X-axis line | `#555555`, solid, thinnest | Shown by default; hidden on two charts | Inconsistent. |
| Y-axis line | Not shown | Not shown on all ten | Agrees. |
| Palette order | `#172859`, `#004ea2`, `#389d63`, `#d1d2d4`, `#58585a`… | `#172859`, `#f58220`, `#5cba60`… | Flourish leads with a navy/orange contrast pair; the guide leads with two blues. Flourish order is the better default for categorical work. |
| Palette depth | 17 defined colours | ISS colours for ~3–4 slots, Flourish stock beyond | Needs fixing. |

**Three decisions worth making before the D3 work starts**, since a coded pipeline will bake them in:

1. **Font.** Century Gothic is not a web font and has no free equivalent; if the site is to match, a substitute needs choosing deliberately rather than inheriting whatever Flourish ships.
2. ~~**Full-depth categorical ramp.**~~ **Resolved — see section 7 below.**
3. **Grey scale.** One set of values for text, ticks, gridlines and axis lines across both Tableau and D3 output.

---

## 6. Carrying this into D3

Directly reusable:

- Suppress chart chrome; white ground; no y-axis line; gridlines only.
- Direct end labels on the salient two to four series, legend suppressed or reduced to small rounded swatches.
- Dashed stroke reserved for a reference/average series.
- Shaded band between two lines where the gap is the point.
- Units in the tick formatter, short axis title at the side.
- Source line with named source, URL, access date where relevant; definitional footnote separate from the caveat subtitle.
- Padded domain minimum rather than a tight fit to the data.

Needs building rather than porting: the popup/tooltip behaviour (Flourish templates supply it — custom headers such as `{{Name}}` with `Fatalities: {{Fatalities}}` bodies), the size legend for proportional-symbol maps, and the filter/nesting interaction in the treemap.

---

## 7. The AFI series ramp (resolved 2026-09-08)

The fixed eight-slot categorical sequence for all AFI charts. Assign in order, never cycle.

```
#172859, #e67500, #004ea2, #389d63, #892e88, #e79f2b, #9e234f, #5791cd
```

| Slot | Hex | Name | Provenance | L | C | On white | ΔE to next |
|---|---|---|---|---|---|---|---|
| 1 | `#172859` | ISS navy | guide | 0.294 | 0.091 | 14.15:1 | 37.3 |
| 2 | `#e67500` | ISS orange | snapped from `#f58220` | 0.680 | 0.170 | 3.04:1 | 30.2 |
| 3 | `#004ea2` | ISS blue | guide | 0.436 | 0.151 | 8.04:1 | 28.1 |
| 4 | `#389d63` | ISS green | guide | 0.622 | 0.128 | 3.40:1 | 19.8 |
| 5 | `#892e88` | Aubergine | snapped from `#660066` | 0.470 | 0.165 | 7.47:1 | 37.1 |
| 6 | `#e79f2b` | Amber | snapped from `#eaa22f` | 0.755 | 0.148 | 2.24:1 | 31.1 |
| 7 | `#9e234f` | Maroon | snapped from `#7f0f3b` | 0.470 | 0.161 | 7.48:1 | 20.4 |
| 8 | `#5791cd` | Light blue | guide | 0.643 | 0.109 | 3.31:1 | — |

Separation is OKLab ΔE ×100, worst of simulated protanopia and deuteranopia (Machado–Oliveira–Fernandes 2009, severity 1.0). Target ≥ 8; worst boundary here is 19.8.

**Why this order.** The house opening was navy → orange → green. Orange and green are the one pair in the ISS palette that collapses under red–green colour blindness (ΔE 7.2, inside the 6–8 warning band), and putting them in slots 2 and 3 made them adjacent. Inserting ISS blue between them fixes it at no cost to the house look: navy and orange still open, green still sits high at slot 4.

**Snapping.** Only 7 of the 17 guide colours sit inside the usable lightness band with enough chroma to do identity work. Three slots hold the guide's hue but move lightness or chroma into range. Slots 1, 3, 4 and 8 are guide-exact.

**Series caps.**

- Lines, bars, stacks, areas — **8 slots.** Only neighbours touch, so only neighbours must separate.
- Scatter, bubble, choropleth, small multiples — **3 slots** (navy, orange, blue). Any two marks can sit side by side, so every pair must separate. Slot 4 drops the worst pair to 7.2; slot 5 to 4.8.
- Beyond the cap: fold the tail into "Other", facet into small multiples, or stop colouring by category. A ninth series is never a new hue.

**Two recorded deviations.**

1. Slot 1 sits below the lightness band (0.294 vs 0.43) and just under the chroma floor (0.091 vs 0.10). Kept because it is the ISS identity colour and the practical risks are absent — 14.15:1 contrast and the ramp's strongest boundary at 37.3.
2. Slot 6 is 2.24:1 against white, below the 3:1 mark floor. Wherever slot 6 is in play it must carry a direct label, a visible value, or a table view — which AFI charts already do as end labels, but it stops being optional.

**Strict alternative**, if a clean automated run ever matters more than the navy: `#3250a8, #e67500, #805caa, #389d63, #892e88, #e79f2b, #b72325, #5791cd` — all six checks pass, worst boundary 16.9. Costs the ISS navy in slot 1 and pushes ISS blue out of the ramp.

## 8. Chart greyscale (resolved 2026-09-08)

All values from the ISS Today palette; two previously unused colours get a job.

| Role | Hex | On white | Replaces |
|---|---|---|---|
| Title & primary ink | `#172859` | 14.15:1 | black (Tableau) / `#333333` (Flourish) |
| Labels, ticks, axis line | `#58585a` | 7.10:1 | `#4a4a4a` |
| Gridlines | `#d1d2d4` | 1.51:1 | `#eeeeee` / `#f5f5f5` |
| Panel & band fill | `#eff0f1` | 1.14:1 | — (unused until now) |
| Surface | `#ffffff` | — | unchanged |

Text never wears a series colour. A coloured mark beside the label carries identity; the words stay in ink.

Typography is settled in section 9; sequential ramps in section 10.

Reference page: *AFI Series Ramp* artifact, published 2026-09-08.

---

## 9. Chart typography (revised 2026-09-08)

**Open Sans throughout — the same face the website already uses.**

```css
--chart-display: "Open Sans", system-ui, -apple-system, sans-serif;  /* titles */
--chart-body:    "Open Sans", system-ui, -apple-system, sans-serif;  /* plot text */

.chart { font-family: var(--chart-body); font-variant-numeric: tabular-nums; }
.chart-title { font-weight: 400; }   /* futures.issafrica.org sets headings at 300–400 */
```

Verified live on futures.issafrica.org: the site is Open Sans everywhere, body and headings alike, with H1/H2 at 35px weight 300–400 and body text `#464545`. There is no second family anywhere on the site.

**Why this replaced the earlier Jost + IBM Plex Sans pairing.** Jost was chosen as a web stand-in for Century Gothic. But the site's actual web voice was already Open Sans — that decision predates this work. Keeping Jost in charts alone would not have preserved the brand; it would have made the charts the one element on the page that did not match. An embedded chart should read as part of the article, not as a foreign object.

Open Sans is also a good chart face on its own merits, not a compromise:

| | Open Sans | IBM Plex Sans | Jost | Century Gothic |
|---|---|---|---|---|
| Label width @13px | 175.2px | 167.6px | 160.9px | 189.4px |
| vs Century Gothic | −7.5% | −11.5% | −15.0% | — |
| x-height / cap | **0.761** | 0.743 | 0.657 | 0.736 |
| Tabular figures | by default | by default | needs `tnum` | by default |

The largest x-height of any candidate, which is what carries 11–12px axis labels, and tabular figures with no CSS to forget. It costs 4.5% more width than IBM Plex Sans — the only real trade.

There is also a free performance gain: the parent article already loads Open Sans, so the iframe takes it from browser cache rather than fetching two more families.

**Superseded:** Jost + IBM Plex Sans. The measurement table for all eleven candidates is kept above for reference, but the decision is closed.

## 10. Sequential ramps for choropleths (agreed 2026-09-08)

**Rule: chosen per chart, but always built from a colour in the ISS Today style guide.** Never a stock ramp — the current use of Flourish's `FlourishOranges` is the thing this replaces. Pick the anchor hue for what the map is about, then generate the ramp from it.

Method, so any anchor produces a valid ramp:

1. Take the guide colour's OKLCH hue and hold it — one hue only, never a rainbow.
2. Space five steps evenly in lightness from the light end down to L 0.40.
3. Let chroma rise toward the dark end (roughly 45% to 105% of the anchor's own chroma), capped at the hue's in-gamut ceiling.
4. Set the lightest step so it clears **2:1 against white** — otherwise the low end of the scale disappears on the page.

Worked five-step ramps from the guide anchors, all validated (monotone lightness, adjacent ΔL ≥ 0.06, single hue, light end ≥ 2:1):

| Anchor | Ramp, light → dark |
|---|---|
| ISS orange `#f58220` | `#dda987` `#ca875a` `#b66425` `#924c13` `#6d370a` |
| ISS blue `#004ea2` | `#98b6e0` `#739acf` `#4d7dbe` `#2560ac` `#0b458b` |
| ISS green `#389d63` | `#96bea3` `#70a581` `#488c61` `#177343` `#0e5630` |
| ISS red `#b72325` | `#e8a39c` `#d57e75` `#c25850` `#ac2c2a` `#871115` |
| ISS navy `#172859` | `#a8b4cf` `#8897ba` `#697ba5` `#4b5f90` `#30447b` |
| ISS purple `#8064a2` | `#bcafcd` `#a090b7` `#8672a0` `#6d548a` `#543774` |

Generator — self-contained, pass any guide hex:

```js
// OKLCH <-> sRGB helpers omitted for brevity; use any OKLCH library (culori: oklch/formatHex/inGamut).
const maxC = (L,H) => { let lo=0, hi=0.42;
  for (let i=0;i<40;i++){ const m=(lo+hi)/2; inGamut({L,C:m,H}) ? lo=m : hi=m; } return lo; };
const step = (L,H,C,i) => hexFromOklch({ L, C: Math.min(maxC(L,H)*0.92, C*(0.45+0.15*i)), H });

function seqRamp(anchorHex, n = 5) {
  const { H, C } = oklch(anchorHex);
  let hiL = 0.90;                                   // lightest step: solve for >= 2.05:1 on white
  while (contrast(step(hiL,H,C,0), '#ffffff') < 2.05 && hiL > 0.5) hiL -= 0.005;
  const loL = 0.40;
  return Array.from({length:n}, (_,i) => step(hiL + (loL-hiL)*i/(n-1), H, C, i));
}
```

For a **diverging** scale (a measure with a real midpoint — change, balance, surplus/deficit) use two guide anchors from opposite sides of the wheel with a neutral grey midpoint, equal steps per arm. Never put a hue at the midpoint.

---

## 11. Embedding and hosting (tested 2026-09-08)

Charts go into OpenCMS articles as an `<iframe>`; pasted raw HTML does not survive the editor. Each chart is therefore a single self-contained HTML file at a stable public URL.

**Claude artifact URLs cannot be used.** `claude.ai` serves artifact pages with `Content-Security-Policy: frame-ancestors 'self'`, so no other site may frame them. Viewing and sharing work normally — only embedding is blocked. Artifacts remain the right place to *review* a chart before publishing it.

Hosting options, in order of least setup:

1. **Netlify Drop** — drag a folder onto the page, get a permanent public URL with a free account, re-drag to update. No git. Framing allowed.
2. **GitHub Pages** — one public repo with Pages enabled; update by drag-and-drop through github.com. More setup, but versioned and survives a change of staff.
3. **OpenCMS VFS** — cleanest institutionally, since URLs stay on issafrica.org, but uploads go through the web team, so it is not self-service.

Hosting is only needed at publication. It does not block chart design.
