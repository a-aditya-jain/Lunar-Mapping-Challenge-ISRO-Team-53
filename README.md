# High-Resolution Elemental Mapping of Lunar Surface

## Project Overview

This project presents a systematic approach for high-resolution elemental mapping of the lunar surface using X-ray fluorescence (XRF) data collected from Chandrayaan-2’s CLASS instrument. The solution integrates spectral data with spatial metadata, applies Gaussian fitting, chi-square filtering, and flux integration techniques to analyze XRF line signatures and calculate elemental ratios such as Mg/Si, Al/Si, and Ca/Si. The results are mapped onto a lunar albedo base map and visualized using Python and QGIS.

## Problem Statement

The objective of the project is to process the XRF data from CLASS (Chandrayaan-2’s instrument) to identify elemental abundances of various elements on the lunar surface. The data must be calibrated using XSM solar data and response files (ARF, RMF). After processing, elemental ratios like Mg/Si, Al/Si, and Ca/Si are to be calculated and mapped onto a lunar base map.

## Deliverables

- A catalog of detected XRF lines and their corresponding elements.
- A map showing the coverage of XRF lines on the lunar surface.
- Compositional groups based on elemental ratios.
- Visualization of the best elemental ratios on a lunar map.
- Subpixel resolution maps.

## Dataset

### CLASS Dataset
- **FITS Files**: 8-second spectra observed by the Spectral Calibration Detector (SCD).
- **XML Files**: Contain metadata (latitude, longitude).
- **XSM Data**: Calibrated data of solar flares.
  
### Calibration Data
- **RMF (Response Matrix File)**: A 2048 x 2048 redistribution matrix.
- **ARF (Auxiliary Response Function)**: A 2 x 2048 file giving the effective area as a function of energy.

## Methodology

1. **Data Preprocessing**: FITS files are divided based on solar angles. Files with solar angles > 90° are treated as background files, while those with solar angles < 90° are used for spectral analysis.
2. **Spectral Analysis**:
   - Gaussian fitting is applied to model observed spectral features.
   - Chi-square values are used to assess the goodness of fit, with acceptable values ranging from 0.8 to 2.0.
   - Additional FITS files are merged if chi-square values fall outside the acceptable range.
3. **Background Subtraction**: Background files are used to calibrate the data, and peaks are identified to extract elemental signatures.
4. **Mapping**: Coordinates from the FITS files are mapped using Python and QGIS to create visual representations on the lunar surface.
5. **Line Intensity Ratios**: Calculations are based on flux values of Kα lines of key elements, and ratios are mapped onto the lunar base map.

## Software Tools and Scripts

- **Automation Script**: Automates the data processing pipeline.
- **Compile FITS Script**: Processes FITS files, applies Gaussian fitting, and performs chi-square analysis.
- **Background Adder**: Handles background files by filtering solar angles and merging contiguous files.
- **Find Line Intensity Ratios Script**: Calculates elemental line intensities, ratios, and stores results in a CSV file.

## Mapping and Visualization

- **QGIS**: Used to plot the elemental ratios onto the lunar base map, leveraging the Unified Geologic Map of the Moon.
- **Python**: Libraries such as `rasterio`, `pandas`, `plotly`, and `shapely` are used for geospatial data processing and interactive mapping.
- **Subpixel Mapping**: Overlapping observations allow for subpixel resolution mapping of elemental ratios.

## Results and Inferences

- The project successfully mapped elemental ratios (Mg/Si, Al/Si, and Ca/Si) over the lunar surface.
- Subpixel resolution maps provided enhanced insight into compositional heterogeneity.
- High FeO and MgO concentrations are correlated with darker mare regions, while high Al concentrations indicate brighter highland areas.

## Future Prospects

- Improving the subpixel resolution by reducing the window size from 0.1° to 0.05°.
- Enhancing the visualization of elemental ratios using machine learning techniques like KNN for predicting missing data points.

## References

1. Athiray, P.S., et al. Validation of methodology to derive elemental abundances from X-ray observations on Chandrayaan-1. [doi:10.1016/j.pss.2012.10.003](https://doi.org/10.1016/j.pss.2012.10.003)
2. Narendranath, S., et al. Lunar elemental abundances as derived from Chandrayaan-2. [doi:10.1016/j.icarus.2023.115898](https://doi.org/10.1016/j.icarus.2023.115898)
3. Mithun, N.P.S., et al. Solar X-ray Monitor On Board the Chandrayaan-2 Orbiter. [doi:10.1007/s11207-020-01712-1](https://doi.org/10.1007/s11207-020-01712-1)

