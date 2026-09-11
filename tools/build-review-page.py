#!/usr/bin/env python3
"""Compose the review artifact from the template file itself.

The chart CSS and the chart JS are copied verbatim, so what the reviewer
looks at is byte-identical to what ships. Only the surrounding chrome —
the mode switches, the config readout, the height sweep — is added here.
"""
import re, pathlib

tpl = pathlib.Path("/home/claude/afi-bar-template.html").read_text()
css = re.search(r"<style>(.*?)</style>", tpl, re.S).group(1)
js  = re.search(r"<script>(.*?)</script>", tpl, re.S).group(1)

# the chart markup, lifted from the template so the two cannot drift
chart_markup = re.search(r'<div class="afi">.*?\n</div>', tpl, re.S).group(0)

CHROME_CSS = """
/* ============================================================
   Review chrome. Not part of the template — this is the harness
   the template is inspected in. The chart panel below keeps the
   article's white ground in every theme, because that is the
   ground it is published on.
   ============================================================ */
:root{
  --page:        #eceef2;
  --chrome-ink:  #172859;
  --chrome-mute: #5c6577;
  --chrome-line: #d5d9e0;
  --chrome-card: #f7f8fa;
  --paper-line:  #dfe3e8;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --page:        #0d1420;
    --chrome-ink:  #e7ebf2;
    --chrome-mute: #93a0b5;
    --chrome-line: #263041;
    --chrome-card: #151d2b;
    --paper-line:  #253044;
  }
}
:root[data-theme="dark"]{
  --page:        #0d1420;
  --chrome-ink:  #e7ebf2;
  --chrome-mute: #93a0b5;
  --chrome-line: #26304180;
  --chrome-card: #151d2b;
  --paper-line:  #253044;
}

html,body{background:var(--page)}
body{color:var(--chrome-ink)}

.shell{max-width:1060px; margin:0 auto; padding-block:32px 56px; padding-left:20px; padding-right:20px;
  display:flex; flex-direction:column; gap:22px}

.masthead{display:flex; flex-direction:column; gap:6px}
.masthead h1{font-family:var(--display); font-size:26px; font-weight:400; margin:0;
  letter-spacing:-.01em; text-wrap:balance; color:var(--chrome-ink)}
.masthead p{margin:0; font-size:14px; line-height:1.5; color:var(--chrome-mute); max-width:66ch}

.controls{display:grid; gap:16px 26px; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  padding:16px 18px; border:1px solid var(--chrome-line); border-radius:8px; background:var(--chrome-card)}
.ctl{display:flex; flex-direction:column; gap:7px; min-width:0}
.ctl > span{font-size:10.5px; text-transform:uppercase; letter-spacing:.09em;
  color:var(--chrome-mute); font-weight:600}
.seg{display:flex; flex-wrap:wrap; gap:4px}
.seg button{font:inherit; font-size:12px; line-height:1; padding:7px 11px; cursor:pointer;
  border:1px solid var(--chrome-line); background:transparent; color:var(--chrome-mute);
  border-radius:5px; white-space:nowrap}
.seg button[aria-pressed="true"]{background:#172859; border-color:#172859; color:#fff}
.seg button:disabled{opacity:.38; cursor:not-allowed}
.seg button:focus-visible{outline:2px solid #e67500; outline-offset:2px}
@media (prefers-reduced-motion:no-preference){ .seg button{transition:background .12s, color .12s} }

.note{font-size:12px; color:var(--chrome-mute); margin:0}
.note b{font-weight:600; color:var(--chrome-ink)}

/* The article ground — white in every theme, because that is where it lands.
   The colour has to be restated too: the chrome sets a light body colour for
   the dark page, and anything in the chart that inherits rather than naming
   its own colour (the title does) would take it and vanish on white. */
.paper{background:#ffffff; color:var(--ink);
  border:1px solid var(--paper-line); border-radius:8px;
  padding:22px 26px 18px; max-width:100%; overflow:hidden}
.paper .afi{padding-top:0}
.papercap{display:flex; justify-content:space-between; align-items:baseline; gap:14px;
  flex-wrap:wrap; font-size:11px; color:var(--chrome-mute); margin:0 2px 8px}
.papercap .h{font-variant-numeric:tabular-nums}

.readout{border:1px solid var(--chrome-line); border-radius:8px; background:var(--chrome-card);
  padding:14px 16px; overflow-x:auto}
.readout h2{margin:0 0 8px; font-size:10.5px; text-transform:uppercase; letter-spacing:.09em;
  color:var(--chrome-mute); font-weight:600}
.readout pre{margin:0; font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:12px; line-height:1.65; color:var(--chrome-ink); white-space:pre}

@media (max-width:560px){
  .paper{padding:16px 14px 14px}
  .masthead h1{font-size:22px}
}
"""

