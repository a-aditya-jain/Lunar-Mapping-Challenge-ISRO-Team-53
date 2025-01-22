
# Sub-Pixel Mapping with GeoTIFF and CSV Data

This task visualizes sub-pixel data from a CSV file overlaid on a GeoTIFF raster file. The resulting map highlights grid cell values with a color scale for easy analysis.

## Requirements

The code requires the following Python libraries:

- `os`
- `pandas`
- `rasterio`
- `shapely`
- `geopandas`
- `matplotlib`

Install these libraries using `pip` if they are not already installed.

## Inputs

1. **GeoTIFF File**: A raster file used as the base map. Specify its path in `tiff_file`:
   ```python
   tiff_file = r"Path to Geo-tiff file"
   ```
   
2. **CSV File**: Contains sub-pixel data with the following columns:
   - `latitude`: Latitude of the grid cell center.
   - `longitude`: Longitude of the grid cell center.
   - `avg_ratio`: Value associated with the grid cell.

   Specify its path in `csv_file`:
   ```python
   csv_file = r"Path to CSV file"
   ```

## Features

- **Raster Visualization**: Displays the GeoTIFF raster as the base map using `rasterio`.
- **Grid Cell Overlay**: Each CSV row represents a grid cell visualized as a polygon on the map.
- **Dynamic Coloring**: The `avg_ratio` values determine the color of grid cells using the `autumn_r` colormap.
- **Coordinate Labels**: Custom hardcoded labels for latitude and longitude axes.
- **Color Bar**: A vertical color bar provides context for the `avg_ratio` values.

## Code Explanation

1. **Environment Setup**: 
   - Ignores celestial body mismatches in projections using `os.environ`.

2. **GeoTIFF Loading**:
   - The GeoTIFF raster is loaded and displayed using `rasterio`.

3. **CSV Data Processing**:
   - Data is read using `pandas`.
   - Grid cell polygons are created using `shapely`.

4. **GeoDataFrame Creation**:
   - A `geopandas` GeoDataFrame stores the polygons and their associated values.
   - Reprojection ensures compatibility with the GeoTIFF CRS.

5. **Visualization**:
   - The GeoTIFF and grid cells are plotted together using `matplotlib`.
   - A colorbar reflects the range of `avg_ratio` values.

6. **Output**:
   - The resulting map is saved as a PNG file:
     ```python
     output_file = "subpixel_map.png"
     ```

## Output

The generated map includes:
- The base GeoTIFF raster.
- Overlaid polygons representing grid cells with non-zero `ratio` values.
- A colorbar indicating the range of values.
