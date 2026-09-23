# Handover: "At a glance" summary blocks

Continuing work that started in the Claude app (Data Visualisations project), 23 Sep 2026.
Put this file in the repo at `docs/handover-at-a-glance.md`. The first Claude Code session can read it alongside `CLAUDE.md`.

---

## 1. What we're doing and why

Country pages on futures.issafrica.org open with a **Canva slider** in the intro, just above the grey Executive Summary panel. It is slow to update, looks foreign on the page and is heavy. We measured it on the Sudan page: 47 requests, 7 outside domains (including telemetry and Sentry), about 1.2 MB of JavaScript and about 5.5 MB of assets once unpacked.

We're replacing it with a **native, self-contained HTML summary block**. Each block has:

- a headline sentence and a short line under it
- a row of context figures
- five tabs, each holding one finding: a headline, a short paragraph and a real chart
- links to the matching section of the report page

The website audit concluded that the site needs **lazy loading and WebP images**, not different chart software. This block is in line with that: one request, about 61 KB compressed, and nothing loaded from outside the file.

**Decision: no involvement from the web team for now.** So:

- the block is hosted on GitHub Pages and embedded as an **iframe**, like the charts
- it must work **without any script on the article page**, so it can't resize its iframe
- raw HTML pasted into OpenCMS is stripped, which is why it has to be an iframe

## 2. Current state

| Item | Status |
|---|---|
| `sudan-at-a-glance.html` | Finished prototype. **Not yet committed.** The copy is in `C:\Users\dmclachlan\Downloads\`. It goes in the **repo root**. |
| Project doc `AFI at-a-glance summary template.html` | The same file, saved in the Claude project. |
| Push from the Claude app | Not possible. The session had no write access to `African-Futures/afi-charts`. Commit from VS Code instead. |

**First step:** copy `sudan-at-a-glance.html` into the repo root, commit and push. It then goes live at
`https://african-futures.github.io/afi-charts/sudan-at-a-glance.html`

## 3. Embed code (no page script needed)

```html
<iframe src="https://african-futures.github.io/afi-charts/sudan-at-a-glance.html"
        title="Sudan at a glance" width="100%" height="840"
        frameborder="0" scrolling="no"></iframe>
```

- **840 px** is the tested height. Every tab fits with nothing clipped or overlapping at iframe widths from 320 to 810 px. The article column is 810 px on desktop; on phones, the page's 20 px side margins leave 320 px on a 360 px screen.
- 800 also works when the iframe is 360 px or wider.
- Do **not** add `loading="lazy"` to this iframe, because it sits at the top of the page. Every chart iframe further down *should* get `loading="lazy"`.

## 4. How the block works

**It detects being in an iframe** (`window.self !== window.top`, or `?framed=1` for testing) and then switches to fixed-box mode (the `afi-framed` class):

- The block is `height: 100vh` in a flex column.
- The header, the context figures and the tabs take their natural height. The open panel takes the rest.
- Each chart is drawn at the height its container is given, and redrawn whenever the width or height changes.

**Charts never get squeezed below a usable size.** A function called `fit()` hides optional lines one at a time until every chart has at least 150 px and the list of scenario rows fits. The order is:

1. the line under the headline
2. the legend (the line ends are labelled anyway)
3. the tab's explanatory paragraph
4. the captions

The caption explaining the estimated values (`.afi-g-cap.keep`) is never hidden, and neither are numbers or charts.

**Outside an iframe** (for example, if pasted into a page some day), the block flows at its natural height. Panels get a steady minimum height so the page doesn't jump when switching tabs.

**Structure of the file:**

- **Wording:** plain HTML, which editors can change directly.
- **Chart numbers:** all in the `DATA` block at the top of the script, each with a note saying where on the report page it is quoted.
- **Charts:** hand-written SVG. No D3, because it's self-contained.
  - `fork()` draws the history line splitting into Current Path (dashed navy) and Combined (orange).
  - `pop()` draws the population columns.
  - `ratio()` draws the working-age ratio bar against the 1.7 threshold.
  - `levers()` draws the ranking chart.
  - `dumbbell()` draws the "what changes by 2043" rows.
- **Tabs:** full ARIA tabs that work with the arrow keys. Without JavaScript, every panel shows, one after another.
- **Font:** Open Sans (the Latin variable font from Google Fonts, the same file the site loads, 48 KB), embedded as base64. `unicode-range` covers Latin only.
- **Links:** full URLs to the report's sections with `target="_top"`, so they open in the article window rather than inside the iframe. The section addresses were read from the live page: `#02-current-path`, `#demographics-health`, `#04-comparisons`, `#03-scenarios` and so on.
- **Height message:** the block also sends its height to the page it sits in (`afiGlanceHeight`). This is harmless and only needed if the web team ever adds a resize listener.

