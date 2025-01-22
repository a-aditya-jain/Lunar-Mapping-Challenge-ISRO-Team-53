import os
import numpy as np
import rasterio
from pyproj import CRS, Transformer
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import base64
from shapely.geometry import Polygon

# Set the environment variable to ignore celestial body mismatches
os.environ["PROJ_IGNORE_CELESTIAL_BODY"] = "YES"

# Paths to the GeoTIFF and CSV files
tiff_file = r"path to geotiff file"
csv_file = r"path to csv file"

# Define CRS
geotiff_crs = CRS.from_proj4("+proj=eqc +lat_ts=0 +lon_0=0 +a=1737400 +b=1737400 +units=m")
csv_crs = CRS.from_epsg(4326)  # WGS84 for CSV coordinates

# Read and downscale GeoTIFF
with rasterio.open(tiff_file) as src:
    raster = src.read(1)
    raster_min, raster_max = raster.min(), raster.max()
    # Downscale raster for better performance
    downscaled_raster = raster[::4, ::4]  # Reduce resolution by a factor of 4
    raster_normalized = ((downscaled_raster - raster_min) / (raster_max - raster_min) * 255).astype(np.uint8)

# Convert raster to Base64 image
def raster_to_base64(raster_data):
    img = Image.fromarray(raster_data, mode="L")  # Grayscale image
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return "data:image/png;base64," + base64.b64encode(buffer.read()).decode()

raster_image_base64 = raster_to_base64(raster_normalized)

# Read CSV
try:
    df = pd.read_csv(csv_file, encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv(csv_file, encoding="latin1")

# Transform coordinates
transformer = Transformer.from_crs(csv_crs, geotiff_crs, always_xy=True)
polygons, ca_si_values = [], []

for _, row in df.iterrows():
    try:
        longitudes = [float(row[f"V{i}_LONGITUDE"]) for i in range(4)]
        latitudes = [float(row[f"V{i}_LATITUDE"]) for i in range(4)]
        longitudes.append(longitudes[0])
        latitudes.append(latitudes[0])
        x_coords, y_coords = transformer.transform(longitudes, latitudes)
        x_coords_deg = [max(min(x / 1737400 * 180 / np.pi, 180), -180) for x in x_coords]
        y_coords_deg = [max(min(y / 1737400 * 180 / np.pi, 90), -90) for y in y_coords]
        # Simplify polygons using Shapely
        poly = Polygon(zip(x_coords_deg, y_coords_deg)).simplify(0.01)  # Simplify by 0.01 degrees
        if poly.is_valid:
            polygons.append((list(poly.exterior.coords.xy[0]), list(poly.exterior.coords.xy[1])))
            ca_si_values.append(float(row["ca/si"]))  # Use "ca/si" instead of "mg/si"
    except KeyError as e:
        print(f"Error in row: {row}, {e}")

# Normalize ca/si
ca_si_min, ca_si_max = min(ca_si_values), max(ca_si_values)

# Precompute colors for polygons
color_map = [
    f"rgba({255 * (1 - (val - ca_si_min) / (ca_si_max - ca_si_min)):.0f}, "
    f"{255 * (1 - abs(0.5 - (val - ca_si_min) / (ca_si_max - ca_si_min)) * 2):.0f}, "
    f"{255 * ((val - ca_si_min) / (ca_si_max - ca_si_min)):.0f}, 0.8)"
    for val in ca_si_values
]

# Create figure
fig = go.Figure()

# Add GeoTIFF as a background
fig.add_layout_image(
    dict(
        source=raster_image_base64,
        x=-180,
        y=90,
        xref="x",
        yref="y",
        sizex=360,
        sizey=180,
        xanchor="left",
        yanchor="top",
        layer="below",
    )
)

# Add simplified polygons with hover information
for (x_coords_deg, y_coords_deg), color, ca_si in zip(polygons, color_map, ca_si_values):
    a = sum(x_coords_deg[:-1]) / len(x_coords_deg[:-1])  # Average longitude
    b = sum(y_coords_deg[:-1]) / len(y_coords_deg[:-1])  # Average latitude
    fig.add_trace(
        go.Scatter(
            x=x_coords_deg,
            y=y_coords_deg,
            fill="toself",
            hoverinfo="text",
            text=f"ca/si: {ca_si}<br> Longitude: {a:.2f}<br> Latitude: {b:.2f}",
            line=dict(color="black", width=0.5),
            fillcolor=color,
            marker=dict(opacity=0),
            opacity=0.8,
        )
    )

# Add a calibrated color ramp
fig.add_trace(
    go.Scatter(
        x=[None],  # Dummy x value
        y=[None],  # Dummy y value
        mode="markers",
        marker=dict(
            size=10,
            color=np.linspace(ca_si_min, ca_si_max, 100),  # Simulate color values
            colorscale="Turbo_r",  # Same colorscale as polygons
            cmin=ca_si_min,
            cmax=ca_si_max,
            colorbar=dict(
                title="ca/si",
                titleside="right",
                tickvals=[ca_si_min, (ca_si_min + ca_si_max) / 2, ca_si_max],
                ticktext=[f"{ca_si_min:.2f}", f"{(ca_si_min + ca_si_max) / 2:.2f}", f"{ca_si_max:.2f}"],
                len=0.6,  # Height of the colorbar
                thickness=20,  # Width of the colorbar
                x=1.1,  # Position to the right of the plot
                y=0.5,  # Centered vertically
            ),
        ),
        hoverinfo="none"  # No hover for the color ramp
    )
)

# Update layout with dynamic zoom
fig.update_layout(
    title="ca_si_ratio_map",
    xaxis=dict(title="Longitude (degrees)", range=[-180, 180], autorange=False, fixedrange=False),
    yaxis=dict(title="Latitude (degrees)", range=[-90, 90], autorange=False, fixedrange=False, scaleanchor="x"),
    hovermode="closest",
    showlegend=False,
    dragmode="pan",  # Enables interactive dragging and zooming
    margin=dict(l=50, r=50, t=50, b=50),  # Add margins for better visual appeal
)

# Save interactive map without lasso and box select
fig.write_html(
    "ca_by_si_interactivePlot.html",
    include_plotlyjs=True,
    full_html=True,
    config={"scrollZoom": True, "displayModeBar": True, "modeBarButtonsToRemove": ["select2d", "lasso2d"]},
)
print("Interactive map saved as 'ca_by_si_interactivePlot.html'. Open this file in your browser.")
