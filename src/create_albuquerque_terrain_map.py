"""
Create geospatial outputs for Albuquerque fatal police shooting locations, 2015-2024.

Outputs:
- GeoJSON point layer in WGS84
- Interactive Folium terrain/topographic HTML map
- Static GeoPandas/Matplotlib point map fallback

Optional static terrain:
Install contextily and uncomment the add_basemap block to draw web tiles in the PNG.
"""
from __future__ import annotations

from pathlib import Path
import html

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster, Fullscreen, MeasureControl

INPUT_CSV = Path("data/albuquerque_incident_detail_2015_2024.csv")
OUTPUT_DIR = Path("outputs/geospatial")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load incident records.
df = pd.read_csv(INPUT_CSV)

# Keep only records with coordinates.
df = df.dropna(subset=["latitude", "longitude"]).copy()
df["incident_date"] = pd.to_datetime(df["incident_date"], errors="coerce")

# Build a GeoDataFrame in standard latitude/longitude coordinates.
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:4326",
)

# Save GeoJSON for reuse in QGIS, Tableau, ArcGIS, Folium, etc.
geojson_path = OUTPUT_DIR / "albuquerque_fatal_police_shootings_2015_2024.geojson"
gdf.to_file(geojson_path, driver="GeoJSON")

# -----------------------------
# Interactive terrain map
# -----------------------------
center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]

m = folium.Map(location=center, zoom_start=11, tiles=None, control_scale=True)

# Terrain/topographic basemap. Loads tiles in the browser, so internet is required when viewing.
folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)",
    name="OpenTopoMap terrain",
    overlay=False,
    control=True,
).add_to(m)

# Add a quieter alternate basemap.
folium.TileLayer(
    tiles="CartoDB positron",
    name="CartoDB Positron",
    overlay=False,
    control=True,
).add_to(m)

cluster = MarkerCluster(name="Fatal police shooting locations").add_to(m)

for _, row in gdf.iterrows():
    apd = bool(row.get("apd_involved", False))
    armed = str(row.get("armed_with", "unknown"))
    color = "red" if apd else "blue"
    icon = "exclamation-sign" if armed == "gun" else "info-sign"

    popup = f"""
    <b>Date:</b> {html.escape(str(row.get('incident_date', ''))[:10])}<br>
    <b>Victim:</b> {html.escape(str(row.get('victim_name', 'Unknown')))}<br>
    <b>Age:</b> {html.escape(str(row.get('age', 'Unknown')))}<br>
    <b>Race label:</b> {html.escape(str(row.get('race_label', 'Unknown')))}<br>
    <b>Armed with:</b> {html.escape(str(row.get('armed_with', 'Unknown')))}<br>
    <b>Threat type:</b> {html.escape(str(row.get('threat_type', 'Unknown')))}<br>
    <b>Flee status:</b> {html.escape(str(row.get('flee_status', 'Unknown')))}<br>
    <b>APD involved:</b> {html.escape(str(row.get('apd_involved', 'Unknown')))}<br>
    <b>Agencies:</b> {html.escape(str(row.get('agencies_involved', 'Unknown')))}
    """

    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=folium.Popup(popup, max_width=420),
        tooltip=f"{row.get('incident_date', '')} | {'APD' if apd else 'Non-APD / multi-agency'}",
        icon=folium.Icon(color=color, icon=icon),
    ).add_to(cluster)

# Add an overall bounding rectangle for quick visual orientation.
bounds = [
    [gdf.geometry.y.min(), gdf.geometry.x.min()],
    [gdf.geometry.y.max(), gdf.geometry.x.max()],
]
folium.Rectangle(
    bounds=bounds,
    color="#333333",
    weight=1,
    fill=False,
    tooltip="Incident coordinate extent",
).add_to(m)

Fullscreen().add_to(m)
MeasureControl(position="topleft", primary_length_unit="miles").add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

html_path = OUTPUT_DIR / "albuquerque_fatal_police_shootings_terrain_map.html"
m.save(html_path)

# -----------------------------
# Static GeoPandas fallback map
# -----------------------------
fig, ax = plt.subplots(figsize=(11, 9))

# Plot APD vs non-APD points. No basemap is added here so this works offline.
gdf.assign(
    apd_label=gdf["apd_involved"].map(
        {True: "APD involved", False: "Other / multi-agency"}
    )
).plot(
    ax=ax,
    column="apd_label",
    categorical=True,
    legend=True,
    markersize=55,
    alpha=0.75,
)

ax.set_title("Albuquerque Fatal Police Shooting Locations, 2015-2024", fontsize=18)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.grid(True, alpha=0.25)

# Optional static terrain tiles using contextily:
# import contextily as cx
# gdf_web = gdf.to_crs(epsg=3857)
# ax.clear()
# gdf_web.plot(ax=ax, column="apd_label", categorical=True, legend=True, markersize=55, alpha=0.75)
# cx.add_basemap(ax, source=cx.providers.OpenTopoMap)
# ax.set_axis_off()

png_path = OUTPUT_DIR / "albuquerque_fatal_police_shootings_geopandas_static.png"
fig.tight_layout()
fig.savefig(png_path, dpi=180)
plt.close(fig)

print(f"Wrote {geojson_path}")
print(f"Wrote {html_path}")
print(f"Wrote {png_path}")
