#!/usr/bin/env python3
"""Génère index.html pour le site morez-rando."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "randonnees.json"
OUT = Path(__file__).parent / "index.html"

data = json.loads(DATA_FILE.read_text())
randos = data["randonnees"]

DIFF_BADGE = {
    "Facile": ("🟢", "#22c55e"),
    "Modéré": ("🟡", "#f59e0b"),
    "Difficile": ("🔴", "#ef4444"),
}

ACTIVITY_ICONS = {
    "pied": "🥾",
    "vtt": "🚵",
    "ski_de_fond": "⛷️",
    "raquettes": "🎿",
}

ACTIVITY_LABELS = {
    "pied": "Randonnée à pied",
    "vtt": "VTT",
    "ski_de_fond": "Ski de fond",
    "raquettes": "Raquettes",
}

def stars(note):
    full = int(note)
    half = 1 if (note - full) >= 0.3 else 0
    return "★" * full + ("½" if half else "") + f" ({note})"

def card(r, activity):
    icon, color = DIFF_BADGE.get(r["difficulte"], ("⚪", "#888"))
    act_icon = ACTIVITY_ICONS[activity]
    gpx = f'gpx/{r["gpx_file"]}'
    url_btn = ""
    for key in ["komoot_url", "jura_url", "info_url"]:
        if key in r:
            label = "Komoot" if "komoot" in key else "Jura Tourisme" if "jura" in key else "Infos"
            url_btn = f'<a href="{r[key]}" target="_blank" class="btn-link">🔗 {label}</a>'
            break

    pts = ""
    if r.get("points_interet"):
        pts = "<div class='poi'>" + " · ".join(f"📍 {p}" for p in r["points_interet"]) + "</div>"

    saisons = " ".join({
        "printemps": "🌸", "été": "☀️", "automne": "🍂", "hiver": "❄️"
    }.get(s, s) for s in r.get("saisons", []))

    return f"""
    <div class="card" data-activity="{activity}" data-diff="{r['difficulte'].lower()}">
      <div class="card-header">
        <span class="act-badge">{act_icon} {ACTIVITY_LABELS[activity]}</span>
        <span class="diff-badge" style="background:{color}">{icon} {r['difficulte']}</span>
      </div>
      <h3>{r['id']} — {r['nom']}</h3>
      <div class="meta-row">
        <span>📏 <strong>{r['distance_km']} km</strong></span>
        <span>⬆️ <strong>{r['denivele_pos_m']} m</strong></span>
        <span>⏱️ <strong>{r['duree_h']:.1f}h</strong></span>
        <span>🔄 {r['type']}</span>
        <span>{saisons}</span>
      </div>
      <div class="depart">📍 Départ : {r['depart']}</div>
      <p class="desc">{r['description']}</p>
      {pts}
      <div class="card-footer">
        <span class="note">⭐ {stars(r.get('note', 4.0))}</span>
        {url_btn}
        <a href="{gpx}" download class="btn-gpx">📥 GPX</a>
      </div>
    </div>"""

sections = ""
for act, label in ACTIVITY_LABELS.items():
    items = randos.get(act, [])
    if not items:
        continue
    icon = ACTIVITY_ICONS[act]
    cards_html = "\n".join(card(r, act) for r in sorted(items, key=lambda x: x["distance_km"]))
    sections += f"""
  <section id="{act}">
    <h2>{icon} {label} <span class="count">({len(items)} itinéraires)</span></h2>
    <div class="cards-grid">{cards_html}</div>
  </section>"""

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🗺️ Randonnées autour de Morez – Haut-Jura</title>
<style>
  :root {{
    --bg: #0f172a; --card: #1e293b; --border: #334155;
    --text: #e2e8f0; --muted: #94a3b8; --accent: #3b82f6;
    --green: #22c55e; --yellow: #f59e0b; --red: #ef4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; }}
  header {{
    background: linear-gradient(135deg, #1e3a5f, #0f172a);
    padding: 2.5rem 1rem 2rem;
    text-align: center;
    border-bottom: 1px solid var(--border);
  }}
  header h1 {{ font-size: 2rem; margin-bottom: .5rem; }}
  header p {{ color: var(--muted); font-size: 1rem; }}
  .nav-pills {{
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: .5rem; padding: 1.5rem 1rem; background: var(--card);
    border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 10;
  }}
  .nav-pills a {{
    padding: .4rem 1rem; border-radius: 999px; background: var(--border);
    color: var(--text); text-decoration: none; font-size: .9rem;
    transition: background .2s;
  }}
  .nav-pills a:hover {{ background: var(--accent); }}
  .stats-bar {{
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 1.5rem; padding: 1.5rem; background: var(--bg);
    border-bottom: 1px solid var(--border);
  }}
  .stat {{ text-align: center; }}
  .stat-val {{ font-size: 1.8rem; font-weight: 700; color: var(--accent); }}
  .stat-lbl {{ font-size: .8rem; color: var(--muted); }}
  main {{ max-width: 1400px; margin: 0 auto; padding: 2rem 1rem; }}
  section {{ margin-bottom: 3rem; }}
  section h2 {{
    font-size: 1.5rem; margin-bottom: 1.5rem; padding-bottom: .5rem;
    border-bottom: 2px solid var(--accent);
  }}
  .count {{ font-size: 1rem; color: var(--muted); font-weight: 400; }}
  .cards-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.2rem;
  }}
  .card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.2rem;
    transition: transform .15s, border-color .15s;
  }}
  .card:hover {{ transform: translateY(-2px); border-color: var(--accent); }}
  .card-header {{ display: flex; justify-content: space-between; margin-bottom: .6rem; }}
  .act-badge {{ font-size: .8rem; color: var(--muted); }}
  .diff-badge {{
    font-size: .75rem; padding: .2rem .6rem;
    border-radius: 999px; color: #fff; font-weight: 600;
  }}
  .card h3 {{ font-size: 1rem; margin-bottom: .7rem; line-height: 1.3; }}
  .meta-row {{
    display: flex; flex-wrap: wrap; gap: .5rem 1rem;
    font-size: .85rem; margin-bottom: .6rem;
  }}
  .meta-row span {{ color: var(--muted); }}
  .meta-row strong {{ color: var(--text); }}
  .depart {{ font-size: .8rem; color: var(--muted); margin-bottom: .5rem; }}
  .desc {{ font-size: .85rem; color: var(--muted); line-height: 1.5; margin-bottom: .6rem; }}
  .poi {{ font-size: .78rem; color: #64748b; margin-bottom: .8rem; }}
  .card-footer {{
    display: flex; align-items: center; gap: .6rem;
    flex-wrap: wrap; margin-top: .5rem;
    padding-top: .7rem; border-top: 1px solid var(--border);
  }}
  .note {{ font-size: .82rem; color: var(--yellow); flex: 1; }}
  .btn-gpx, .btn-link {{
    padding: .3rem .7rem; border-radius: 6px;
    font-size: .8rem; text-decoration: none; font-weight: 600;
    transition: opacity .15s;
  }}
  .btn-gpx {{ background: var(--green); color: #fff; }}
  .btn-link {{ background: var(--accent); color: #fff; }}
  .btn-gpx:hover, .btn-link:hover {{ opacity: .85; }}
  footer {{
    text-align: center; padding: 2rem;
    color: var(--muted); font-size: .85rem;
    border-top: 1px solid var(--border);
  }}
  @media (max-width: 600px) {{
    header h1 {{ font-size: 1.4rem; }}
    .cards-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<header>
  <h1>🗺️ Randonnées autour de Morez</h1>
  <p>Haut-Jura (39) · Rayon 30 km · {sum(len(v) for v in randos.values())} itinéraires classés</p>
</header>

<nav class="nav-pills">
  <a href="#pied">🥾 À pied</a>
  <a href="#vtt">🚵 VTT</a>
  <a href="#ski_de_fond">⛷️ Ski de fond</a>
  <a href="#raquettes">🎿 Raquettes</a>
</nav>

<div class="stats-bar">
  <div class="stat"><div class="stat-val">{len(randos.get('pied', []))}</div><div class="stat-lbl">🥾 À pied</div></div>
  <div class="stat"><div class="stat-val">{len(randos.get('vtt', []))}</div><div class="stat-lbl">🚵 VTT</div></div>
  <div class="stat"><div class="stat-val">{len(randos.get('ski_de_fond', []))}</div><div class="stat-lbl">⛷️ Ski de fond</div></div>
  <div class="stat"><div class="stat-val">{len(randos.get('raquettes', []))}</div><div class="stat-lbl">🎿 Raquettes</div></div>
  <div class="stat"><div class="stat-val">19</div><div class="stat-lbl">📥 Fichiers GPX</div></div>
  <div class="stat"><div class="stat-val">30km</div><div class="stat-lbl">📍 Rayon Morez</div></div>
</div>

<main>
{sections}
</main>

<footer>
  Sources : Komoot · Visorando · Jura Tourisme · Espace Nordique Jurassien<br>
  GPX générés algorithmiquement — pour tracés exacts utiliser les liens Komoot<br>
  Mis à jour le {data['meta']['derniere_maj']}
</footer>
</body>
</html>"""

OUT.write_text(html, encoding="utf-8")
print(f"✅ index.html généré — {sum(len(v) for v in randos.values())} randonnées")
