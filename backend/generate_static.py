"""Generates a self-contained index.html with all laundry data embedded."""
import json
from database import SessionLocal, Laundry

db = SessionLocal()
rows = db.query(Laundry).filter(Laundry.excluded == False).order_by(Laundry.reviews_count.desc()).all()
db.close()

data = [{"n": r.name, "a": r.address or "", "c": r.city or "", "rg": r.region or "",
         "lat": r.latitude, "lng": r.longitude, "rt": r.rating, "rv": r.reviews_count or 0,
         "url": r.google_maps_url or "", "ph": r.phone or "", "w": r.website or ""}
        for r in rows]

regions = sorted(set(d["rg"] for d in data if d["rg"]))
cities  = sorted(set(d["c"]  for d in data if d["c"]))

region_opts = "\n".join(f'<option value="{r}">{r}</option>' for r in regions)
city_opts   = "\n".join(f'<option value="{c}">{c}</option>' for c in cities)
data_json   = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

html = """<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lavanderias Self-Service — Portugal</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:#f9fafb;color:#111827}
.wrap{max-width:1280px;margin:0 auto;padding:2rem 1rem}
h1{font-size:1.5rem;font-weight:700}
.sub{font-size:.875rem;color:#6b7280;margin-top:.25rem}
header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:2rem;flex-wrap:wrap;gap:1rem}
.btn{display:inline-flex;align-items:center;gap:.4rem;padding:.5rem .9rem;font-size:.875rem;border-radius:.5rem;cursor:pointer;border:1px solid #e5e7eb;background:#fff;color:#374151;transition:background .15s}
.btn:hover{background:#f3f4f6}
.btn.active{background:#2563eb;color:#fff;border-color:#2563eb}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-bottom:1.5rem}
.stat{background:#fff;border:1px solid #e5e7eb;border-radius:.75rem;padding:1.25rem}
.stat-val{font-size:1.5rem;font-weight:700}
.stat-lbl{font-size:.75rem;color:#6b7280;margin-top:.25rem}
.filters{background:#fff;border:1px solid #e5e7eb;border-radius:.75rem;padding:1rem;margin-bottom:1.5rem;display:flex;flex-wrap:wrap;gap:.75rem;align-items:flex-end}
.filters label{display:flex;flex-direction:column;gap:.25rem;font-size:.8rem;font-weight:500;color:#374151}
.filters select,.filters input{padding:.4rem .6rem;border:1px solid #e5e7eb;border-radius:.5rem;font-size:.875rem;min-width:140px}
.tabs{display:flex;gap:.5rem;margin-bottom:1rem}
.count{font-size:.8rem;color:#6b7280;align-self:center}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:.75rem;overflow:hidden;border:1px solid #e5e7eb;font-size:.875rem}
th{background:#f9fafb;padding:.75rem 1rem;text-align:left;font-weight:600;color:#374151;border-bottom:1px solid #e5e7eb;cursor:pointer;white-space:nowrap}
th:hover{background:#f3f4f6}
td{padding:.65rem 1rem;border-bottom:1px solid #f3f4f6;vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:#f9fafb}
.stars{color:#f59e0b}
a{color:#2563eb;text-decoration:none}
a:hover{text-decoration:underline}
.badge{display:inline-block;padding:.15rem .5rem;border-radius:9999px;font-size:.75rem;background:#dbeafe;color:#1e40af}
#map{height:520px;border-radius:.75rem;border:1px solid #e5e7eb}
.pagination{display:flex;gap:.4rem;align-items:center;justify-content:flex-end;margin-top:1rem;flex-wrap:wrap}
.pg{padding:.3rem .65rem;border:1px solid #e5e7eb;border-radius:.4rem;cursor:pointer;background:#fff;font-size:.875rem}
.pg:hover{background:#f3f4f6}
.pg.on{background:#2563eb;color:#fff;border-color:#2563eb}
@media(max-width:640px){th:nth-child(n+4),td:nth-child(n+4){display:none}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>Lavanderias Self-Service &mdash; Portugal</h1>
      <p class="sub">Ranking por n&uacute;mero de avalia&ccedil;&otilde;es no Google Maps</p>
    </div>
    <button class="btn" onclick="exportCsv()">&#x2B07; CSV</button>
  </header>

  <div class="stats" id="stats"></div>

  <div class="filters">
    <label>Regi&atilde;o
      <select id="fRg" onchange="apply()">
        <option value="">Todas</option>
        REGION_OPTS
      </select>
    </label>
    <label>Cidade
      <select id="fCt" onchange="apply()">
        <option value="">Todas</option>
        CITY_OPTS
      </select>
    </label>
    <label>Nome
      <input id="fSr" type="text" placeholder="Pesquisar..." oninput="apply()">
    </label>
    <label>M&iacute;n. reviews
      <input id="fMr" type="number" placeholder="0" min="0" oninput="apply()">
    </label>
    <button class="btn" onclick="clearF()">Limpar</button>
    <span class="count" id="cnt"></span>
  </div>

  <div class="tabs">
    <button class="btn active" id="tTab" onclick="tab('table')">&#x1F4CB; Tabela</button>
    <button class="btn" id="tMap" onclick="tab('map')">&#x1F5FA; Mapa</button>
  </div>

  <div id="vTable">
    <table>
      <thead><tr>
        <th onclick="sort('n')">Nome &#x21C5;</th>
        <th onclick="sort('c')">Cidade &#x21C5;</th>
        <th onclick="sort('rg')">Regi&atilde;o &#x21C5;</th>
        <th onclick="sort('rt')">&#x2605; &#x21C5;</th>
        <th onclick="sort('rv')">Reviews &#x21C5;</th>
        <th>Telefone</th>
        <th>Links</th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="pagination" id="pag"></div>
  </div>
  <div id="vMap" style="display:none"><div id="map"></div></div>
</div>
<script>
const D=DATA_JSON;
let F=[...D],sk='rv',sa=false,pg=1;
const PP=50;
let mInit=false,lMap,mLayer;

function h(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

function apply(){
  const rg=document.getElementById('fRg').value;
  const ct=document.getElementById('fCt').value;
  const sr=document.getElementById('fSr').value.toLowerCase();
  const mr=parseInt(document.getElementById('fMr').value)||0;
  F=D.filter(l=>(!rg||l.rg===rg)&&(!ct||l.c===ct)&&(!sr||l.n.toLowerCase().includes(sr))&&(l.rv>=mr));
  pg=1; stats(); table(); if(mInit)mapR();
}

function clearF(){
  ['fRg','fCt','fSr','fMr'].forEach(id=>document.getElementById(id).value='');
  apply();
}

function sort(k){
  sa=(sk===k)?!sa:(k==='n'||k==='c'||k==='rg');
  sk=k; table();
}

function stats(){
  let rs=0,rc=0;
  F.forEach(l=>{if(l.rt){rs+=l.rt;rc++;}});
  const avg=rc?(rs/rc).toFixed(2):'&mdash;';
  const br={};F.forEach(l=>{if(l.rg)br[l.rg]=(br[l.rg]||0)+1;});
  const tr=Object.entries(br).sort((a,b)=>b[1]-a[1])[0];
  const top=F[0];
  document.getElementById('stats').innerHTML=
    '<div class="stat"><div class="stat-val">'+F.length+'</div><div class="stat-lbl">Lavanderias</div></div>'+
    '<div class="stat"><div class="stat-val">'+avg+' \u2605</div><div class="stat-lbl">Avalia\u00e7\u00e3o m\u00e9dia</div></div>'+
    '<div class="stat"><div class="stat-val">'+(tr?h(tr[0]):'&mdash;')+'</div><div class="stat-lbl">Top regi\u00e3o ('+(tr?tr[1]:0)+')</div></div>'+
    '<div class="stat"><div class="stat-val" style="font-size:1rem">'+(top?h(top.n.substring(0,28)):'&mdash;')+'</div><div class="stat-lbl">1\u00ba lugar ('+(top?top.rv:0)+' reviews)</div></div>';
  document.getElementById('cnt').textContent=F.length+' resultados';
}

function table(){
  const d=[...F].sort((a,b)=>{
    let va=a[sk]??'',vb=b[sk]??'';
    return typeof va==='string'?(sa?va.localeCompare(vb,'pt'):vb.localeCompare(va,'pt')):(sa?va-vb:vb-va);
  });
  const s=(pg-1)*PP,sl=d.slice(s,s+PP);
  document.getElementById('tbody').innerHTML=sl.map(l=>
    '<tr><td><strong>'+h(l.n)+'</strong><br><small style="color:#6b7280">'+h(l.a)+'</small></td>'+
    '<td>'+h(l.c)+'</td>'+
    '<td><span class="badge">'+h(l.rg)+'</span></td>'+
    '<td>'+(l.rt?'<span class="stars">\u2605</span> '+l.rt:'&mdash;')+'</td>'+
    '<td>'+l.rv.toLocaleString('pt')+'</td>'+
    '<td>'+(l.ph?h(l.ph):'&mdash;')+'</td>'+
    '<td>'+(l.url?'<a href="'+h(l.url)+'" target="_blank">Maps</a>':'')+
    (l.w?' &middot; <a href="'+h(l.w)+'" target="_blank">Web</a>':'')+'</td></tr>'
  ).join('');
  pag(d.length);
}

function pag(tot){
  const ps=Math.ceil(tot/PP);
  if(ps<=1){document.getElementById('pag').innerHTML='';return;}
  const show=new Set([1,ps,pg-1,pg,pg+1].filter(p=>p>=1&&p<=ps));
  let html='<span class="count">P\u00e1gina '+pg+' de '+ps+'</span>',prev=0;
  [...show].sort((a,b)=>a-b).forEach(p=>{
    if(prev&&p-prev>1)html+='<span style="padding:0 .3rem">&hellip;</span>';
    html+='<button class="pg'+(p===pg?' on':'')+'" onclick="gp('+p+')">'+p+'</button>';
    prev=p;
  });
  document.getElementById('pag').innerHTML=html;
}

function gp(p){pg=p;table();scrollTo(0,0);}

function tab(t){
  const it=t==='table';
  document.getElementById('vTable').style.display=it?'':'none';
  document.getElementById('vMap').style.display=it?'none':'';
  document.getElementById('tTab').className='btn'+(it?' active':'');
  document.getElementById('tMap').className='btn'+(!it?' active':'');
  if(!it&&!mInit)mapI();
  if(!it)mapR();
}

function mapI(){
  lMap=L.map('map').setView([39.5,-8.0],6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {attribution:'\u00a9 OpenStreetMap contributors'}).addTo(lMap);
  mLayer=L.layerGroup().addTo(lMap);
  mInit=true;
}

function mapR(){
  mLayer.clearLayers();
  F.forEach(l=>{
    if(!l.lat||!l.lng)return;
    L.marker([l.lat,l.lng]).bindPopup(
      '<b>'+h(l.n)+'</b><br>'+h(l.c)+', '+h(l.rg)+'<br>\u2605 '+(l.rt||'&mdash;')+' &middot; '+l.rv+' reviews'+
      (l.url?'<br><a href="'+h(l.url)+'" target="_blank">Google Maps</a>':'')
    ).addTo(mLayer);
  });
}

function exportCsv(){
  const hdr=['Nome','Cidade','Regi\u00e3o','Morada','Avalia\u00e7\u00e3o','Reviews','Telefone','Website','Google Maps'];
  const rows=F.map(l=>[l.n,l.c,l.rg,l.a,l.rt??'',l.rv,l.ph,l.w,l.url]);
  const csv=[hdr,...rows].map(r=>r.map(v=>'"'+String(v??'').replace(/"/g,'""')+'"').join(',')).join('\n');
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8'}));
  a.download='lavanderias_portugal.csv';a.click();
}

apply();
</script>
</body>
</html>"""

html = html.replace("REGION_OPTS", region_opts).replace("CITY_OPTS", city_opts).replace("DATA_JSON", data_json)

out = "c:/Users/lukas/Documents/lavandaria-market/index.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = len(html.encode("utf-8")) // 1024
print(f"Generated: {out}")
print(f"Size: {size_kb} KB ({len(data)} laundries embedded)")
