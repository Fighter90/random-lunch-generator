"""Race-condition check: 5 clicks within ~300 ms; how many results get rendered?
Starter code renders all 5 in succession (flicker); the regenerated code renders only the last one.
Usage: python3 rapid_click_check.py index_original.html index_regenerated.html
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
SEED = """(()=>{let a=42>>>0;Math.random=function(){a=(a+0x6D2B79F5)>>>0;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};})();"""
OBS = """()=>{window.__changes=[];const t=document.querySelector('.food-name');
new MutationObserver(()=>{if(t.textContent!=='Thinking...')window.__changes.push(t.textContent)}).observe(t,{childList:true,characterData:true,subtree:true});}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for f in sys.argv[1:]:
        pg = b.new_page(); pg.add_init_script(SEED); pg.goto(Path(f).resolve().as_uri()); pg.wait_for_timeout(800)
        pg.evaluate(OBS)
        for _ in range(5):
            pg.click("#generateBtn"); pg.wait_for_timeout(60)
        pg.wait_for_timeout(900)
        print(f, "results rendered after 5 fast clicks:", pg.evaluate("window.__changes"))
        pg.close()
    b.close()
