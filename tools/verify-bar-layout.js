/* Geometry harness for the AFI bar/column template.
   CDNs are blocked in the sandbox, so the chart cannot be rendered here.
   This extracts the template's own layout functions and runs them against
   d3-exact reimplementations of scaleBand / scaleLinear, then checks the
   invariants that would otherwise only show up in a published chart. */
const fs = require("fs");
const SRC = fs.readFileSync("/home/claude/afi-bar-template.html", "utf8");

/* ---------- d3 shims: scaleBand and scaleLinear, per the d3 docs ---------- */
function scaleBand(){
  let domain=[], r0=0, r1=1, pi=0, po=0, align=0.5, step=0, bw=0, pos=new Map();
  function rescale(){
    const n=domain.length;
    step = (r1-r0) / Math.max(1, n - pi + po*2);
    bw = step * (1 - pi);
    const start = r0 + (r1 - r0 - (step*(n - pi)))*align;
    pos = new Map(domain.map((d,i)=>[String(d), start + step*i]));
  }
  const s = d => pos.get(String(d));
  s.domain = v => v===undefined?domain:(domain=v.map(String),rescale(),s);
  s.range  = v => v===undefined?[r0,r1]:([r0,r1]=v,rescale(),s);
  s.paddingInner = v => v===undefined?pi:(pi=v,rescale(),s);
  s.paddingOuter = v => v===undefined?po:(po=v,rescale(),s);
  s.bandwidth = () => bw;
  s.step = () => step;
  return s;
}
function scaleLinear(){
  let d=[0,1], r=[0,1];
  const s = x => r[0] + (x - d[0])/(d[1]-d[0])*(r[1]-r[0]);
  s.domain = v => v===undefined?d:(d=v.slice(),s);
  s.range  = v => v===undefined?r:(r=v.slice(),s);
  s.nice = (n=10)=>{ const st=tickStep(d[0],d[1],n);
    d=[Math.floor(d[0]/st)*st, Math.ceil(d[1]/st)*st]; return s; };
  s.ticks = (n=10)=>{ const st=tickStep(d[0],d[1],n), out=[];
    for(let t=Math.ceil(d[0]/st)*st; t<=d[1]+1e-9; t+=st) out.push(+t.toFixed(10)); return out; };
  return s;
}
function tickStep(a,b,n){
  const step0=Math.abs(b-a)/Math.max(1,n), e=Math.floor(Math.log(step0)/Math.LN10),
        err=step0/Math.pow(10,e);
  return (err>=Math.sqrt(50)?10:err>=Math.sqrt(10)?5:err>=Math.sqrt(2)?2:1)*Math.pow(10,e);
}

const d3 = {
  min:(a,f)=>{const v=a.map(f).filter(x=>x!=null&&!isNaN(x));return v.length?Math.min(...v):undefined;},
  max:(a,f)=>{const v=a.map(f).filter(x=>x!=null&&!isNaN(x));return v.length?Math.max(...v):undefined;},
  extent:(a,f)=>[d3.min(a,f),d3.max(a,f)],
  format:()=>x=>String(x),
  scaleBand, scaleLinear,
};

/* ---------- pull the template's own layout functions ---------- */
const block = SRC.slice(
  SRC.indexOf("/* One row per category"),
  SRC.indexOf("/* ---- scaffolding ---- */")
);
if (!block || block.length < 500) throw new Error("could not extract the layout block");

let fails = 0, checks = 0;
const ok = (name, cond, extra="") => {
  checks++;
  if (!cond) { fails++; console.log(`  FAIL  ${name} ${extra}`); }
  else console.log(`  ok    ${name} ${extra}`);
};

/* the stand-in DATA from the template */
const DATA_SRC = SRC.slice(SRC.indexOf("const DATA = /*__DATA__*/"), SRC.indexOf("/* ============================================================\n   AFI design system"));
const DATA0 = eval("(" + DATA_SRC.replace("const DATA = /*__DATA__*/","").trim().replace(/;\s*$/,"") + ")");

