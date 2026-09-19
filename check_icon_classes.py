"""
Problem 1 check (static): do all icon classes used in an index.html exist in the Font Awesome build the page loads?

Reads the lunchMenu array from the HTML, downloads (or reads) the pinned all.min.css and looks for a
`.fa-NAME:before{content:"..."}` rule for every class. This is the same check as the grep in README, done in Python
so it can run in CI: exit code 1 if any icon is missing.

Usage: python3 check_icon_classes.py index_original.html [index_fixed.html ...] [--css fa.css] [--fa-version 7.1.0]
  --fa-version checks the same classes against another Font Awesome release on cdnjs (default 6.4.0).
"""
import re, sys, urllib.request

FA_VERSION = sys.argv[sys.argv.index("--fa-version") + 1] if "--fa-version" in sys.argv else "6.4.0"
CSS_URL = f"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{FA_VERSION}/css/all.min.css"

skip = set()
for flag in ("--css", "--fa-version"):
    if flag in sys.argv: skip.add(sys.argv[sys.argv.index(flag) + 1])
args = [a for a in sys.argv[1:] if not a.startswith("--") and a not in skip]
css_path = sys.argv[sys.argv.index("--css") + 1] if "--css" in sys.argv else None
if css_path:
    css = open(css_path, encoding="utf-8").read()
else:
    css = urllib.request.urlopen(CSS_URL).read().decode("utf-8")
    print(f"downloaded {CSS_URL} ({len(css)} bytes)")

def menu(html):
    """[(dish, 'fas fa-xxx'), ...] from the lunchMenu array."""
    return re.findall(r'\{\s*name:\s*"([^"]+)",\s*icon:\s*"([^"]+)"', open(html, encoding="utf-8").read())

def content_code(cls):
    """Return the glyph code for the class or None if no rule exists.
    FA 6.4 writes `.fa-name:before{content:"\\fXXX"}`; FA 6.5+/7 writes `.fa-name{--fa:"\\fXXX"}` — both are handled."""
    name = re.escape(cls.split()[-1])          # 'fas fa-fish' -> 'fa-fish'
    m = re.search(r'(?:^|[,}])(?:\.[\w-]+:before,)*\.' + name + r':before(?:,\.[\w-]+:before)*\{content:"([^"]+)"\}', css)
    if not m:
        m = re.search(r'(?:^|[,}])(?:\.[\w-]+,)*\.' + name + r'(?:,\.[\w-]+)*\{--fa:"([^"]+)"\}', css)
    return m.group(1) if m else None

missing_total = 0
for html in args:
    print(f"\n== {html}")
    print(f"{'dish':10} {'icon class':24} {'rule in all.min.css':22} glyph")
    for dish, cls in menu(html):
        code = content_code(cls)
        status = "present" if code else "MISSING -> nothing drawn"
        print(f"{dish:10} {cls:24} {status:22} {code or '-'}")
        missing_total += code is None
print(f"\nmissing icon classes: {missing_total}")
sys.exit(1 if missing_total else 0)
