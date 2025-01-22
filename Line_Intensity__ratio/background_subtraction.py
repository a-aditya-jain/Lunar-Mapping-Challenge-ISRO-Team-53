import os
import shutil
from astropy.io import fits
from scipy.optimize import curve_fit
from scipy.stats import chisquare
import numpy as np
import subprocess

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

    subprocess.run(f"gdl -e \"CLASS_add_L1_files_time,'{fits_directory}',{startTime},{endTime},'{output_dir}'\"", shell=True) # combining using the provided adder code

    combined_file_path = os.path.join(output_dir, "L1_ADDED_FILES_TIME")
    combined_file_path = os.path.join(combined_file_path, combined_name)
    return combined_file_path


def main(fits_directory, compiled_folder):
    fits_files = sorted([os.path.join(fits_directory, f) for f in os.listdir(fits_directory) if f.endswith(".fits")])

    i = 0
    while i < len(fits_files):
        fits_file = fits_files[i]
        batch_files = [fits_file]

        while isBG(fits_files[i]):
            batch_files.append(fits_files[i])
            i += 1
        
        combined_file = add_fits_files(batch_files, compiled_folder, fits_directory)
        i += 1


# Entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process FITS files with Gaussian fitting and Chi-square check.")
    parser.add_argument("--fits_directory", "-d", required=True, help="Path to directory containing FITS files.")
    parser.add_argument("--compiled_folder", "-c", required=True, help="Path to folder to store compiled FITS files.")

    args = parser.parse_args()

    main(args.fits_directory, args.compiled_folder)
