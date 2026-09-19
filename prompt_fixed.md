# Random Lunch Menu Generator — code-generation prompt (repaired)

## Q: I need to code random lunch menu recsys then publish this into github page. Let's first write the description readme.
(unchanged — see week1/prompt.md)

## Q: Now write index.html. Fix the icon problem by checking the library source, not your memory.

The previous version used icon class names that do not exist in the library. Do not repeat this.

1. Load Font Awesome from exactly one pinned URL and treat it as the single source of truth:
   https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
2. Before you use ANY icon class, verify it against that file: download all.min.css and confirm that a rule
   `.fa-<name>:before{content:"..."}` exists for it. Do not recall icon names from memory and do not
   invent names by analogy (fa-pasta, fa-bowl, fa-bowl-hot do not exist). Print the list of the 12
   verified names with their content codes before writing the HTML.
3. Each icon must be relevant to its dish. If the Free set has no icon for a dish, choose the closest
   food-related one and say so in a comment (e.g. Tacos → fa-pepper-hot); never pad with a random
   utensil. Do not require that icons be unique across dishes — the Free set is too small for that.
4. Keep every dish as one object { name, icon } and select it with ONE Math.random() index, so name and
   icon can never diverge.
5. After inserting the <i>, read getComputedStyle(el, '::before').content; if it is none or empty,
   console.warn and fall back to fas fa-utensils. The user must never see a name without an icon.
6. Store the pending setTimeout id and clearTimeout it on the next click, so that fast repeated clicks
   cannot interleave two results.
7. Keep the existing markup, ids and classes (#generateBtn, .lunch-display, .food-icon, .food-name);
   this is a repair, not a rewrite.

Output: the complete index.html only.
