"""
Decode a raw International Futures (IFs) CSV extract into tidy data + metadata.

IFs extracts share a fixed shape:
  row 0        variable code, repeated once per column   e.g. POPMEDAGE[1]
  row 1        series name per column                    e.g. Algeria, Africa
  rows 2..n    optional blank / annotation rows
  units row    e.g. "Years", "Million", "Billion US$"
  scenario row e.g. "Base", "Current Path"
  data rows    first cell is the year, then one value per column

Row positions are detected, not assumed, so extracts with extra header rows,
several variables or several scenarios still decode.
"""
import csv, json, re, sys
from pathlib import Path

# Extend as new variables appear. Falls back to the raw code.
VARIABLE_LABELS = {
    "POPMEDAGE": ("Median age", "years"),
    "POP":       ("Population", "million"),
    "GDPPCP":    ("GDP per capita (PPP)", "thousand US$"),
    "GDP":       ("GDP", "billion US$"),
    "INFRAELECACC": ("Population with electricity access", "%"),
    "LIFEXP":    ("Life expectancy", "years"),
    "DemogDiv":  ("Demographic dividend", "working-age population per dependant"),
}
# IFs aggregate/grouping names are not countries; they get reference styling.
AGGREGATE_HINTS = ("Afr-", "World", "Africa", "Asia", "Europe", "Americas",
                   "Oceania", "-Income", "OECD", "G7", "BRICS", "Region")

# IFs abbreviates group names. These expansions are confirmed; anything else
# matching a group pattern is flagged rather than guessed at, because a wrong
# expansion is a mislabelled chart and nobody would notice.
SERIES_LABELS = {
    "Afr-SubSahar": "Sub-Saharan Africa",
    "Afr-North":    "North Africa",
    "AU Central":   "Central Africa",
    "AU East":      "East Africa",
    "AU North":     "North Africa",
    "AU South":     "Southern Africa",
    "AU West":      "West Africa",
    "Africa":       "Africa",
    "World":        "World",
}
# Group codes: "Afr-SubSahar" style, and African Union regions "AU North" etc.
GROUP_PATTERN = re.compile(r"^((Afr|Asia|Eur|Amer|Ocean)-|AU\s)", re.I)

def display_name(raw):
    """Return (label, needs_confirmation)."""
    if raw in SERIES_LABELS:
        return SERIES_LABELS[raw], False
    if GROUP_PATTERN.match(raw):
        return raw, True          # an IFs group code we have no verified expansion for
    return raw, False             # a country name — use as-is

def is_year(cell):
    c = (cell or "").strip()
    return bool(re.fullmatch(r"(1[89]|20|21)\d{2}", c))

def decode(path):
    rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
    first_data = next(i for i, r in enumerate(rows) if r and is_year(r[0]))
    header = rows[:first_data]
    body   = [r for r in rows[first_data:] if r and is_year(r[0])]

    ncols = max(len(r) for r in rows)
    def hrow(idx):
        r = header[idx] if idx < len(header) else []
        return [(c or "").strip() for c in r] + [""] * (ncols - len(r))

    codes  = hrow(0)
    names  = hrow(1)
    # units / scenario: the last two non-empty header rows before the data
    filled = [i for i in range(len(header)) if any(hrow(i)[1:])]
    units_row    = hrow(filled[-2]) if len(filled) >= 2 else [""] * ncols
    scenario_row = hrow(filled[-1]) if len(filled) >= 1 else [""] * ncols

    series = []
    for c in range(1, ncols):
        if not names[c]:
            continue
        code = re.sub(r"\[.*?\]", "", codes[c]).strip()
        label, unit = VARIABLE_LABELS.get(code, (code, units_row[c].lower()))
        label_name, needs_confirm = display_name(names[c])
        series.append({
            "column": c,
            "name": label_name,
            "rawName": names[c],
            "needsLabelConfirmation": needs_confirm,
            "variable": code,
            "variableLabel": label,
            "unit": unit or units_row[c].lower(),
            "scenario": scenario_row[c],
            "isAggregate": any(h.lower() in names[c].lower() or names[c].startswith(h)
                               for h in AGGREGATE_HINTS),
        })

    years, values = [], {s["name"]: [] for s in series}
    for r in body:
        years.append(int(r[0].strip()))
        for s in series:
            cell = (r[s["column"]] if s["column"] < len(r) else "").strip()
            values[s["name"]].append(float(cell) if cell not in ("", "-") else None)

    return {
        "years": years,
        "series": series,
        "values": values,
        "variables": sorted({s["variable"] for s in series}),
        "scenarios": sorted({s["scenario"] for s in series if s["scenario"]}),
        "units": sorted({s["unit"] for s in series if s["unit"]}),
    }

if __name__ == "__main__":
    d = decode(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/afi/raw.csv")
    print(f"years        {d['years'][0]}–{d['years'][-1]}  ({len(d['years'])} rows)")
    print(f"variables    {d['variables']}")
    print(f"scenarios    {d['scenarios']}")
    print(f"units        {d['units']}")
    print(f"series       {len(d['series'])}")
    for s in d["series"]:
        v = [x for x in d["values"][s["name"]] if x is not None]
        kind = "aggregate" if s["isAggregate"] else "country"
        warn = "  ?? unverified group code — confirm the label" if s["needsLabelConfirmation"] else ""
        print(f"  {s['name']:<20} {kind:<10} n={len(v):>3}  "
              f"min {min(v):>6.2f}  max {max(v):>6.2f}  "
              f"{d['years'][0]} {v[0]:>6.2f} → {d['years'][-1]} {v[-1]:>6.2f}{warn}")
    miss = {k: sum(1 for x in v if x is None) for k, v in d["values"].items()}
    print("missing values:", {k: n for k, n in miss.items() if n} or "none")
    Path("/home/claude/afi/data.json").write_text(json.dumps(d, indent=1))
    print("\nwrote data.json")