CHROME_JS = r"""
/* ============================================================
   Review chrome. Mutates CONFIG/DATA in place and re-runs the
   template's own buildTable() + render() — no second copy of
   the drawing code exists on this page.
   ============================================================ */
(function(){
  const DATASETS = {
    ranking: {
      label: "Ranking",
      title: "Illustrative example — categorical ranking",
      subtitle: "Stand-in data, not a published figure. Eight categories, three series, one missing value. Replace DATA, the title and the source line before this goes near an article.",
      vTitle: "Thousands of people",
      categories: ["Zimbabwe","Mozambique","Lesotho","Malawi","Nigeria",
                   "Democratic Republic of the Congo","Eswatini","Zambia"],
      series: [{name:"Category 1"},{name:"Category 2"},{name:"Category 3"}],
      values: {
        "Category 1": [412,268,191,143, 96, 74, 61, 48],
        "Category 2": [188,121, 84, 77, 63, 41, 29, 22],
        "Category 3": [ 96, 57, 38, 31,null,26, 17, 14],
      },
      sort: "desc", forecastFrom: null, overlay: null,
    },
    series: {
      label: "Time series",
      title: "Illustrative example — time series with a forecast",
      subtitle: "Stand-in data, not a published figure. Sixteen years, four series, forecast from 2025, plus one series carried on a second axis.",
      vTitle: "Gigawatt hours",
      categories: [2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030],
      series: [{name:"Category 1"},{name:"Category 2"},{name:"Category 3"},{name:"Category 4"},{name:"Index"}],
      values: {
        "Category 1":[120,126,131,139,142,138,149,158,166,173,181,190,199,209,219,230],
        "Category 2":[ 88, 92, 97, 99,104,101,110,117,123,129,136,143,151,159,167,176],
        "Category 3":[ 41, 46, 52, 59, 67, 71, 82, 95,109,124,141,160,181,204,229,257],
        "Category 4":[ 33, 32, 31, 31, 30, 28, 29, 28, 27, 26, 26, 25, 24, 23, 22, 21],
        "Index":     [1.9,2.1,2.0,2.3,2.5,2.2,2.7,3.0,3.2,3.4,3.6,3.9,4.1,4.4,4.6,4.9],
      },
      sort: "none", forecastFrom: 2025,
      overlay: {series:"Index", title:"Index (1 = 2010)", decimals:1},
    },
  };

  const state = {
    dataset: "ranking", orient: "bar", mode: "stacked",
    sort: "desc", labels: "auto", forecast: true, overlay: false, highlight: false,
    segments: true,
  };

  const GROUPS = [
    {key:"dataset", label:"Data",        opts:[["ranking","Ranking"],["series","Time series"]]},
    {key:"orient",  label:"Orientation", opts:[["bar","Bar"],["column","Column"]]},
    {key:"mode",    label:"Mode",        opts:[["single","Single"],["grouped","Grouped"],["stacked","Stacked"],["stacked100","100%"]]},
    {key:"sort",    label:"Sort",        opts:[["none","None"],["desc","Largest first"],["asc","Smallest first"]]},
    {key:"labels",  label:"Value labels",opts:[["auto","Auto"],["true","On"],["false","Off"]]},
    {key:"extra",   label:"Devices",     opts:[["forecast","Forecast"],["overlay","Second axis"],["highlight","Highlight"],["segments","Segment labels"]], toggle:true},
  ];

  const bar = document.getElementById("controls");
  GROUPS.forEach(gp => {
    const wrap = document.createElement("div"); wrap.className = "ctl";
    const lab = document.createElement("span"); lab.textContent = gp.label; wrap.appendChild(lab);
    const seg = document.createElement("div"); seg.className = "seg"; seg.dataset.group = gp.key;
    gp.opts.forEach(([val, text]) => {
      const b = document.createElement("button");
      b.type = "button"; b.id = `opt-${gp.key}-${val}`; b.dataset.val = val; b.textContent = text;
      b.addEventListener("click", () => {
        if (gp.toggle) state[val] = !state[val];
        else state[gp.key] = val;
        apply();
      });
      seg.appendChild(b);
    });
    wrap.appendChild(seg); bar.appendChild(wrap);
  });

  const noteEl = document.getElementById("note");
  const hEl    = document.getElementById("hreadout");
  const cfgEl  = document.getElementById("cfgreadout");

  function apply(){
    const ds = DATASETS[state.dataset];
    const timeAxis = state.dataset === "series";

    /* rules the template enforces with a console warning — enforced here so
       the preview never shows a form the house rules disallow */
    /* Gate these at the point of use, never by writing back into `state` —
       zeroing state.forecast on the ranking dataset left it off for good once
       the user switched to the time series. */
    if (timeAxis && state.sort !== "none") state.sort = "none";
    const useOverlay = state.overlay && timeAxis
                       && state.orient === "column" && state.mode !== "stacked100";
    const useForecast = state.forecast && timeAxis;
    const stacked = state.mode === "stacked" || state.mode === "stacked100";
    const useSegments = state.segments && stacked;

    /* swap the data in place — the template holds a const binding to it */
    DATA.categories = ds.categories.slice();
    DATA.series = ds.series.map(s => ({...s}));
    DATA.values = JSON.parse(JSON.stringify(ds.values));

    Object.assign(CONFIG, {
      title: ds.title, subtitle: ds.subtitle, vTitle: ds.vTitle,
      source: "Illustrative data — replace before publishing", sourceUrl: null,
      orient: state.orient, mode: state.mode, sort: state.sort,
      valueLabels: state.labels === "auto" ? "auto" : state.labels === "true",
      highlight: (state.highlight && !timeAxis) ? ["Lesotho","Malawi"] : [],
      forecastFrom: useForecast ? ds.forecastFrom : null,
      forecastShade: true,
      segmentLabels: useSegments,
      overlayLine: useOverlay ? ds.overlay : null,
      excludeSeries: (timeAxis && !useOverlay) ? ["Index"] : [],
      height: 440, rowHeight: null, decimals: timeAxis ? 0 : 0,
    });

    document.getElementById("title").textContent = CONFIG.title;
    document.getElementById("subtitle").textContent = CONFIG.subtitle;

    /* reflect state on the buttons, disabling what does not apply */
    document.querySelectorAll(".seg").forEach(seg => {
      const key = seg.dataset.group;
      seg.querySelectorAll("button").forEach(b => {
        const v = b.dataset.val;
        const on = key === "extra" ? !!state[v] : state[key] === v;
        b.setAttribute("aria-pressed", String(on));
        let off = false;
        if (key === "sort" && timeAxis) off = v !== "none";
        if (v === "forecast") off = !timeAxis;
        if (v === "overlay")  off = !timeAxis || state.orient !== "column" || state.mode === "stacked100";
        if (v === "highlight") off = timeAxis;
        if (v === "segments")  off = !stacked;
        b.disabled = off;
      });
    });

    const msgs = [];
    if (timeAxis) msgs.push("Sorting is off on a time axis — ordering years by size is a lie.");
    if (state.orient === "bar") msgs.push("The second axis is a column device, so it is off here.");
    if (state.mode === "single" && DATA.series.length > 1) msgs.push("Single mode draws the first series only.");
    noteEl.innerHTML = msgs.length ? msgs.map(m => `<b>·</b> ${m}`).join(" ") : "&nbsp;";

    buildTable(); render();
    showHeight();
    cfgEl.textContent = configText();
  }

  function configText(){
    const keys = ["orient","mode","sort","valueLabels","stackTotals","segmentLabels",
                  "segmentLabelFormat","catLines","highlight",
                  "forecastFrom","forecastShade","overlayLine","excludeSeries","height","rowHeight"];
    const lines = keys.map(k => {
      const v = CONFIG[k];
      const s = v === null ? "null"
        : typeof v === "string" ? `"${v}"`
        : Array.isArray(v) ? JSON.stringify(v)
        : typeof v === "object" ? JSON.stringify(v)
        : String(v);
      return `  ${(k + ":").padEnd(16)}${s},`;
    });
    return "const CONFIG = {\n" + lines.join("\n") + "\n};";
  }

  /* Measure after the webfont has settled, not before: a first-load reading
     taken against the fallback face reported a height 350px out. */
  function showHeight(){
    const read = () => {
      const h = Math.ceil(document.querySelector(".afi").getBoundingClientRect().height);
      hEl.textContent = `${h}px at this width`;
    };
    read();
    document.fonts.ready.then(() => setTimeout(read, 60));
  }
  /* and keep it honest as the pane is resized */
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(showHeight, 200); });

  document.getElementById("measure").addEventListener("click", async () => {
    const paper = document.querySelector(".paper");
    const shell = document.querySelector(".shell");
    const afi = document.querySelector(".afi");
    const prev = paper.style.width, prevMax = paper.style.maxWidth;
    shell.style.overflow = "hidden";   /* a 1100px probe must not scroll the page */
    /* .paper is max-width:100%, which silently clamped every probe to the
       container and returned the same height at all eight widths. */
    paper.style.maxWidth = "none";
    const hs = [];
    for (const w of [1100,960,860,760,640,560,480,400]){
      paper.style.width = w + "px";
      render();
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
      hs.push(Math.ceil(afi.getBoundingClientRect().height));
    }
    paper.style.width = prev; paper.style.maxWidth = prevMax;
    shell.style.overflow = ""; render();
    const tallest = Math.ceil(Math.max(...hs) / 10) * 10;
    hEl.textContent = `iframe height ${tallest}px (tallest of ${hs.join(", ")})`;
  });

  /* The template's PNG export writes a blob download. That works on the
     hosted chart; the artifact viewer never grants a page download
     permission, so the button would silently do nothing here. Hide it in
     the preview rather than leave a dead control on the page. */
  const inArtifact = /(^|\.)claude\.ai$|claudeusercontent/.test(location.hostname);
  const dl = document.getElementById("download");
  if (dl && inArtifact){
    dl.hidden = true;
    const cap = document.getElementById("ground");
    if (cap) cap.textContent += " Download PNG is hidden in this preview; it works on the hosted file.";
  }

  apply();
})();
"""

