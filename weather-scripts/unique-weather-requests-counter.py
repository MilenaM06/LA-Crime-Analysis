import os
import pandas as pd

# 1. SET FILE PATH
crime_csv_path = "data/crime-data/crime_data_2010_2019.csv"

if not os.path.exists(crime_csv_path):
    raise FileNotFoundError(f"File not found: {crime_csv_path}")

# 2. LOAD CRIME DATA
crime_df = pd.read_csv(crime_csv_path)
print("Original rows:", len(crime_df))

# 3. CREATE PROPER DATETIME (FOR YOUR FORMAT)
crime_df["DATE OCC"] = crime_df["DATE OCC"].astype(str)
crime_df["TIME OCC"] = crime_df["TIME OCC"].astype(str)

# Remove the time part from DATE OCC (keep only date)
crime_df["DATE OCC"] = crime_df["DATE OCC"].str.split(" ").str[0]

# Convert TIME OCC to 4-digit format
crime_df["TIME OCC"] = crime_df["TIME OCC"].str.zfill(4)

# Convert 1350 → 13:50:00
crime_df["TIME OCC"] = (
    crime_df["TIME OCC"].str[:2] + ":" +
    crime_df["TIME OCC"].str[2:] + ":00"
)

# Combine into datetime
crime_df["datetime"] = pd.to_datetime(
    crime_df["DATE OCC"] + " " + crime_df["TIME OCC"],
    format="%m/%d/%Y %H:%M:%S",
    errors="coerce"
)

# Remove invalid rows
crime_df = crime_df.dropna(subset=["datetime", "LAT", "LON"])

print("Datetime conversion done.")

# 4. ROUND LOCATION (Reduce Requests)
crime_df["lat_round"] = crime_df["LAT"].round(2)
crime_df["lon_round"] = crime_df["LON"].round(2)

# 5. ROUND TIME TO HOUR
crime_df["hour"] = crime_df["datetime"].dt.floor("h")

# 6. CREATE UNIQUE REQUEST KEY
crime_df["request_key"] = (
    crime_df["hour"].astype(str) + "_" +
    crime_df["lat_round"].astype(str) + "_" +
    crime_df["lon_round"].astype(str)
)

# 7. COUNT UNIQUE REQUESTS
unique_requests = crime_df["request_key"].nunique()

print("Unique weather requests:", unique_requests)

# 8. SAVE UNIQUE REQUEST LIST
unique_df = crime_df[[
    "hour",
    "lat_round",
    "lon_round",
    "request_key"
]].drop_duplicates()

unique_df.to_csv("data/results/unique_weather_requests.csv", index=False)

print("Saved unique_weather_requests.csv")