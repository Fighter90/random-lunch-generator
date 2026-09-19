# Random Lunch Generator — A01 artifacts (LLM4Rec, HSE)

Live page: https://sergey-cv.com/random-lunch-generator/
Repository: https://github.com/Fighter90/random-lunch-generator
Report: `emelyanov_sergey_a01_report.pdf` (this folder is reference [8] of the report)

## What was wrong and what was done (one paragraph)

The starter `index.html` from `dryjins/RecSys-LLMs/week1` shows a dish name on every click but an icon only on
some clicks. Three defects: (1) three icon class names — `fa-bowl-hot`, `fa-pasta`, `fa-bowl` — do not exist in the
Font Awesome 6.4.0 stylesheet the page loads, so Ramen, Pasta and Soup never get an icon (3/12 = 25%);
(2) Tacos is drawn as a spoon (`fa-utensil-spoon`) — the icon renders but is wrong; (3) fast repeated clicks
interleave several delayed results. The root cause of (1) is the prompt: it never asked the model to verify icon
names against the library source, so the model invented plausible names. Fixes: correct names + a runtime
`::before` fallback (deployed), Tacos → `fa-pepper-hot` and a `clearTimeout` (regenerated code), and a repaired
prompt that makes source verification the first step.

## Files and where they appear in the report

| File | What it is | Report section |
| --- | --- | --- |
| `index_original.html` | Starter code, verbatim copy of `week1/index.html` [1] | §1, §4 Table 1 rows 1–2, §5 Failure case |
| `index_guard_only.html` | Starter names kept + runtime fallback only (isolates the guard) | §3 Key design decisions, §4 Table 1 row 3 |
| `index_fixed.html` | Three icon names corrected + fallback | §4 Table 1 row 4, §5 Fix, Listing 1 |
| `index.html` | = `index_fixed.html`; the file served by GitHub Pages | §4 Table 1 row 5 (deployed page) |
| `prompt.md` | Original `week1/prompt.md` [1] — contains only the README step | §5 Root cause, "What surprised me" |
| `prompt_fixed.md` | Repaired prompt: verify every icon against `all.min.css` before use, relevance to dish, single random draw, fallback, `clearTimeout` | §3 Key design decisions, §5 Fix (Change 2) |
| `index_regenerated.html` | Code written from `prompt_fixed.md`: verified names, Tacos → `fa-pepper-hot`, `clearTimeout` | §4 Table 1 row 6, §4 rapid-click check |
| `check_icon_classes.py` | Problem 1, static: reads `lunchMenu`, checks every class has a `.fa-NAME:before` rule in the pinned `all.min.css`; exit 1 on a miss (CI-ready) | §4 Table 2, §4 Verification |
| `run_experiment.py` | Problem 1, in the browser: headless Chromium, seeded `Math.random`, N clicks, per-click `::before` check → console table + JSON | §3 Pipeline, §4 Setup |
| `list_dish_icons.py` | Problem 2, semantic: prints dish → icon of several HTML files side by side and marks changes (Tacos: spoon → pepper-hot) — the human check | §5 Root cause, §5 Fix |
| `rapid_click_check.py` | Problem 3, race: 5 clicks within ~300 ms; counts how many results are rendered | §4 Table 2 note, §5 "What surprised me" |
| `requirements.txt` | Pinned test dependency (`playwright==1.63.0`) | §3 Tools & libraries |
| `results/index_original_seed42_n100.json` | Baseline, seed 42: 30/100 failures (Ramen 11, Pasta 8, Soup 11) | Table 1 row 1, Table 2 |
| `results/index_original_seed7_n300.json` | Baseline, seed 7: 67/300 (22.3%) — converges to 3/12 | Table 1 row 2 |
| `results/index_guard_only_seed42_n100.json` | Guard only: 0/100 visible, 30 fallback activations | Table 1 row 3, §4 Verification |
| `results/index_fixed_seed42_n100.json` | Fixed code: 0/100 | Table 1 row 4 |
| `results/live-pages_seed42_n100.json` | Deployed page (sergey-cv.com): 0/100 | Table 1 row 5 |
| `results/index_regenerated_seed42_n100.json` | Regenerated code: 0/100 | Table 1 row 6 |
| `figures/fig1_failure_mechanism.png` | Pipeline diagram: the icon disappears at the CSS lookup step | Figure 1 |
| `figures/fig2_left_original_ramen.png` | Starter code, seed 42, click 1: "Ramen", empty icon box | Figure 2 left |
| `figures/fig2_right_deployed_ramen.png` | Deployed page, same seed, same click: bowl icon | Figure 2 right |

## Reproduce every number

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && playwright install chromium

# Table 1 (arguments: <html or URL> <clicks> <seed> <label>)
python3 run_experiment.py index_original.html    100 42 baseline      # 30/100
python3 run_experiment.py index_original.html    300 7  baseline-300  # 67/300
python3 run_experiment.py index_guard_only.html  100 42 guard-only    # 0/100, 30 console warnings
python3 run_experiment.py index_fixed.html       100 42 fixed         # 0/100
python3 run_experiment.py https://sergey-cv.com/random-lunch-generator/ 100 42 live-pages  # 0/100
python3 run_experiment.py index_regenerated.html 100 42 regen         # 0/100

# Problem 1, static (exit code 1 while any class is missing): 3 missing in original, 0 in fixed/regenerated
python3 check_icon_classes.py index_original.html index_fixed.html index_regenerated.html

# Problem 2, semantic: dish -> icon side by side, Tacos changes from fa-utensil-spoon to fa-pepper-hot
python3 list_dish_icons.py index_original.html index_fixed.html index_regenerated.html

# Problem 3, race-condition check (starter renders 5 results, regenerated renders 1)
python3 rapid_click_check.py index_original.html index_regenerated.html

# Ground truth for "class exists" (Table 2, column "Matches in all.min.css")
curl -sSL -o fa.css https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
for c in pizza-slice fish hamburger leaf utensil-spoon bowl-hot bread-slice pasta mortar-pestle drumstick-bite bowl fire \
         bowl-rice wheat-awn bowl-food pepper-hot; do
  echo "$c: $(grep -o "\.fa-$c[:,{]" fa.css | wc -l)"
done
# expected: bowl-hot 0, pasta 0, bowl 0; every other name 1
```

Hand check used in the report: 11 + 8 + 11 = 30; 30 / 100 = 0.30.
