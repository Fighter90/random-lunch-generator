"""
Problem 2 check (semantic): print the dish -> icon table of one or more index.html files side by side,
so a human can see whether each icon matches its dish (e.g. Tacos -> fa-utensil-spoon in the starter).
This cannot be automated: a wrong-but-existing icon renders perfectly. The script only makes the list visible.

Usage: python3 list_dish_icons.py index_original.html index_fixed.html index_regenerated.html
"""
import re, sys

def menu(html):
    return dict(re.findall(r'\{\s*name:\s*"([^"]+)",\s*icon:\s*"([^"]+)"', open(html, encoding="utf-8").read()))

files = sys.argv[1:]
menus = [menu(f) for f in files]
dishes = list(menus[0].keys())
w = 26
print(f"{'dish':10}" + "".join(f"{f[:w-1]:{w}}" for f in files))
for d in dishes:
    row = f"{d:10}"
    for m in menus:
        cls = m.get(d, "-").replace("fas ", "")
        row += f"{cls:{w}}"
    changed = len({m.get(d) for m in menus}) > 1
    print(row + ("  <- changed" if changed else ""))
