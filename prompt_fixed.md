# Code Generation Brief: Repair the Random Lunch Generator

Repair the existing `index_original.html`. Do not rewrite the page, replace the UI with emoji, or change its visual structure.

## Required Workflow

1. Pin Font Awesome to this exact URL:

   ```text
   https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
   ```

2. Before generating or editing the menu mappings, download that exact `all.min.css` file.

3. Verify every icon class against the downloaded CSS before using it. An icon is verified only when the exact class has a glyph rule with non-empty `content`, such as:

   ```css
   .fa-pizza-slice:before{content:"\\f818"}
   ```

   Check exact class boundaries. Do not accept substring matches such as `fa-bowl` inside `fa-bowl-food`.

4. Do not invent icon names or choose names from memory. If a proposed class is not found in the pinned CSS, reject it and choose another verified class.

## Menu Mapping Rules

- Keep one object per dish in the existing `lunchMenu` array.
- Each object must have exactly this shape:

  ```javascript
  { name: "Dish name", icon: "fas fa-icon-name" }
  ```

- Every icon must be relevant to its dish.
- If Font Awesome 6.4.0 Free has no exact dish icon, use the closest relevant food icon. For example:

  ```javascript
  { name: "Tacos", icon: "fas fa-pepper-hot" }
  ```

- Do not require icons to be unique. Reusing a verified, relevant icon is allowed when it is the best available match.
- Do not use an icon merely because its name sounds plausible; it must pass the downloaded-CSS glyph check.

## Interaction and Randomness Rules

- Keep exactly one `Math.random()` call for each button click.
- Compute the index with the existing menu length:

  ```javascript
  const randomIndex = Math.floor(Math.random() * lunchMenu.length);
  ```

- Do not reroll, retry, or make a second random draw when an icon fails verification or rendering.
- Keep the existing loading state and 500 ms result delay unless a change is required for the timer fix.
- Store the pending result timer in a variable.
- On the next click, call `clearTimeout` on the pending result timer before scheduling the new result.
- Ensure an old pending callback cannot overwrite the result selected by a newer click.

## Runtime Glyph Fallback

After inserting the selected icon `<i>` element, inspect the actual CSS-generated glyph:

```javascript
const iconElement = foodIcon.querySelector('i');
const iconContent = getComputedStyle(iconElement, '::before').content;
```

If the content is `none`, `""`, or an empty string:

1. Log a warning identifying the dish and requested icon class.
2. Replace the icon element's class with:

   ```text
   fas fa-utensils
   ```

The fallback must happen after the `<i>` has been inserted and must not trigger another random selection.

## Repair Constraints

- Keep the existing element IDs, including `generateBtn`.
- Keep the existing CSS class names, including `food-icon`, `food-name`, `lunch-display`, `generate-btn`, and `fade-in`.
- Keep the existing DOM structure, layout, styling, copy, and Font Awesome `<i>`-based rendering approach.
- Make the smallest targeted repair; do not convert the project to a framework, split files, or redesign the page.
- Do not change the dish names unless required to preserve the existing behavior.

## Acceptance Checks

The generated result must satisfy all of the following:

- The stylesheet URL is exactly the pinned Font Awesome 6.4.0 cdnjs URL.
- Every `lunchMenu` icon class has an exact glyph rule in the downloaded `all.min.css`.
- Every selected icon is semantically relevant or the closest verified food-icon substitute.
- There is one `{name, icon}` object per dish.
- There is one `Math.random()` call per click.
- A missing runtime glyph produces a warning and displays `fas fa-utensils` instead.
- A second click cancels the first click's pending result timer.
- Five rapid clicks leave only the final click's result visible.
- Existing IDs and classes remain unchanged.
