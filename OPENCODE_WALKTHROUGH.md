# A01 — OpenCode session script (≈ 26 turns, 90–120 min)
# Order: take the repo -> find -> confirm in code -> confirm in browser -> fix code -> fix prompt -> regenerate -> push
# "->" lines are what YOU type after reading the agent's answer. They are the personal steps the rubric looks for.

TERMINAL
  mkdir -p ~/a01 && cd ~/a01 && git clone https://github.com/dryjins/RecSys-LLMs.git
  unzip emelyanov_sergey_a01_starter_kit.zip -d project && cd project
  diff ../RecSys-LLMs/week1/index.html index_original.html && diff ../RecSys-LLMs/week1/prompt.md prompt.md   # both silent
  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && playwright install chromium
  echo ".venv/" > .gitignore && git init && git add -A && git commit -m "A01: starter code from dryjins/RecSys-LLMs week1 + check scripts"
  opencode

── STEP 1  TAKE THE REPO, FIND THE ERRORS ──────────────────────────────────────────────────────────────
T1  Read index_original.html and prompt.md. Explain line by line how a click becomes a dish name and an icon: the handler, where the
    random index is computed, the 500 ms delay, how the <i> is inserted, and which CSS library draws it from which URL.
T2  What does prompt.md actually ask for? Does it contain the request that produced this code? Does it say anything about which icons exist?
    -> The prompt only covers the README; the code came from an unrecorded follow-up. It never asks to verify icon names.
T3  Run: python3 list_dish_icons.py index_original.html. Which icons look wrong for their dish, and which class names look suspicious to you?
    -> Tacos shown as a spoon is a defect of its own (the icon renders but is wrong). Suspicious names: bowl-hot, pasta, bowl.
T4  Give 5 hypotheses why the icon is "sometimes" missing, ranked by likelihood, each with a check under 2 minutes.
T5  Show every Math.random call with line numbers. Is there more than one per click? Is Math.floor(rand * 12) a valid index for 12 items?
    -> One call, indices 0–11. "Two random draws" and "off-by-one" are rejected.
T6  Could it be a network problem? What would the console show if all.min.css failed to load, and would that break some icons or all of them?
    -> A failed stylesheet breaks all icons, not three. Network hypothesis rejected.

── STEP 2  CONFIRM IN CODE (STATIC) ────────────────────────────────────────────────────────────────────
T7  Run: python3 check_icon_classes.py index_original.html. Which classes have no glyph rule in the pinned all.min.css?
    -> bowl-hot, pasta, bowl have no rule.
T8  Show me the actual rule for fa-pizza-slice in the downloaded CSS, and grep all three missing names raw so we have a second independent check.
    -> .fa-pizza-slice:before{content:"\f818"} exists; the three names return nothing. No rule = nothing drawn, and no error. Expected share 3/12 = 25%.
T9  Would upgrading Font Awesome fix it? Run: python3 check_icon_classes.py index_original.html --fa-version 6.7.2 and again with 7.1.0. Is there an fa-taco anywhere?
    -> Same three missing in 6.7.2 and 7.1.0; no fa-taco. Version bump rejected — the names simply do not exist.

── STEP 3  CONFIRM IN THE BROWSER (DYNAMIC) ────────────────────────────────────────────────────────────
T10 Read run_experiment.py. What does it measure, why does it replace Math.random with a seeded generator, and what exactly counts as "rendered"?
T11 Run: python3 run_experiment.py index_original.html 100 42 baseline. Explain every line of the output.
    -> Hand count: 11 + 8 + 11 = 30 = 30/100. Exactly the three dishes from step 2. Console empty — the failure is silent.
T12 Run: python3 run_experiment.py index_original.html 300 7 baseline-300. Does the rate converge to 25%?
    -> 67/300 = 22.3%, consistent with 3/12.
T13 Run: python3 rapid_click_check.py index_original.html. What happens on five fast clicks and why?
    -> Five interleaved results: each click schedules its own setTimeout and none is cancelled. Defect 3, a race condition.
    (Also open index_original.html in Chrome yourself, click until Ramen, look at Elements/Network in DevTools — no ::before content, CSS 200.)

