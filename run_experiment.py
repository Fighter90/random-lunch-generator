"""
Random Lunch Generator — icon rendering experiment.

Loads a given index.html in headless Chromium (with the real Font Awesome CSS from cdnjs),
seeds Math.random (mulberry32) for reproducibility, clicks "Generate Lunch!" N times and
records for every click: dish name, icon class, and whether the glyph actually rendered.

"Rendered" = the <i> element inside .food-icon has a ::before pseudo-element whose
`content` is a non-empty string. Font Awesome draws every icon via `.fa-xxx:before{content:"\\fXXX"}`,
so an unknown class name produces content:none -> nothing visible on screen.

Usage: python3 run_experiment.py <html file> <clicks> <seed> <label>
"""
import sys, json, collections
from pathlib import Path
from playwright.sync_api import sync_playwright

html_file, n_clicks, seed, label = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]

SEED_SCRIPT = f"""
(() => {{
  // mulberry32 PRNG, seed = {seed}; replaces Math.random so runs are reproducible
  let a = {seed} >>> 0;
  Math.random = function() {{
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }};
}})();
"""

CHECK = """
() => {
  const i = document.querySelector('.food-icon i');
  const name = document.querySelector('.food-name').textContent;
  if (!i) return {name, cls: null, content: 'NO_I_ELEMENT', rendered: false};
  const content = getComputedStyle(i, '::before').content;   // e.g. '"\\uf818"' or 'none'
  const rendered = content !== 'none' && content !== '""' && content !== 'normal';
  return {name, cls: i.className, content, rendered};
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.add_init_script(SEED_SCRIPT)
    console_lines = []
    page.on("console", lambda m: console_lines.append(m.text))
    page.goto(html_file if html_file.startswith("http") else Path(html_file).resolve().as_uri())
    page.wait_for_function("document.fonts.status === 'loaded'")
    page.wait_for_timeout(700)  # initial generateRandomLunch() on load uses a 500 ms setTimeout

    rows = []
    for k in range(n_clicks):
        page.click("#generateBtn")
        page.wait_for_timeout(650)
        r = page.evaluate(CHECK)
        r["click"] = k + 1
        rows.append(r)
    browser.close()

fails = [r for r in rows if not r["rendered"]]
per_dish = collections.Counter(r["name"] for r in rows)
per_dish_fail = collections.Counter(r["name"] for r in fails)

print(f"=== {label}: file={html_file} clicks={n_clicks} seed={seed}")
print(f"icon failures: {len(fails)}/{n_clicks} = {len(fails)/n_clicks:.3f}")
print("per dish (shown / icon missing):")
for dish, cnt in sorted(per_dish.items()):
    print(f"  {dish:10s} {cnt:4d} / {per_dish_fail.get(dish, 0):3d}")
if fails:
    print("first failing rows:")
    for r in fails[:3]:
        print("  ", r)
if console_lines:
    print("console:", console_lines[:5])

out = (label if html_file.startswith("http") else Path(html_file).with_suffix("").name) + f"_seed{seed}_n{n_clicks}.json"
Path("results").mkdir(exist_ok=True)
json.dump({"label": label, "file": html_file, "clicks": n_clicks, "seed": seed,
           "failures": len(fails), "rate": len(fails)/n_clicks, "rows": rows},
          open(Path("results")/out, "w"), indent=1)
