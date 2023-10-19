import pandas as pd
import os

# Directory where CSV files are located
dir_path = "results"
all_files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]

# Create a list to store dataframes
dfs = []

# Read each CSV file, add a new column for the currency name, and append it to the list
for file in all_files:
    # Extract currency name from the filename
    currency_name = file.split('_')[0]

    file_path = os.path.join(dir_path, file)
    df = pd.read_csv(file_path)
    df = df[(df['Profit'] > 0) & (df['Profitable Orders'] > df['Loss Orders'])]
    # Add a new column 'currency' to the dataframe and assign the currency_name to all its rows
    df['currency'] = currency_name
    dfs.append(df)

# Concatenate all dataframes in the list
merged_df = pd.concat(dfs, ignore_index=True)

# Save the merged dataframe to a new CSV file
merged_df.to_csv(os.path.join(dir_path, "merged.csv"), index=False)

print("All CSV files have been merged into 'merged.csv' with currency names added.")
