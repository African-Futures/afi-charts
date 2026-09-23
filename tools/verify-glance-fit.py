"""Render check for an "At a glance" summary block inside a fixed iframe.

Serves the repository locally, embeds the block in a host page as an iframe
(the way OpenCMS embeds it), and checks every tab at every height and width:

  1. the source line sits inside the iframe
  2. nothing in the open panel runs into the source line
  3. each chart box is at least 150px tall, and the drawn chart is no taller
  4. no two text labels in a chart overlap, none falls outside the chart,
     and no drawn line (data or reference; not gridlines) runs through a label
  5. the last scenario row doesn't run into the caption below it, and the
     comparison cards fit their box
  6. there is no sideways scrolling

Usage:
  python tools/verify-glance-fit.py sudan-at-a-glance.html
  python tools/verify-glance-fit.py sudan-at-a-glance.html --heights 760,800,840,880,900

Exits 1 if any case fails. A new block must pass at 840 (the embed height)
and 880. Needs Playwright:  pip install playwright && playwright install chromium
"""
import argparse, functools, http.server, os, socketserver, sys, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDTHS = [810, 700, 560, 440, 375, 360, 335, 320]   # 810 = article column; 320 = 360px phone less margins
HEIGHTS = [840, 880]

CHECK = r"""
() => {
  const P = [], vh = innerHeight, vw = innerWidth, de = document.documentElement;
  if (!de.classList.contains('afi-framed')) P.push('not in framed mode');
  if (vw < 100 || vh < 100) P.push('viewport not real ' + vw + 'x' + vh);
  const foot = document.querySelector('.afi-g-foot');
  const fr = foot.getBoundingClientRect();
  if (fr.bottom > vh + 0.5) P.push('source line below iframe (' + Math.round(fr.bottom) + '>' + vh + ')');
  const panel = document.querySelector('.afi-g-panel:not([hidden])');
  const kids = [...panel.querySelectorAll('*')].filter(e => e.offsetParent !== null && !e.closest('svg'));
  const lowest = Math.max(...kids.map(e => e.getBoundingClientRect().bottom));
  if (lowest > fr.top + 0.5) P.push('panel runs into source line by ' + Math.round(lowest - fr.top) + 'px');
  if (de.scrollWidth > vw + 0.5) P.push('sideways scroll ' + de.scrollWidth);
  for (const c of panel.querySelectorAll('.afi-g-chart')) {
    const cr = c.getBoundingClientRect();
    if (cr.height < 150) P.push(c.dataset.chart + ' box only ' + Math.round(cr.height) + 'px');
    const svg = c.querySelector('svg'); if (!svg) { P.push(c.dataset.chart + ' no svg'); continue; }
    const sr = svg.getBoundingClientRect();
    if (sr.height > cr.height + 1) P.push(c.dataset.chart + ' svg taller than box');
    const t = [...svg.querySelectorAll('text')].map(e => ({s: e.textContent, r: e.getBoundingClientRect()})).filter(o => o.r.width > 0);
    for (const o of t) if (o.r.left < sr.left - 1 || o.r.right > sr.right + 1 || o.r.top < sr.top - 1 || o.r.bottom > sr.bottom + 1)
      P.push(c.dataset.chart + ' label outside: ' + o.s);
    // labels against the drawn lines (data lines and reference lines, not gridlines);
    // white text sits on a mark by design, so it is left out
    const M = svg.getScreenCTM(), segs = [];
    const pt = (x, y) => ({x: M.a * x + M.c * y + M.e, y: M.b * x + M.d * y + M.f});
    for (const el of svg.querySelectorAll('polyline, line')) {
      if ((el.getAttribute('stroke') || '').toLowerCase() === '#d1d2d4') continue;
      const p = el.tagName === 'line'
        ? [pt(+el.getAttribute('x1'), +el.getAttribute('y1')), pt(+el.getAttribute('x2'), +el.getAttribute('y2'))]
        : el.getAttribute('points').trim().split(/\s+/).map(s => s.split(',').map(Number)).map(([x, y]) => pt(x, y));
      for (let k = 1; k < p.length; k++) segs.push([p[k - 1], p[k]]);
    }
    const onMark = e => /fill:\s*#fff/i.test(e.getAttribute('style') || '');
    for (const e of svg.querySelectorAll('text')) {
      if (onMark(e)) continue;
      const r = e.getBoundingClientRect(); if (!r.width) continue;
      const hit = segs.some(([a, b]) => {
        const n = Math.max(2, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y)));
        for (let k = 0; k <= n; k++) {
          const x = a.x + (b.x - a.x) * k / n, y = a.y + (b.y - a.y) * k / n;
          if (x > r.left + 1 && x < r.right - 1 && y > r.top + 1 && y < r.bottom - 1) return true;
        }
        return false;
      });
      if (hit) P.push(c.dataset.chart + ' line through label: ' + e.textContent);
    }
    for (let i = 0; i < t.length; i++) for (let j = i + 1; j < t.length; j++) {
      const a = t[i].r, b = t[j].r;
      if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1)
        P.push(c.dataset.chart + ' overlap: "' + t[i].s + '" / "' + t[j].s + '"');
    }
  }
  const db = panel.querySelector('.afi-g-db');
  if (db) {
    const rows = db.querySelectorAll('.r'), last = rows[rows.length - 1];
    const cap = [...panel.querySelectorAll('.afi-g-cap')].find(e => e.offsetParent && e.getBoundingClientRect().top >= db.getBoundingClientRect().top);
    if (last && cap && last.getBoundingClientRect().bottom > cap.getBoundingClientRect().top + 0.5) P.push('last row runs into caption');
    if (db.scrollHeight > db.clientHeight + 1) P.push('rows overflow list box');
  }
  const cmp = panel.querySelector('.afi-g-cmp');
  if (cmp) {
    if (cmp.scrollHeight > cmp.clientHeight + 1) P.push('cards overflow their box');
    for (const e of cmp.querySelectorAll('.c')) if (e.scrollWidth > e.clientWidth + 1) P.push('card too narrow: ' + e.querySelector('b').textContent);
  }
  return P;
}
"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def ints(s):
    return [int(v) for v in s.split(",") if v.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", help="block to check, relative to the repo root")
    ap.add_argument("--heights", type=ints, default=HEIGHTS, help="iframe heights, comma-separated")
    ap.add_argument("--widths", type=ints, default=WIDTHS, help="iframe widths, comma-separated")
    args = ap.parse_args()
    if not os.path.isfile(os.path.join(ROOT, args.file)):
        sys.exit(f"not found: {args.file} (give the path relative to the repo root)")

    from playwright.sync_api import sync_playwright

    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=ROOT))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}/{args.file.replace(os.sep, '/')}"

    cases = fails = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 1000})
        for h in args.heights:
            for w in args.widths:
                page.set_content(f'<body style="margin:0"><iframe id="f" src="{url}" width="{w}" height="{h}" '
                                 f'frameborder="0" scrolling="no"></iframe></body>')
                page.wait_for_load_state("networkidle")
                frame = page.query_selector("#f").content_frame()
                frame.wait_for_selector(".afi-g-chart svg")
                tabs = frame.locator("[role=tab]")
                for i in range(tabs.count()):
                    tabs.nth(i).click()
                    frame.wait_for_timeout(150)   # tab switch redraws after layout
                    cases += 1
                    problems = frame.evaluate(CHECK)
                    if problems:
                        fails += 1
                        print(f"FAIL  height {h}  width {w}  tab {i + 1}: " + "; ".join(problems))
        browser.close()
    srv.shutdown()

    print(f"{cases - fails}/{cases} cases pass ({args.file}; heights {args.heights}; widths {args.widths})")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
