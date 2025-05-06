# preprocess_scats.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import argparse

def load_and_clean_data(csv_path):
    # Load CSV
    df = pd.read_csv(csv_path)

    # Drop rows with missing Date
    df = df[df['Date'].notna()]

    # Fix column names
    df.columns = df.columns.str.strip()

    # Extract only needed columns
    meta_cols = ['SCATS Number', 'Location', 'NB_LATITUDE', 'NB_LONGITUDE', 'Date']
    vol_cols = [f'V{i:02d}' for i in range(96) if f'V{i:02d}' in df.columns]
    
    df = df[meta_cols + vol_cols]

    # Melt into long format
    df_long = df.melt(id_vars=meta_cols, value_vars=vol_cols,
                      var_name='Interval', value_name='Volume')

    # Map interval to minutes
    df_long['Minutes'] = df_long['Interval'].apply(lambda x: int(x[1:]) * 15)
    df_long['Timestamp'] = pd.to_datetime(df_long['Date']) + pd.to_timedelta(df_long['Minutes'], unit='m')

    # Clean up
    df_long = df_long.sort_values(by=['SCATS Number', 'Timestamp']).reset_index(drop=True)
    df_long.drop(columns=['Interval', 'Minutes', 'Date'], inplace=True)

    return df_long

def create_sequences(volumes, seq_len=12):
    X, y = [], []
    for i in range(len(volumes) - seq_len):
        X.append(volumes[i:i + seq_len])
        y.append(volumes[i + seq_len])
    return np.array(X), np.array(y)

def prepare_model_input(df_long, site_id=970, seq_len=12):
    site_df = df_long[df_long['SCATS Number'] == site_id]
    volumes = site_df['Volume'].fillna(0).values.reshape(-1, 1)

    scaler = MinMaxScaler()
    volumes_scaled = scaler.fit_transform(volumes).flatten()

    X, y = create_sequences(volumes_scaled, seq_len)
    return X, y, scaler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True, help="Path to the SCATS CSV file")
    parser.add_argument("--site", type=int, default=970, help="SCATS Number to filter")
    parser.add_argument("--seq_len", type=int, default=12, help="Length of input sequence")
    args = parser.parse_args()

    print("Loading and processing data...")
    df_long = load_and_clean_data(args.csv)
    print("Preparing model input...")
    X, y, scaler = prepare_model_input(df_long, site_id=args.site, seq_len=args.seq_len)

    print(f"Data ready for ML model: {X.shape[0]} samples of length {X.shape[1]}")
