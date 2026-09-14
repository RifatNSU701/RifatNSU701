#!/usr/bin/env python3
"""Generate a dynamic premium language analytics SVG from stats.json."""
import json, math, os
ROOT=os.path.join(os.path.dirname(__file__),"..")
DATA=os.path.join(ROOT,"docs","data","stats.json")
OUT=os.path.join(ROOT,"assets","language-analytics.svg")
COLORS=["#2FD9E8","#FFB84D","#8B7CFF","#54D17A","#FF6B8A","#7FD6FF","#C58CFF","#66E0C2"]

def esc(v): return str(v).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def polar(cx,cy,r,a):
    a=math.radians(a-90); return cx+r*math.cos(a),cy+r*math.sin(a)
def arc(cx,cy,r,s,e):
    x1,y1=polar(cx,cy,r,s); x2,y2=polar(cx,cy,r,e); large=1 if e-s>180 else 0
    return f"M{x1:.2f},{y1:.2f} A{r},{r} 0 {large} 1 {x2:.2f},{y2:.2f}"

def main():
    with open(DATA,encoding="utf-8") as f: data=json.load(f)
    langs=data.get("languages",[])
    if not langs: return
    total=sum(x.get("bytes",0) for x in langs) or 1
    langs=[{"name":x["name"],"percent":x.get("bytes",0)/total*100} for x in langs if x.get("name")]
    top=langs[:8]
    other=sum(x["percent"] for x in langs[8:])
    if other>0: top.append({"name":"Other","percent":other})
    cx,cy,r=180,205,105; angle=0; arcs=[]
    for i,x in enumerate(top):
        sweep=x["percent"]*3.6; end=angle+sweep; c=COLORS[i%len(COLORS)]
        arcs.append(f'<path d="{arc(cx,cy,r,angle,end)}" stroke="{c}" stroke-width="28" fill="none" stroke-linecap="round" class="arc" style="--d:{i*0.08:.2f}s"/>')
        angle=end
    rows=[]; maxp=max(x["percent"] for x in top) or 1
    for i,x in enumerate(top):
        y=112+i*38; c=COLORS[i%len(COLORS)]; w=315*x["percent"]/maxp
        rows.append(f'<text x="390" y="{y+5}" fill="#DCE6EE" font-size="13" font-family="Inter,Segoe UI,sans-serif">{esc(x["name"])}</text><rect x="500" y="{y-7}" width="315" height="10" rx="5" fill="#182630"/><rect x="500" y="{y-7}" width="{w:.1f}" height="10" rx="5" fill="{c}" class="bar" style="--d:{i*0.08:.2f}s"/><text x="858" y="{y+5}" fill="{c}" font-size="12" font-weight="700" text-anchor="end" font-family="Inter,Segoe UI,sans-serif">{x["percent"]:.2f}%</text>')
    legend=[]
    for i,x in enumerate(top[:6]):
        xx=45+(i%3)*105; yy=352+(i//3)*24; c=COLORS[i%len(COLORS)]
        legend.append(f'<circle cx="{xx}" cy="{yy-4}" r="4" fill="{c}"/><text x="{xx+10}" y="{yy}" fill="#7F929F" font-size="10" font-family="Inter,Segoe UI,sans-serif">{esc(x["name"])}</text>')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520" role="img" aria-label="Dynamic GitHub language analytics"><defs><linearGradient id="p" x1="0" x2="1"><stop stop-color="#081016"/><stop offset="1" stop-color="#0D1821"/></linearGradient><filter id="g"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><style>.arc{{animation:in .8s ease-out var(--d) both;filter:url(#g)}}.bar{{transform-origin:500px center;animation:grow .9s cubic-bezier(.2,.8,.2,1) var(--d) both}}.scan{{animation:scan 4s linear infinite}}.pulse{{animation:pulse 2s ease-in-out infinite}}@keyframes in{{from{{opacity:0;stroke-dasharray:0 800}}to{{opacity:1}}}}@keyframes grow{{from{{transform:scaleX(0);opacity:.2}}to{{transform:scaleX(1);opacity:1}}}}@keyframes scan{{from{{transform:translateX(-900px);opacity:0}}15%{{opacity:.7}}85%{{opacity:.7}}to{{transform:translateX(900px);opacity:0}}}}@keyframes pulse{{50%{{opacity:1}}}}</style></defs><rect width="900" height="520" rx="22" fill="#05080B"/><rect x="14" y="14" width="872" height="492" rx="18" fill="url(#p)" stroke="#182731"/><rect x="14" y="14" width="872" height="2" fill="#2FD9E8" class="scan"/><text x="42" y="55" fill="#E9F4F8" font-size="20" font-weight="700" font-family="Inter,Segoe UI,sans-serif">LANGUAGE ANALYTICS</text><text x="42" y="77" fill="#718592" font-size="11" font-family="Inter,Segoe UI,sans-serif">Live repository language distribution · GitHub byte data</text><circle cx="850" cy="51" r="5" fill="#3DDC84" class="pulse"/><text x="835" y="72" fill="#3DDC84" font-size="9" text-anchor="end" font-family="Courier New,monospace">LIVE DATA</text><line x1="42" y1="94" x2="858" y2="94" stroke="#1B2A34"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#182630" stroke-width="28"/>{''.join(arcs)}<circle cx="{cx}" cy="{cy}" r="70" fill="#081016" stroke="#162731"/><text x="{cx}" y="{cy-3}" fill="#E9F4F8" font-size="25" font-weight="700" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif">{top[0]["percent"]:.1f}%</text><text x="{cx}" y="{cy+18}" fill="#718592" font-size="10" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif">{esc(top[0]["name"])} · top</text>{''.join(legend)}<text x="390" y="98" fill="#9FB0BA" font-size="11" font-weight="700" font-family="Inter,Segoe UI,sans-serif">CODE SHARE</text>{''.join(rows)}<line x1="42" y1="468" x2="858" y2="468" stroke="#1B2A34"/><text x="42" y="490" fill="#657884" font-size="10" font-family="Inter,Segoe UI,sans-serif">Automatically regenerated from docs/data/stats.json</text><text x="858" y="490" fill="#657884" font-size="10" text-anchor="end" font-family="Inter,Segoe UI,sans-serif">RifatNSU701</text></svg>'''
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    with open(OUT,"w",encoding="utf-8") as f:f.write(svg)
if __name__=="__main__": main()
