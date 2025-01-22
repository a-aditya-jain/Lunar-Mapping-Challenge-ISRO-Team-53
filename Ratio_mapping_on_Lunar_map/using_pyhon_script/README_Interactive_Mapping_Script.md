
# README: Interactive Mapping Script

## **File Requirements**

### **1. GeoTIFF File**
- A high-resolution raster file used as the background.
- **Parameter**: `tiff_file`
- **Description**: Specify the path to the GeoTIFF file.

### **2. CSV File**
- Contains polygon vertices (`V0_LONGITUDE`, `V0_LATITUDE`, ..., `V3_LATITUDE`) and associated ratio values.
- **Parameter**: `csv_file`
- **Description**: Specify the path to the CSV file.

---

## **Python Environment**
- Ensure Python 3.8 or higher is installed on your system.

---

## **Required Libraries**
The script requires the following libraries:

`rasterio, numpy, pyproj, pandas, plotly, Pillow, shapely`

### **Installing Libraries**
Run the following command in your terminal to install all required libraries:
```bash
pip install rasterio numpy pyproj pandas plotly Pillow shapely
```

---

## **Environment Configuration**
To avoid celestial body mismatch errors, set the following environment variable in the Python script:
```python
os.environ["PROJ_IGNORE_CELESTIAL_BODY"] = "YES"
```
Place this line at the beginning of the script, just after importing the required libraries.

---

## **How to Run the Script**

1. Clone or copy the script to the system.
2. Save the script as a `.py` file, such as `interactive_map.py`.
3. Run the script from the terminal or console:
   ```bash
   python interactive_map.py
   ```
   Replace `interactive_map.py` with the actual name of your script.

---

## **Output**
- An interactive HTML file will be created in the working directory.
- This file can be opened in any modern web browser for visualization.

---

## **Notes**
- This setup is same for plotting of all the ratios on lunar base mapas.
