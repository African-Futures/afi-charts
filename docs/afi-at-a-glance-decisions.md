# "At a glance" summary blocks — how they work and why

The summary block replaces the Canva slider at the top of a country page on
futures.issafrica.org, just above the grey Executive Summary panel. The template
is `templates/afi-at-a-glance-template.html`. The first published block is
`sudan-at-a-glance.html`, and the template's default content is that block.

## Why not the Canva slider

Measured on the Sudan page, the slider cost 47 requests, 7 outside domains
(including telemetry and Sentry), about 1.2 MB of JavaScript and about 5.5 MB of
assets once unpacked. It was also slow to update and looked foreign on the page.
The block is one request, about 61 KB compressed, with nothing loaded from
outside the file.

## What a block contains

- a headline sentence and a short line under it (the sub-headline)
- a row of context figures
- five tabs, each holding one finding: a headline, a short paragraph and a chart
- a link from each tab to the matching section of the report page
- a source line

## Hosting: an iframe with no page script

For now the web team is not involved, so:

- the block is hosted on GitHub Pages and embedded as an iframe, like the charts
- raw HTML pasted into OpenCMS is stripped, which is why it has to be an iframe
- nothing can run on the article page, so the block cannot resize its iframe

That makes the iframe a **fixed box**, as it is for the charts. Anything that
does not fit is clipped silently.

```html
<iframe src="https://african-futures.github.io/afi-charts/<country>-at-a-glance.html"
        title="<Country> at a glance" width="100%" height="840"
        frameborder="0" scrolling="no"></iframe>
```

- **840 px** is the tested height, for iframe widths from 320 px (a 360 px phone
  less the page's 20 px margins) to 810 px (the article column).
- 800 works for the Sudan block only when the iframe is 360 px or wider.
- No `loading="lazy"`: the block sits at the top of the page. Chart iframes
  further down should have it.

The fully native option — an OpenCMS content template, with no iframe, which
search engines would also index — needs the web team, and is for later.

## Fitting the fixed box

The block detects that it is in an iframe (`window.self !== window.top`, or
`?framed=1` for testing) and adds the class `afi-framed` to `<html>`. Then:

- the block is `height: 100vh`, laid out as a flex column
- the header, context figures and tabs take their natural height, and the open
  panel takes the rest
- each chart is drawn at the height its box is given, and redrawn when the width
  or height changes (a `ResizeObserver`, and again once the font has loaded)

**Charts are never squeezed below 150 px.** When the open panel has too little
room, `fit()` hides optional lines one at a time, re-measuring after each, until
every chart box is at least 150 px tall (measured exactly, not rounded), the
scenario rows fit in their box and the section link sits above the source line. The order is fixed:

1. the sub-headline (`.afi-g-dek`)
2. the legend (`.afi-g-key`) — the line ends are labelled anyway. A legend
   marked `.keep` is never hidden: the ratio chart's is, because at phone
   widths there is no room to name its lines at their ends
3. the tab's paragraph (`.afi-g-p`)
4. the captions (`.afi-g-cap`)

A caption marked `.keep` — the one explaining worked-out values — is never
hidden, and neither are numbers or charts. `fit()` runs again on every tab
switch and resize, starting with everything visible.

**Outside an iframe** the block flows at its natural height. On screens 560 px
and wider every panel gets the same minimum height, so the page doesn't jump
when switching tabs.

The block also posts its height to the parent page (`afiGlanceHeight`). Nothing
listens yet; it only matters if the web team ever adds a resize listener.

## Structure of the file

- **Wording** is plain HTML, which editors can change directly. Every place that
  changes per country is marked `PER COUNTRY`.
- **Chart numbers** are all in the `DATA` block at the top of the script, marked
  `/*__DATA__*/` as in the bar template. Each value carries a comment saying
  where on the report page it is quoted.
- **Charts** are hand-written SVG, with no D3, so the file stays self-contained:
  - `fork()` — the history line splitting into Current Path (dashed navy) and
    the scenario (orange)
  - `pop()` — population columns
  - `ratio()` — a small line chart of working-age people per dependant, one
    value a year, Current Path (dashed navy) against the scenario (orange),
    with the 1.7 threshold as a dashed green rule
  - `levers()` — the ranking chart
  - `dumbbell()` — the "what changes by 2043" rows
- **Tabs** are full ARIA tabs that work with the arrow keys, Home and End.
  Without JavaScript every panel shows, one after another.
- **Font**: Open Sans, the Latin variable font from Google Fonts (the same file
  the site loads, 48 KB), embedded as base64. Keep it embedded: the block must be
  self-contained.
- **Links** are full URLs to the report's section anchors, with `target="_top"`
  so they open in the article window rather than inside the iframe. Read the
  anchors from the live page.

## Design choices

- White background with thin rules, because the grey Executive Summary panel
  sits directly underneath.
- The eyebrow ("Sudan at a glance") is in the site's heading green `#389d63`.
  The headline is Open Sans at weight 300, matching the site's H2.
- Navy for the Current Path and history, orange for the scenario, grey for
  de-emphasised series.
- Text is always in ink colours, never series colours; the dot carries the
  colour.
- On the history charts, lines join only the values quoted in the report, and
  the captions say so. They are not annual data. The ratio chart is annual data
  from an IFs extract.
- A label beside the first history point goes below it when the line rises
  from it, and above it when the line falls, so the line never crosses it.

## Making a new country

1. Copy the template to the repo root as `<country>-at-a-glance.html`.
2. Use the same five-tab pattern, but choose the findings that suit that report.
3. Replace everything marked `PER COUNTRY`, and `DATA`.
4. **Use only figures quoted on the report page**, or an annual series from an
   IFs extract supplied for the purpose (say which file in the `DATA` comment,
   and check its end value against the figure the page quotes). Where the page
   only gives a difference, a value may be worked out from it: mark it `derived: true`
   (it gets a `*`), keep the `.keep` caption, and note how it was worked out.
   Never invent provenance: the model version and date in the source line come
   from the report page.
5. Check the report text for figures that don't add up, and leave those out
   rather than choose between them. On Sudan this removed GDP per capita and the
   age shares.
6. Run the render check and fix anything it finds:

   ```
   python tools/verify-glance-fit.py <country>-at-a-glance.html
   ```

   It must report 0 failures at 840 and 880 across all widths. A chart with more
   labels than Sudan's may need a larger height; measure it with `--heights`,
   never assume.

## The render check

`tools/verify-glance-fit.py` serves the repo, embeds the block in an iframe on a
host page, and checks every tab at each height and width:

1. the source line sits inside the iframe
2. nothing in the open panel runs into the source line
3. each chart box is at least 150 px tall, and the drawn chart is no taller
4. no two text labels in a chart overlap, none falls outside the chart, and no
   drawn line (data or reference, not gridlines) runs through a label
5. the last scenario row doesn't run into the caption below it
6. there is no sideways scrolling

As `CLAUDE.md` says, test labels against each other, not only against the
edges.

Sudan's results: no failures at 840, 880 and 900. At 800, the last tab fails
below 360 px. At 760, it fails at most widths.
