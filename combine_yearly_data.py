import pandas as pd
import os
import glob

# Folder containing the yearly CSVs
folder_path = "data_combined"

# Collect all CSV files
csv_files = sorted(glob.glob(os.path.join(folder_path, "*stats.csv")))

# Initialize a list to collect DataFrames
df_list = []

# Load and process each file
for file in csv_files:
    year = int(os.path.basename(file)[:4])  # Extract year from filename
    df = pd.read_csv(file, encoding="ISO-8859-1")
    df["Year"] = year
    df_list.append(df)

# Combine all into one DataFrame
combined_df = pd.concat(df_list, ignore_index=True)

# Clean column names
combined_df.columns = combined_df.columns.str.strip().str.replace("ï»¿", "")

# Add HR/PA, K%, BB% columns to match decade view logic
combined_df["HR/PA"] = combined_df["HR"] / combined_df["PA"]
combined_df["K%"] = combined_df["SO"] / combined_df["PA"]
combined_df["BB%"] = combined_df["BB"] / combined_df["PA"]

# Save the fully combined dataset
full_output_path = "data/combined_yearly_stats_all_players.csv"
combined_df.to_csv(full_output_path, index=False)

# Filter for starters only (PA >= 100)
starters_df = combined_df[combined_df["PA"] >= 100]
starters_output_path = "data/combined_yearly_stats_starters_only.csv"
starters_df.to_csv(starters_output_path, index=False)

print(combined_df.head())