**Design choices:**

- White background with thin rules, because the grey Executive Summary panel sits directly underneath.
- The label "Sudan at a glance" is in the site's heading green (`#389d63`). The headline is Open Sans at weight 300, matching the site's H2.
- Colours:
  - navy for the Current Path and history
  - orange for the Combined scenario or the named scenario
  - grey for de-emphasised series
- Text is always in ink colours, never series colours.
- Lines join only the values quoted in the report, and the captions say so.

## 5. How it was tested (repeat this for any new country)

Serve the folder with `python -m http.server`, then load the file in a host page inside an iframe. Playwright was used for this. Check:

- iframe heights 760, 800, 840, 880 and 900
- iframe widths 810, 700, 560, 440, 375, 360, 335 and 320
- every tab at every combination

In each case, check that:

1. the source line at the bottom sits inside the iframe
2. nothing in the open panel runs into the source line
3. each chart's container is at least 150 px tall, and the drawn chart is no taller than its container
4. no two text labels in a chart overlap, and no label falls outside the chart
5. the last scenario row doesn't run into the caption below it
6. there's no sideways scrolling

The final result was **0 problems at 840 and 880 across all widths**. Follow the render-check rules in `CLAUDE.md`: test labels against each other, not just against the edges.

## 6. Problems found on the live Sudan page (not yet reported)

Found while checking the figures, on https://futures.issafrica.org/geographic/countries/sudan/ (IFs v7.38, last updated 15 June 2026, contact: Enoch Randy Aikins):

- **GDP per capita doesn't add up.** The Current Path value for 2043 is US$2 998. The Combined value, US$3 176, is described as "US$792 more than the Current Path", which implies about US$2 384. This is probably a mix of market-rate and purchasing-power figures. GDP per capita was **left out** of the block for this reason.
- **The age shares add up to 101.9%** (57.2% under 15, 41.3% working age, 3.4% over 65). Left out.
- **The displacement figures differ:** "nearly 15 million" in the Current Path section, but "more than 13 million" in the Executive Summary. The block uses about 15 million, from the fuller passage.
- **Typos and slips:**
  - "US$38.9 billion by 20243"
  - "Mali" in the Sudan education paragraph
  - manufacturing "US$439", which is probably US$439 million
  - net crop imports of 12.4% described as "less than" the 7.9% average
- **GDP difference is slightly off:** the Current Path GDP of US$38.9bn plus the stated US$19bn difference gives US$57.9bn, against the US$58.2bn quoted for Combined. This is only rounding.
- **Three Current Path values in the block are worked out, not quoted.** The page only gives the gap to the scenario, so they are marked `*`:
  - life expectancy 68.9 (73.1 − 4.2)
  - adult education 5.9 years (7.6 − 1.7)
  - carbon emissions 8.6 Mt (11.4 ÷ 1.326)

## 7. Next steps

1. **Commit and publish** `sudan-at-a-glance.html`. Check it live at 840 px in a test article, or in a local HTML page with the embed code.
2. **Turn it into a template:** move the Sudan file to `templates/afi-at-a-glance-template.html`. Keep a `DATA` placeholder in the same style as the bar template, which renders with a working default, and add the template to the table in `README.md`. Record the fixed-box approach and the `fit()` order in `docs/`.
3. **Add a check script:** save the test sweep from section 5 as `tools/verify-glance-fit.py`, so every new country is checked the same way.
4. **Next country:** use the same five-tab pattern and change the findings to suit each report. Use only figures quoted on the page. Mark any value you've calculated and list it in the file's notes.
5. **Report the section 6 problems** to the Sudan page owner before the block goes live beside that text.
6. **Later, once the web team is involved:** an OpenCMS content template would let the block sit in the page as real content, with no iframe. That is the fully native option, and it's also indexed by search engines.

## 8. Things to remember

- **Never invent where a figure comes from** (from `CLAUDE.md`). Every number in `DATA` must be quoted on the report page.
- **A published file name is its web address, so it can never change.** Use lower case with hyphens, and put the file in the repo root.
- **Keep the font embedded in the summary blocks.** They must be self-contained. If many *charts* ever embed fonts, a single shared font file in the repo would cache better.
- **The Claude app workspace could not reach Google Fonts, npm, PyPI or the ISS site directly.** The font had to come through the desktop browser. Local VS Code doesn't have that restriction.
