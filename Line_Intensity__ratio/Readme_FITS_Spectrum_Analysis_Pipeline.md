
# FITS Spectrum Analysis Pipeline

## Overview
The project processes data from the ISRO database for spectral analysis using FITS files. The pipeline consists of three key scripts:

1. **bg_adder.py**: Identifies and merges background FITS files based on solar angle, creating a compiled background dataset.
2. **compile_fits.py**: Filters, merges, and processes non-background daytime FITS files using Gaussian fitting with chi-square evaluation.
3. **line_intensities.py**: Analyzes spectral data by extracting elemental line intensity ratios and geographic data, storing the results in a CSV file.

---

## Prerequisites

### Dependencies
The project requires the following Python libraries:
- **General**: `os`, `shutil`, `subprocess`
- **FITS file processing**: `astropy.io.fits`, `pandas`
- **Numerical and scientific computation**: `numpy`, `scipy`
- **Peak detection**: `scipy.signal`

Additionally, ensure that `gdl` is installed for FITS file merging.

---

## Pipeline Details

### 1. **bg_adder.py: Background File Compilation**
- **Description**: Filters FITS files based on solar angle and merges contiguous background files.
- **Inputs**:
  - `--fits_directory (-d)`: Directory containing FITS files.
  - `--compiled_folder (-c)`: Directory to store merged background files.
- **Outputs**: Merged background files saved in the compiled folder.
- **How to Run**:
  ```bash
  python bg_adder.py -d /path/to/fits/files -c /path/to/compiled_bg
  ```

---

### 2. **compile_fits.py: FITS File Processing**
- **Description**:
  - Processes non-background files by:
    - Performing Gaussian fitting on the 1–2 keV range.
    - Accepting files with chi-square values between 0.8 and 2.
    - Merging contiguous files if necessary.
- **Inputs**:
  - `--fits_directory (-d)`: Directory containing FITS files.
  - `--compiled_folder (-c)`: Directory to store processed files.
- **Outputs**:
  - FITS files passing chi-square criteria are saved in the compiled folder.
  - Merged files for those requiring adjustment are also stored here.
- **How to Run**:
  ```bash
  python compile_fits.py -d /path/to/fits/files -c /path/to/compiled_fits
  ```

---

### 3. **line_intensities.py: Spectrum Analysis**
- **Description**:
  - Analyzes spectral data by:
    - Comparing detected peaks with known elemental excitation energies.
    - Calculating intensity ratios relative to silicon (Si).
    - Extracting geographic data from FITS headers.
- **Inputs**:
  - `--bg`: Directory containing compiled background FITS files.
  - `--fits`: Directory containing compiled processed FITS files.
- **Outputs**:
  - CSV file containing:
    - Geographic coordinates (latitude and longitude).
    - Intensity ratios for detected elements relative to silicon.
- **How to Run**:
  ```bash
  python line_intensities.py --bg ./compiled_bg --fits ./compiled_fits --output results.csv
  ```

---

## Outputs Summary
- **Compiled Backgrounds**: `./compiled_bg` (merged background FITS files).
- **Processed FITS Files**: `./compiled_fits` (chi-square validated files).
- **Results CSV**: Contains geographic data and elemental intensity ratios.

---

**Error Handling**:
  - Files failing Gaussian fitting are logged and skipped.
  - Merging failures are managed by cleaning intermediate files.
**Configuration**:
  - Adjust chi-square thresholds (default: 0.8–2) in `compile_fits.py` for different datasets.
  - Update `ignore_erange` and energy peak tolerances in `line_intensities.py` as needed.

---

## Example Workflow
```bash
# Step 1: Process background files
python bg_adder.py -d /data/raw_fits -c ./compiled_bg

# Step 2: Process non-background files with Gaussian fitting
python compile_fits.py -d /data/raw_fits -c ./compiled_fits

# Step 3: Extract line intensities and geographic data
python line_intensities.py --bg ./compiled_bg --fits ./compiled_fits --output results.csv
```

## Note:
   - The CSV file "coordinate_and_line_intesity_ratio" provided, is for a particular day only.
