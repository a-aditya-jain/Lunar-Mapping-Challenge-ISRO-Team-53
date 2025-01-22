import os
import shutil
from astropy.io import fits
from scipy.optimize import curve_fit
from scipy.stats import chisquare
import numpy as np
import subprocess

# Gaussian fitting function
def three_gaussians(x, a1, b1, c1, a2, b2, c2, a3, b3, c3):
    gauss1 = a1 * np.exp(-(x - b1) ** 2 / (2 * c1 ** 2))
    gauss2 = a2 * np.exp(-(x - b2) ** 2 / (2 * c2 ** 2))
    gauss3 = a3 * np.exp(-(x - b3) ** 2 / (2 * c3 ** 2))
    return gauss1 + gauss2 + gauss3


# Function to perform Gaussian fit and calculate chi-square
def gauss_fit_chi2(channel, count):
    # Mask the data for the 1-2 keV range
    mask = (channel >= 1.0) & (channel <= 2.0)
    x_fit = channel[mask]
    y_fit = count[mask]

    # Initial guesses for the parameters
    initial_guess = [max(y_fit), 1.2, 0.05, max(y_fit) / 2, 1.5, 0.05, max(y_fit) / 3, 1.8, 0.05]

    # Perform curve fitting
    try:
        params, _ = curve_fit(three_gaussians, x_fit, y_fit, p0=initial_guess, maxfev=10000)
        y_fitted = three_gaussians(x_fit, *params)

        # Normalize to ensure comparable sums
        y_fitted_normalized = y_fitted * (np.sum(y_fit) / np.sum(y_fitted))

        # Calculate chi-square
        chi2, _ = chisquare(y_fit, y_fitted_normalized)
    except Exception as e:
        print(f"Error during Gaussian fit: {e}")
        return None

    return chi2


# Function to process a single FITS file
def process_fits_file(fits_file, compiled_folder):
    with fits.open(fits_file) as hdul:
        data = hdul[1].data
        channel = data["channel"] * 13.5 / 1000  # Convert to keV
        count = data["counts"]

        chi2 = gauss_fit_chi2(channel, count)

        if chi2 is None:
            print(f"Failed to fit file: {fits_file}")
            return False, chi2

        print(f"File: {fits_file}, Chi-Square: {chi2}")

        if 0.8 <= chi2 <= 2:
            # Extract timestamp from the filename
            filename = os.path.basename(fits_file)
            start_time = filename.split("_")[3]  # Extract start time (YYYYMMDDThhmmssmse)
            year, month, day = start_time[:4], start_time[4:6], start_time[6:8]

            # Create destination folder
            output_folder = os.path.join(compiled_folder, year, month, day)
            os.makedirs(output_folder, exist_ok=True)

            # Move the file
            shutil.copy(fits_file, output_folder)
            print(f"File {fits_file} moved to {output_folder}")
            return True, chi2

        return False, chi2

# Function to check whether it is night-time (background) or day-time data
def isBG(fits_file):
    with fits.open(fits_file) as hdul:
        header = hdul[1].header
        solar_ang = header["SOLARANG"]

        return solar_ang > 90.0


# Function to merge contiguous FITS files
def add_fits_files(file_list, output_dir, fits_directory):
    combined_start = file_list[0].split("_")[-2]  # Start time of the first file
    combined_end = file_list[-1].split("_")[-1]  # End time of the last file
    combined_name = 'ch2_cla_L1_time_added_' + combined_start + '-' + combined_end

    startTime = combined_start
    startTime = "'"+startTime[0:4]+"-"+startTime[4:6]+"-"+startTime[6:11]+":"+startTime[11:13]+":"+startTime[13:15]+"."+startTime[15:]+"'"
    endTime = combined_end
    endTime = endTime[0:4]+"-"+endTime[4:6]+"-"+endTime[6:11]+":"+endTime[11:13]+":"+endTime[13:15]+"."+endTime[15:18]
    endTime = "'" + endTime + "'"
    startTime = startTime.strip()
    endTime = endTime.strip()

    subprocess.run(f"gdl -e \"CLASS_add_L1_files_time,'{fits_directory}',{startTime},{endTime},'{output_dir}'\"", shell=True) #adding files using the provided adder code

    combined_file_path = os.path.join(output_dir, "L1_ADDED_FILES_TIME")
    combined_file_path = os.path.join(combined_file_path, combined_name)

    return combined_file_path


def main(fits_directory, compiled_folder):
    fits_files = sorted([os.path.join(fits_directory, f) for f in os.listdir(fits_directory) if f.endswith(".fits")])
    for i in fits_files:
        print(i.split('/')[-1])

    i = 0
    while i < len(fits_files):
        fits_file = fits_files[i]

        if isBG(fits_file): #checks if its a bg file and ignores
            i += 1
            continue

        # Try processing a single file
        success, chi2 = process_fits_file(fits_file, compiled_folder)

        if not success and chi2 is not None:
            # Start adding contiguous files
            print(f"Chi-square > 2 for file: {fits_file}, attempting to add contiguous files...")

            batch_files = [fits_file]
            for j in range(i + 1, min(i + 12, len(fits_files))):  # Limit to a maximum of 12 files
                batch_files.append(fits_files[j])
                combined_file = add_fits_files(batch_files, compiled_folder, fits_directory)

                # Try processing the combined file
                success, chi2 = process_fits_file(combined_file, compiled_folder)

                if j+1 < min(i + 12, len(fits_files)) and isBG(fits_files[j+1]): #Break if a bg file comes in between
                    break

                if success:
                    print(f"Successfully processed combined file: {combined_file}")
                    i = j  # Skip to the last file in the batch
                    break

                elif j-i < 10:
                    os.remove(combined_file)

            if not success:
                print(f"Failed to process even after adding up to 12 files: {fits_file}")

        i += 1


# Entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process FITS files with Gaussian fitting and Chi-square check.")
    parser.add_argument("--fits_directory", "-d", required=True, help="Path to directory containing FITS files.")
    parser.add_argument("--compiled_folder", "-c", required=True, help="Path to folder to store compiled FITS files.")

    args = parser.parse_args()

    main(args.fits_directory, args.compiled_folder)
