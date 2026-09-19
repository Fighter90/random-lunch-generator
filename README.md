# Random Lunch Generator

This repository contains the A01 random lunch generator, its repair variants, the repaired generation prompt, and the checks used to reproduce the reported results.

Live page: https://sergey-cv.com/random-lunch-generator/

Repository: https://github.com/Fighter90/random-lunch-generator

## What Was Wrong

The starter page displayed a dish name on every click but could display no icon for some dishes. Three Font Awesome 6.4.0 class names were absent from the stylesheet loaded by the page: `fa-bowl-hot`, `fa-pasta`, and `fa-bowl`. They affected Ramen, Pasta, and Soup, respectively, so 3 of 12 entries had missing glyphs and the expected failure rate was 25%. Tacos used `fa-utensil-spoon`, which rendered but was semantically wrong. Finally, every click created an independent 500 ms timer, so rapid clicks rendered several stale results in sequence.

The repair keeps the original page structure and Font Awesome rendering. The fixed variant verifies the missing glyphs at runtime and falls back to `fas fa-utensils`; the regenerated/deployed variant additionally uses relevant verified replacements and cancels the prior pending result on a new click. The deployed `index.html` is byte-identical to `index_regenerated.html`.

## Files

| File | Where it is used |
| --- | --- |
| `.gitignore` | Git working-tree exclusion rules. |
| `README.md` | This artifact inventory and reproduction guide. |
| `OPENCODE_WALKTHROUGH.md` | Project walkthrough and investigation notes. |
| `requirements.txt` | Python test dependency pin, used before running Playwright checks. |
| `prompt.md` | Original request and generated README prompt; used as the prompt-root-cause reference. |
| `prompt_fixed.md` | Analogue of the original `prompt.md`: preserves the original README dialogue and adds the missing verified single-file code request and answer. |
| `index_original.html` | Untouched starter page; baseline for the three defects. |
| `index_guard_only.html` | Starter mappings plus runtime glyph fallback; isolates the guard behavior. |
| `index_fixed.html` | Fixed page with the three missing mappings replaced, distinct Ramen/Soup bowl icons, and the runtime fallback retained. |
| `index.html` | Deployed GitHub Pages entry point; byte-identical to `index_regenerated.html`. |
| `index_regenerated.html` | Page regenerated from `prompt_fixed.md`; uses verified mappings and cancels stale timers. |
| `check_icon_classes.py` | Downloads or reads `all.min.css` and checks exact glyph rules for every menu icon. |
| `list_dish_icons.py` | Prints dish-to-icon mappings side by side for the semantic review. |
| `run_experiment.py` | Runs seeded headless-browser clicks and measures CSS `::before` glyph rendering. |
| `rapid_click_check.py` | Performs five fast clicks and records how many delayed result names appear. |
| `figures/fig1_failure_mechanism.png` | Failure-mechanism diagram used in the report. |
| `figures/fig2_left_original_ramen.png` | Baseline Ramen screenshot showing the missing icon. |
| `figures/fig2_right_deployed_ramen.png` | Fixed/deployed Ramen screenshot showing the icon. |
| `results/index_original_seed42_n100.json` | Baseline 100-click seeded observations. |
| `results/index_original_seed7_n300.json` | Baseline 300-click seeded observations. |
| `results/index_guard_only_seed42_n100.json` | Guard-only observations and fallback-triggering rows. |
| `results/index_fixed_seed42_n100.json` | Fixed-page 100-click observations. |
| `results/index_regenerated_seed42_n100.json` | Regenerated-page 100-click observations. |
| `results/live-pages_seed42_n100.json` | Live deployed-page 100-click observations. |

## Reproduce the Numbers

Set up the Python environment and Playwright browser:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

The baseline 100-click result is 30 failures out of 100:

```bash
python3 run_experiment.py index_original.html 100 42 baseline
# icon failures: 30/100 = 0.300
```

The 300-click baseline is 67 failures out of 300:

```bash
python3 run_experiment.py index_original.html 300 7 baseline-300
# icon failures: 67/300 = 0.223
```

The guard-only page renders a fallback for all missing glyphs and reports zero visible failures:

```bash
python3 run_experiment.py index_guard_only.html 100 42 guard-only
# icon failures: 0/100 = 0.000
# console warnings include the missing Pasta, Ramen, and Soup classes
```

The fixed page reports zero failures:

```bash
python3 run_experiment.py index_fixed.html 100 42 fixed
# icon failures: 0/100 = 0.000
```

The deployed entry point is `index.html`, which is the regenerated page:

```bash
python3 run_experiment.py index.html 100 42 deployed
# icon failures: 0/100 = 0.000
```

The regenerated page also reports zero failures:

```bash
python3 run_experiment.py index_regenerated.html 100 42 regen
# icon failures: 0/100 = 0.000
```

Check the missing classes in the original and the repaired pages. The original reports 3 missing classes; the repaired pages report 0:

```bash
python3 check_icon_classes.py index_original.html
python3 check_icon_classes.py index_fixed.html
python3 check_icon_classes.py index_regenerated.html
```

Compare every dish mapping and see the semantic changes:

```bash
python3 list_dish_icons.py index_original.html index_fixed.html index_regenerated.html
```

The expected mapping changes include `Tacos: fa-utensil-spoon -> fa-pepper-hot`, plus verified replacements for Ramen, Pasta, Curry, Steak, and Soup.

Check the rapid-click race. The original emits five delayed names; the regenerated page emits only the final result:

```bash
python3 rapid_click_check.py index_original.html index_regenerated.html
# original: five names
# regenerated: ['Sandwich']
```

For the exact Font Awesome 6.4.0 source check:

```bash
curl -sSL -o fa.css https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
for c in pizza-slice fish hamburger leaf utensil-spoon bowl-hot bread-slice pasta mortar-pestle drumstick-bite bowl fire bowl-food wheat-awn pepper-hot bacon; do
  echo "$c: $(grep -o "\\.fa-$c[:,{]" fa.css | wc -l)"
done
```

The exact missing original names are `bowl-hot`, `pasta`, and `bowl`; the replacement names used by the repaired pages have glyph rules in the same pinned stylesheet.

## License

The original project is licensed under the MIT License.
