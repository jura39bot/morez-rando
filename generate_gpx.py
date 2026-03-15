#!/usr/bin/env python3
"""
Génère des fichiers GPX pour les randonnées autour de Morez (Jura)
Les tracés sont générés algorithmiquement basés sur les waypoints réels.
Pour les tracés exacts, utiliser Komoot/Visorando avec les URLs fournies.
"""
import json
import math
import os
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "randonnees.json"
GPX_DIR = Path(__file__).parent / "gpx"
GPX_DIR.mkdir(exist_ok=True)

# Waypoints clés de la région (coordonnées réelles)
WAYPOINTS = {
    "Morez":           (46.5228, 6.0247),
    "Les Rousses":     (46.4740, 6.0620),
    "La Cure":         (46.4655, 6.0892),
    "Prémanon":        (46.4585, 6.0388),
    "Bellefontaine":   (46.5035, 6.0302),
    "Longchaumois":    (46.4468, 5.9625),
    "Lamoura":         (46.3980, 5.9750),
    "Morbier":         (46.5468, 6.0188),
    "Lajoux":          (46.3962, 5.9847),
    "La Dôle":         (46.4323, 6.1001),
    "Roche Blanche":   (46.4900, 6.0920),
    "Noirmont":        (46.4511, 6.1200),
    "Dent Vaulion":    (46.6722, 6.3328),
    "Le Pont":         (46.6722, 6.3328),
    "Bief Chaille":    (46.4510, 6.0450),
    "Fort Rousses":    (46.4760, 6.0590),
    "Lac Rousses":     (46.4800, 6.0520),
    "Roche Bernard":   (46.5100, 6.0380),
    "Crêt Vigoureuse": (46.4100, 5.9900),
}


def haversine(lat1, lon1, lat2, lon2):
    """Distance en km entre deux points GPS."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def generate_loop_points(center_lat, center_lon, distance_km, denivele_m, n_points=40, alt_base=1100):
    """
    Génère une boucle GPS réaliste autour d'un point central.
    Le dénivelé est simulé avec un profil montée/descente progressif.
    """
    radius = distance_km / (2 * math.pi) / 110  # degrés approximatifs
    points = []
    
    for i in range(n_points + 1):
        angle = 2 * math.pi * i / n_points
        # Légère variation pour rendre le tracé plus naturel
        r_var = radius * (1 + 0.15 * math.sin(3 * angle) + 0.08 * math.cos(7 * angle))
        lat = center_lat + r_var * math.cos(angle)
        lon = center_lon + r_var * math.sin(angle) / math.cos(math.radians(center_lat))
        
        # Profil altimétrique : montée progressive puis descente
        progress = i / n_points
        if progress < 0.5:
            alt_gain = denivele_m * (progress * 2) * (1 + 0.1 * math.sin(20 * progress))
        else:
            alt_gain = denivele_m * (1 - (progress - 0.5) * 2) * (1 + 0.1 * math.sin(20 * progress))
        
        altitude = alt_base + alt_gain
        points.append((lat, lon, max(alt_base, altitude)))
    
    return points


def gpx_header(name, desc=""):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="morez-rando"
     xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>{name}</name>
    <desc>{desc}</desc>
    <time>{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}</time>
    <keywords>jura, morez, randonnée, haut-jura</keywords>
    <bounds/>
  </metadata>
  <trk>
    <name>{name}</name>
    <desc>{desc}</desc>
    <trkseg>
"""


def gpx_footer():
    return """    </trkseg>
  </trk>
</gpx>
"""


def gpx_point(lat, lon, alt, time_str=""):
    t = f"\n      <time>{time_str}</time>" if time_str else ""
    return f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}">\n        <ele>{alt:.1f}</ele>{t}\n      </trkpt>\n'


def generate_gpx(rando, alt_base=1100):
    """Génère un fichier GPX pour une randonnée."""
    lat, lon = rando["coordonnees_depart"]
    name = rando["nom"]
    desc = rando.get("description", "")
    distance = rando["distance_km"]
    denivele = rando["denivele_pos_m"]
    gpx_file = GPX_DIR / rando["gpx_file"]
    
    points = generate_loop_points(lat, lon, distance, denivele, n_points=60, alt_base=alt_base)
    
    content = gpx_header(name, desc)
    for lat_p, lon_p, alt_p in points:
        content += gpx_point(lat_p, lon_p, alt_p)
    content += gpx_footer()
    
    gpx_file.write_text(content, encoding="utf-8")
    return gpx_file.name


def main():
    data = json.loads(DATA_FILE.read_text())
    randos = data["randonnees"]
    total = 0
    
    print("🗺️  Génération des fichiers GPX — Randonnées Morez Jura\n")
    
    for rando in randos.get("pied", []):
        f = generate_gpx(rando, alt_base=900)
        print(f"  🥾 {rando['id']} — {rando['nom']} → {f}")
        total += 1
    
    for rando in randos.get("vtt", []):
        f = generate_gpx(rando, alt_base=1000)
        print(f"  🚵 {rando['id']} — {rando['nom']} → {f}")
        total += 1
    
    for rando in randos.get("ski_de_fond", []):
        f = generate_gpx(rando, alt_base=1050)
        print(f"  ⛷️  {rando['id']} — {rando['nom']} → {f}")
        total += 1
    
    for rando in randos.get("raquettes", []):
        f = generate_gpx(rando, alt_base=1050)
        print(f"  🎿 {rando['id']} — {rando['nom']} → {f}")
        total += 1
    
    print(f"\n✅ {total} fichiers GPX générés dans {GPX_DIR}/")


if __name__ == "__main__":
    main()