BODY = f"""<title>AFI Bar Chart Template</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600&display=swap">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<style>
{css}
{CHROME_CSS}
</style>

<div class="shell">
  <header class="masthead">
    <h1>AFI bar and column template</h1>
    <p>One template, four modes, two orientations. Every switch below is a <code>CONFIG</code> key —
       the block at the foot of the page is the exact config producing what you see. Stand-in data
       throughout; nothing here is a published figure.</p>
  </header>

  <div class="controls" id="controls"></div>
  <p class="note" id="note">&nbsp;</p>

  <div>
    <div class="papercap">
      <span id="ground">The article ground — white, Open Sans, full width, no max-width.</span>
      <span class="h" id="hreadout"></span>
    </div>
    <div class="paper">
{chart_markup}
    </div>
  </div>

  <div class="controls" style="grid-template-columns:1fr">
    <div class="ctl">
      <span>Iframe height</span>
      <div class="seg"><button type="button" id="measure">Measure across widths</button></div>
    </div>
  </div>

  <div class="readout">
    <h2>Config for this chart</h2>
    <pre id="cfgreadout"></pre>
  </div>
</div>

<script>
{js}
</script>
<script>
{CHROME_JS}
</script>
"""

pathlib.Path("/home/claude/afi-bar-review.html").write_text(BODY)
print("artifact:", len(BODY), "bytes")

# Standalone twin for GitHub Pages: same bytes, wrapped in a real document.
STANDALONE = (
    '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    + BODY.replace("<title>AFI Bar Chart Template</title>",
                   "<title>AFI bar and column template — preview</title>", 1)
        .replace("</style>\n\n<div class=\"shell\">", "</style>\n</head>\n<body>\n\n<div class=\"shell\">", 1)
    + "\n</body>\n</html>\n"
)
pathlib.Path("/home/claude/bar-template-preview.html").write_text(STANDALONE)
print("standalone:", len(STANDALONE), "bytes")
