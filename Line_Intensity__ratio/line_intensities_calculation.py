import os
import argparse
import numpy as np
import pandas as pd
from astropy.io import fits
from scipy.signal import find_peaks
from scipy.integrate import quad
from xspec import Spectrum
import csv

# Default constants
DEFAULT_RESPONSE_PATH = './ch2_class_pds_release_40_20241129/cla/calibration'  # Calibration files folder
DEFAULT_FILE_PATH = './ch2_class_pds_release_40_20241129/cla/miscellaneous/ch2_class_x2abund_lmodel_v1.0/X2ABUND_LMODEL_V1/data_constants/kalpha_be_density_kbeta.txt'  # Excitation energy file
DEFAULT_CSV_FILE = './line_int_rat.csv'  # Output CSV file
DEFAULT_IGNORE_ERANGE = ["0.9", "4.2"]  # Energy range to ignore
IGNORE_STRING = '0.0-' + DEFAULT_IGNORE_ERANGE[0] + ' ' + DEFAULT_IGNORE_ERANGE[1] + '-**'

def load_element_data(file_path):
    """Load elemental data from the provided file."""
    columns = ['atomic_number', 'kalpha', 'element_name', 'be', 'density', 'kbeta']
    return pd.read_csv(file_path, sep='\t', header=None, names=columns)

def initialize_csv(csv_file, geo_headers, ratio_headers):
    """Initialize the CSV file with the appropriate headers if it doesn't already exist."""
    if not os.path.isfile(csv_file):
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=geo_headers + ratio_headers)
            writer.writeheader()

def process_fits_folder(folder_path, bg_folder_path, response_path, file_path, csv_file):
    """Process FITS files in the given folder and calculate line intensity ratios."""
    
    # Response Path
    os.chdir(response_path)
    
    element_data = load_element_data(file_path)
    
    # Defining geographic and ratio headers for CSV
    elements = ['o', 'na', 'mg', 'al', 'si', 'p', 's', 'cl', 'ar', 'k', 'ca', 'sc', 'ti', 'v', 'cr', 'mn', 'fe', 'co', 'ni', 'cu', 'zn']
    ratio_headers = [f"{el}/si" for el in elements]
    geo_headers = ['V0_lat', 'V0_long', 'V1_lat', 'V1_long', 'V2_lat', 'V2_long', 'V3_lat', 'V3_long']

    initialize_csv(csv_file, geo_headers, ratio_headers)
    
    for file_name in os.listdir(folder_path):
        if not file_name.endswith('.fits'):
            continue  # Skip non-FITS files
        
        class_l1_data = os.path.join(folder_path, file_name)
        bkg_file = os.path.join(bg_folder_path, 'background_allevents.fits')
        
        # Loading spectrum data
        spec_data = Spectrum(class_l1_data, bkg_file, 'class_rmf_v1.rmf', 'class_arf_v1_ohm.arf')
        spec_data.ignore(IGNORE_STRING)
        
        # Extracting energy and count data
        energy_edges = np.array(spec_data.energies)
        counts = np.array(spec_data.values)
        energy_centers = np.mean(energy_edges, axis=1)
        
        # Detecting peaks in the spectrum
        peak_indices, _ = find_peaks(counts)
        peak_energies = energy_centers[peak_indices]
        
        # Calculating flux for each element
        element_flux = {}
        for _, row in element_data.iterrows():
            element = row['element_name']
            kalpha = row['kalpha']
            
            # Finding the closest detected peak to the element's K_alpha energy
            closest_peak_idx = np.argmin(np.abs(peak_energies - kalpha))
            peak_center = peak_energies[closest_peak_idx]
            
            # If the closest peak is beyond the threshold (5 keV) ignore the element
            if abs(peak_center - kalpha) <= 0.5:
                def count_func(e):
                    return np.interp(e, energy_centers, counts)
                
                window = 0.1  # Energy window for integration
                flux, _ = quad(count_func, peak_center - window, peak_center + window)
                element_flux[element] = flux
            else:
                element_flux[element] = 0
        
        # Calculating ratios relative to Si
        si_flux = element_flux.get('si', 0)
        ratios = {f'{element}/si': (flux / si_flux if si_flux > 0 else 0) for element, flux in element_flux.items()}
        
        # Extracting geographic data from the FITS file header
        hdul = fits.open(class_l1_data)
        headers = hdul[1].header
        geo_data = {
            'V0_lat': headers['V0_LAT'],
            'V0_long': headers['V0_LON'],
            'V1_lat': headers['V1_LAT'],
            'V1_long': headers['V1_LON'],
            'V2_lat': headers['V2_LAT'],
            'V2_long': headers['V2_LON'],
            'V3_lat': headers['V3_LAT'],
            'V3_long': headers['V3_LON']
        }
        hdul.close()
        
        # Combining geographic data and intensity ratios into a single row
        data_row = {**geo_data, **ratios}
        
        # Appending the row to the CSV file
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=geo_headers + ratio_headers)
            writer.writerow(data_row)

def main():
    parser = argparse.ArgumentParser(description="Process FITS files for line intensity ratios.")
    parser.add_argument('--fits_folder', type=str, default='./compiled_fits', help="Path to the folder containing FITS files.")
    parser.add_argument('--bg_folder', type=str, default='./compiled_bg', help="Path to the folder containing background files.")
    parser.add_argument('--response_path', type=str, default=DEFAULT_RESPONSE_PATH, help="Path to the calibration files.")
    parser.add_argument('--file_path', type=str, default=DEFAULT_FILE_PATH, help="Path to the excitation energy file.")
    parser.add_argument('--csv_file', type=str, default=DEFAULT_CSV_FILE, help="Path to the output CSV file.")
    
    args = parser.parse_args()
    
    process_fits_folder(args.fits_folder, args.bg_folder, args.response_path, args.file_path, args.csv_file)
    print("Processing complete. Data appended to CSV.")

if __name__ == "__main__":
    main()