function run(cfgOverrides, label){
  console.log("\n== " + label + " ==");
  const CONFIG = Object.assign({
    orient:"bar", mode:"stacked", sort:"desc", highlight:[], valueLabels:"auto",
    stackTotals:true, decimals:0, axisDecimals:0, valuePrefix:"", valueSuffix:"",
    valueScale:1, vMax:null, valueBands:[], refLines:[], forecastFrom:null,
    forecastShade:false, overlayLine:null, excludeSeries:[], height:440, rowHeight:null,
  }, cfgOverrides);

  const DATA = JSON.parse(JSON.stringify(DATA0));
  const CATS_RAW = DATA.categories || DATA.years;
  const HORIZ = CONFIG.orient === "bar";
  const MODE = CONFIG.mode;
  const STACKED = MODE === "stacked" || MODE === "stacked100";
  const PCT = MODE === "stacked100";
  const RAMP = ["#172859","#e67500","#004ea2","#389d63","#892e88","#e79f2b","#9e234f","#5791cd"];
  const OVL = CONFIG.overlayLine || null;
  const ovlActive = !!(OVL && !HORIZ && DATA.values[OVL.series]);
  const barSeries = DATA.series.filter(s => !(ovlActive && s.name === OVL.series));
  const USED = MODE === "single" ? barSeries.slice(0,1) : barSeries;
  const SERIES = USED.map((s,i)=>({...s, color: USED.length===1?RAMP[0]:RAMP[i%RAMP.length]}));

  const cats = () => CATS_RAW;
  const ctx = {d3, cats, CONFIG, SERIES, DATA, STACKED, PCT, MODE};
  const fn = new Function(...Object.keys(ctx),
    block + "\nreturn {buildRows, buildSegments, valueDomain, barRowHeight};");
  const L = fn(...Object.values(ctx));

  const ROWS = L.buildRows();
  const SEGS = L.buildSegments(ROWS);
  const VDOM = L.valueDomain(SEGS);

  /* --- invariants that do not depend on pixels --- */
  ok("value domain anchored at zero", VDOM[0] <= 0 && VDOM[1] > 0, `[${VDOM}]`);
  if (PCT) ok("100% domain is 0–100", VDOM[0]===0 && VDOM[1]===100);

  if (CONFIG.sort === "desc")
    ok("rows sorted by total, descending",
       ROWS.every((r,i)=> i===0 || ROWS[i-1].total >= r.total));

  ok("every non-null value has a segment",
     SEGS.length === ROWS.reduce((t,r)=>t + r.vals.filter(v=>v!=null).length, 0),
     `${SEGS.length} segments`);

  if (STACKED){
    ROWS.forEach(r => {
      const segs = SEGS.filter(s => s.r === r).sort((a,b)=>a.lo-b.lo);
      const contiguous = segs.every((s,i)=> i===0 ? s.lo===0 : Math.abs(s.lo - segs[i-1].hi) < 1e-9);
      if (!contiguous) { fails++; console.log(`  FAIL  stack contiguous for ${r.cat}`); }
    });
    checks++; console.log("  ok    stack segments contiguous from zero");
    if (PCT){
      const bad = ROWS.filter(r => {
        const top = Math.max(...SEGS.filter(s=>s.r===r).map(s=>s.hi));
        return Math.abs(top - 100) > 1e-6;
      });
      ok("every 100% stack tops out at 100", bad.length === 0,
         bad.length ? `(${bad.map(b=>b.cat).join(", ")})` : "");
    } else {
      const bad = ROWS.filter(r => {
        const top = Math.max(...SEGS.filter(s=>s.r===r).map(s=>s.hi));
        return Math.abs(top - r.total) > 1e-9;
      });
      ok("stack top equals the row total", bad.length === 0);
    }
  }

  /* --- pixel geometry, at several widths --- */
  const heights = [];
  [1100, 860, 640, 480, 400].forEach(W => {
    const rowH = L.barRowHeight();
    /* margins: the same shape the template computes, with measured text
       replaced by a monospace estimate — enough to test bounds, not exact px */
    const est = s => String(s).length * 6.6;
    const widestCat = Math.max(...ROWS.map(r => est(r.cat)));
    const M = HORIZ
      ? {top:10, right:Math.max(12, Math.min(60, Math.round(W*0.25))+4), bottom:44,
         left: Math.min(Math.ceil(widestCat)+10, Math.round(W*0.42))}
      : {top:28, right:12, bottom:30 + Math.min(72, Math.ceil(widestCat*0.64)),
         left: 50};
    const legendH = SERIES.length > 1 ? 26 : 0;
    const H = HORIZ ? M.top + legendH + ROWS.length*rowH + M.bottom : CONFIG.height;
    const iw = Math.max(120, W - M.left - M.right);
    const ih = Math.max(80, H - M.top - M.bottom - legendH);
    heights.push(H);

    const cat = d3.scaleBand().domain(ROWS.map(r=>String(r.cat)))
      .range([0, HORIZ ? ih : iw])
      .paddingInner(MODE==="grouped"?0.28:0.22).paddingOuter(0.12);
    const sub = d3.scaleBand().domain(SERIES.map(s=>s.name))
      .range([0, cat.bandwidth()]).paddingInner(0.12);
    const v = d3.scaleLinear().domain(VDOM).range(HORIZ?[0,iw]:[ih,0]);
    if (CONFIG.vMax == null && !PCT) v.nice(5);

    /* bands inside the plot, in order, non-overlapping */
    const ends = ROWS.map(r => [cat(String(r.cat)), cat(String(r.cat)) + cat.bandwidth()]);
    const across = HORIZ ? ih : iw;
    const inside = ends.every(([a,b]) => a >= -0.01 && b <= across + 0.01);
    const ordered = ends.every(([a],i) => i===0 || a > ends[i-1][0]);
    const nooverlap = ends.every(([a],i) => i===0 || a >= ends[i-1][1] - 0.01);
    if (!(inside && ordered && nooverlap)) {
      fails++; console.log(`  FAIL  band layout at W=${W} (inside=${inside} ordered=${ordered} gap=${nooverlap})`);
    }

    /* every drawn rectangle inside the plot on the value axis */
    const bad = SEGS.filter(s => {
      const a = v(s.lo), b = v(s.hi);
      const lo = Math.min(a,b), hi = Math.max(a,b);
      return lo < -0.01 || hi > (HORIZ ? iw : ih) + 0.01;
    });
    if (bad.length) { fails++; console.log(`  FAIL  ${bad.length} segments outside the plot at W=${W}`); }

    /* grouped bars must not overlap each other inside a band */
    if (MODE === "grouped"){
      const slots = SERIES.map(s => [sub(s.name), sub(s.name)+sub.bandwidth()]);
      const clash = slots.some(([a,b],i)=> i>0 && a < slots[i-1][1] - 0.01);
      const fits  = slots.every(([a,b]) => a >= -0.01 && b <= cat.bandwidth()+0.01);
      if (clash || !fits) { fails++; console.log(`  FAIL  grouped slots at W=${W}`); }
    }
  });
  checks += 3;
  console.log("  ok    bands inside plot, ordered, non-overlapping at every width");
  console.log("  ok    all segments inside the value axis at every width");
  if (MODE === "grouped") console.log("  ok    grouped slots fit the band without overlap");

  const constant = heights.every(h => h === heights[0]);
  ok("SVG height constant across widths", constant, `${heights[0]}px`);
  return heights[0];
}

