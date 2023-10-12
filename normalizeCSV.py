import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

# Define the path to your directory containing CSV files
directory_path = './data/'
output_directory_path = './normalized/'

# Iterate over each CSV file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):
        # Load the CSV file into a DataFrame
        df = pd.read_csv(os.path.join(directory_path, filename))

        # Extract OHLC columns
        ohlc_data = df[['open', 'high', 'low', 'close']]
        timestamp_column = df[['timestamp']]

        # Initialize the Min-Max scaler to normalize to the range 1-100
        scaler = MinMaxScaler(feature_range=(1, 100))

        # Fit and transform the OHLC data
        normalized_ohlc = scaler.fit_transform(ohlc_data)

        # Create a new DataFrame with the normalized data
        normalized_df = pd.DataFrame(normalized_ohlc, columns=[
                                     'Open', 'High', 'Low', 'Close'])
        normalized_df['Timestamp'] = timestamp_column

        # Save the normalized data to a new CSV file in the output directory
        output_filename = os.path.splitext(filename)[0] + '_normalized.csv'
        normalized_df.to_csv(os.path.join(
            output_directory_path, output_filename), index=False)

print("Normalization completed.")
