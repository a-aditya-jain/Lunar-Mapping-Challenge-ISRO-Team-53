import os
import pandas as pd
import rasterio
from rasterio.plot import show
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# Set environment variable to ignore celestial body mismatches
os.environ["PROJ_IGNORE_CELESTIAL_BODY"] = "YES"

# Load the GeoTIFF file
tiff_file = r"D:\subpixelmap\WAC_GLOBAL_E000N0000_032P.PYR.tif"  # Replace with your GeoTIFF file path
with rasterio.open(tiff_file) as src:
    geotiff_crs = src.crs
    fig, ax = plt.subplots(figsize=(12, 10))
    show(src, ax=ax)

    # Hardcode the x-axis and y-axis labels
    x_ticks = ax.get_xticks()
    y_ticks = ax.get_yticks()

    # Generate matching hardcoded labels
    x_labels = [-180 + i * 360 / (len(x_ticks) - 1) for i in range(len(x_ticks))]
    y_labels = [-90 + i * 180 / (len(y_ticks) - 1) for i in range(len(y_ticks))]

    ax.set_xticklabels([f"{x:.0f}" for x in x_labels])
    ax.set_yticklabels([f"{y:.0f}" for y in y_labels])

# Load the CSV file
csv_file = r"D:\subpixelmap\filtered_subpixel_resolutions.csv"  # Replace with your CSV file path
data = pd.read_csv(csv_file)

# Create polygons for grid cells based on the CSV data
polygons = []
values = []
half_size = 0.05  # Half of the 0.1° grid

for _, row in data.iterrows():
    lat, lon = row['latitude'], row['longitude']
    value = row['mg/si_avg']
    
    # Skip grid cells with zero values
    if value == 0:
        continue

    # Define corners of the square based on the center
    corners = [
        (lon - half_size, lat - half_size),
        (lon + half_size, lat - half_size),
        (lon + half_size, lat + half_size),
        (lon - half_size, lat + half_size),
    ]
    polygon = Polygon(corners)
    polygons.append(polygon)
    values.append(value)

# Create a GeoDataFrame for the polygons
gdf = gpd.GeoDataFrame({'value': values, 'geometry': polygons}, crs="EPSG:4326")

# Reproject the GeoDataFrame to match the GeoTIFF CRS, if needed
if geotiff_crs != gdf.crs:
    gdf = gdf.to_crs(geotiff_crs)

# Normalize values for coloring
norm = Normalize(vmin=min(values), vmax=max(values)- 0.1)
cmap = plt.cm.autumn_r

# Plot polygons on the GeoTIFF map
gdf.plot(ax=ax, column='value', cmap=cmap, alpha=0.5, legend=False,
         norm=norm, edgecolor=None)

# Add a colorbar
sm = ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Only needed for colorbar
cbar = plt.colorbar(sm, ax=ax, orientation="vertical", shrink=0.7)
cbar.set_label('mg/si')

# Finalize and save
output_file = "mg_by_si_subpixel_map.png"  # Change this as needed
plt.title("Sub-Pixel Resolution of mg/si")
plt.tight_layout()
plt.savefig(output_file, dpi=300)
print(f"Map saved to {output_file}")
plt.show()
