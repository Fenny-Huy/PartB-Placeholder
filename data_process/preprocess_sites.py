# preprocess_sites.py

import pandas as pd
import argparse
import json

def load_and_filter_sites(csv_path):
    df = pd.read_csv(csv_path)
    
    # Drop rows without Site Number or Description
    df = df.dropna(subset=["Site Number", "Location Description"])
    
    # Ensure Site Number is int (remove rows with non-numeric values)
    df = df[df["Site Number"].apply(lambda x: str(x).isdigit())]
    df["Site Number"] = df["Site Number"].astype(int)

    # Filter only intersections (INT)
    df = df[df["Site Type"] == "INT"]

    # Build mapping: site_id -> description
    site_map = dict(zip(df["Site Number"], df["Location Description"]))

    return site_map

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True, help="Path to SCATS site listing CSV")
    args = parser.parse_args()

    site_map = load_and_filter_sites(args.csv)

    # Save as JSON for use later
    with open("site_map.json", "w") as f:
        json.dump(site_map, f, indent=2)

    print(f"Loaded {len(site_map)} intersection site names.")
