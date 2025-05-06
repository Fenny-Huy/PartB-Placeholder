# preprocess_traffic_counts.py

import pandas as pd
import argparse
import json

def load_and_process_traffic_data(csv_path):
    df = pd.read_csv(csv_path)

    # Drop rows with missing coordinates or traffic counts
    df = df.dropna(subset=["X", "Y", "AADT_ALLVE", "AADT_TRUCK"])

    # Keep only intersection-type entries
    df = df[df["TFM_TYP_DE"] == "INTERSECTION"]

    # Convert to simplified list of dicts
    records = []
    for _, row in df.iterrows():
        record = {
            "desc": row["TFM_DESC"],
            "latitude": row["Y"],
            "longitude": row["X"],
            "aadt_all": int(row["AADT_ALLVE"]),
            "aadt_truck": int(row["AADT_TRUCK"]),
            "truck_pct": float(row["PER_TRUCKS"]) if not pd.isna(row["PER_TRUCKS"]) else None,
            "last_year": int(row["LAST_YEAR"]),
        }
        records.append(record)
    
    return records

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True, help="Path to traffic count locations CSV")
    args = parser.parse_args()

    traffic_data = load_and_process_traffic_data(args.csv)

    # Save as JSON
    with open("traffic_counts.json", "w") as f:
        json.dump(traffic_data, f, indent=2)

    print(f"Saved {len(traffic_data)} intersection traffic records.")