── STEP 4  FIX THE CODE ────────────────────────────────────────────────────────────────────────────────
T14 Before changing names: create index_guard_only.html from index_original.html, keeping the icon names, and after inserting the <i>
    read getComputedStyle(el, '::before').content; if it is none or empty, console.warn and set the class to 'fas fa-utensils'.
    Run: python3 run_experiment.py index_guard_only.html 100 42 guard-only
    -> 0 visible failures, exactly 30 warnings — the same 30 clicks. The guard hides the defect; it does not fix the data.
T15 Propose replacement icons for Ramen, Pasta and Soup from the 6.4.0 Free set and verify each candidate with grep before proposing it.
    -> (agree or adjust; expected: fa-bowl-rice, fa-wheat-awn, fa-bowl-food)
T16 Create index_fixed.html from index_guard_only.html with exactly those three name changes and nothing else. Show the diff.
    Run: python3 check_icon_classes.py index_fixed.html and python3 run_experiment.py index_fixed.html 100 42 fixed
    -> 0 missing, 0/100, no warnings.
T17 Someone suggested replacing all icons with emoji. Make a scratch copy index_emoji.html to see what that would take, then count the changed lines vs the 3-line fix.
    -> Tens of lines vs three, plus OS-dependent glyphs. Rejected as a rewrite, not a repair. (delete index_emoji.html, do not commit it)

── STEP 5  FIX THE PROMPT, REGENERATE ──────────────────────────────────────────────────────────────────
T18 Write prompt_fixed.md: a code-generation step that (1) pins the Font Awesome 6.4.0 URL; (2) requires downloading all.min.css and
    verifying a glyph rule for EVERY icon before use — no names from memory; (3) requires each icon to be relevant to its dish, closest food
    icon if none exists (Tacos -> fa-pepper-hot), no uniqueness requirement; (4) one {name, icon} object and one Math.random per click;
    (5) ::before fallback to fas fa-utensils; (6) clearTimeout of the pending result on the next click; (7) keep ids and classes — repair, not rewrite.
T19 Now write index_regenerated.html following prompt_fixed.md only. Print the verified icon list with glyph codes before writing the file.
T20 Review your own index_regenerated.html against every numbered item of prompt_fixed.md and report pass/fail per item. Fix anything that fails.
T21 Run: python3 check_icon_classes.py index_regenerated.html; python3 list_dish_icons.py index_original.html index_fixed.html index_regenerated.html;
    python3 run_experiment.py index_regenerated.html 100 42 regen; python3 rapid_click_check.py index_original.html index_regenerated.html
    -> 0 missing; Tacos changed to pepper-hot; 0/100; 5 results -> 1. Defect 3 fixed by clearTimeout.

── STEP 6  PUSH AND DEPLOY ─────────────────────────────────────────────────────────────────────────────
T22 Copy index_fixed.html to index.html. Write README.md: what was wrong, a table of every file and where it is used, and the exact commands
    that reproduce each number. Commit: "A01: three defects, repaired prompt, regenerated code, check scripts, results".
T23 Create a public GitHub repository Fighter90/random-lunch-generator from this folder with gh, push main, enable Pages from main:/ and give me the URL.
    (no gh: create the empty repo on github.com, then "Add remote origin ... and push main"; enable Pages in Settings)
T24 Run: python3 run_experiment.py https://sergey-cv.com/random-lunch-generator/ 100 42 live-pages   (or the URL Pages returned)
    -> 0/100. Open it in a browser, click until Ramen, see the bowl.
T25 Commit results/live-pages_seed42_n100.json and push.
T26 Summarize in 5 bullets what was wrong, what was changed, and what evidence supports each change.
    -> read it critically; this is your draft material for §5, to be rewritten in your own words.

EXPORT (terminal, after Ctrl+C)
  opencode session list --format json | python3 -m json.tool | head -40
  opencode export <sessionID> > emelyanov_sergey_a01_session.json     # '>' to a file, never '|'
  python3 -m json.tool emelyanov_sergey_a01_session.json > /dev/null && echo VALID
SUBMIT  emelyanov_sergey_a01_report.pdf + emelyanov_sergey_a01_session.json
