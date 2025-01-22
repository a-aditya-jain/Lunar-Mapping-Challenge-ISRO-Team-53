import pandas as pd

# File paths
input_csv = r"D:\subpixelmap\subpixel_resolutions.csv"  # Path to your input CSV
output_csv = r"D:\subpixelmap\filtered_subpixel_resolutions.csv"  # Path for the filtered CSV

# Read the input CSV file
data = pd.read_csv(input_csv)

# Filter rows where 'mg/si_avg' is not zero
filtered_data = data[data['mg/si_avg'] != 0]

# Save the filtered data to a new CSV file
filtered_data.to_csv(output_csv, index=False)

print(f"Filtered data saved successfully to: {output_csv}")