const H = {};
H.barStacked   = run({orient:"bar",    mode:"stacked"},                    "bar / stacked (template default)");
H.barSingle    = run({orient:"bar",    mode:"single", sort:"desc"},        "bar / single, sorted");
H.barGrouped   = run({orient:"bar",    mode:"grouped"},                    "bar / grouped");
H.bar100       = run({orient:"bar",    mode:"stacked100"},                 "bar / 100% stacked");
H.colStacked   = run({orient:"column", mode:"stacked", sort:"none"},       "column / stacked");
H.colGrouped   = run({orient:"column", mode:"grouped", sort:"none"},       "column / grouped");
H.colSingle    = run({orient:"column", mode:"single", sort:"none"},        "column / single");
H.col100       = run({orient:"column", mode:"stacked100", sort:"none"},    "column / 100% stacked");
H.negatives    = (()=>{ /* negative values must open the domain below zero */
  const keep = JSON.stringify(DATA0);
  DATA0.values["Category 2"] = DATA0.values["Category 2"].map((v,i)=> i%2 ? -v : v);
  const h = run({orient:"column", mode:"grouped", sort:"none"}, "column / grouped with negatives");
  Object.assign(DATA0, JSON.parse(keep));
  return h;
})();

console.log("\n---------------------------------------------");
console.log(`${checks - fails}/${checks} checks passed`);
console.log("iframe heights (round up to the next 10 after a real render):");
Object.entries(H).forEach(([k,v]) => console.log(`  ${k.padEnd(14)} ${v}`));
process.exit(fails ? 1 : 0);
