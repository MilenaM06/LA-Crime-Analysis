import os
import pandas as pd
import numpy as np

# 1. SET FILE PATH
crime_csv_path = "data/crime-data/crime_data_2010_2019.csv"
print("Current working directory:", os.getcwd())

if not os.path.exists(crime_csv_path):
    raise FileNotFoundError(f"File not found: {crime_csv_path}")

# 2. LOAD CRIME DATA
crime_df = pd.read_csv(crime_csv_path)
print("Original rows:", len(crime_df))

# CLEAN COLUMN NAMES
crime_df.columns = crime_df.columns.str.strip()

# CREATE DATETIME CORRECTLY
crime_df["DATE_ONLY"] = crime_df["DATE OCC"].astype(str).str.split(" ").str[0]

# Format TIME OCC properly (1745 → 17:45:00)
crime_df["TIME OCC"] = crime_df["TIME OCC"].astype(str).str.zfill(4)

crime_df["TIME_FORMATTED"] = (
    crime_df["TIME OCC"].str[:2] + ":" +
    crime_df["TIME OCC"].str[2:] + ":00"
)

# Combine
crime_df["datetime"] = pd.to_datetime(
    crime_df["DATE_ONLY"] + " " + crime_df["TIME_FORMATTED"],
    format="%m/%d/%Y %H:%M:%S",
    errors="coerce"
)

print("Null datetimes:", crime_df["datetime"].isna().sum())

# 4. CREATE DATETIME COLUMN
crime_df.columns = crime_df.columns.str.strip()

# Combine date and time
crime_df["DATE OCC"] = crime_df["DATE OCC"].astype(str).str.strip()
crime_df["TIME OCC"] = crime_df["TIME OCC"].astype(str).str.zfill(4)

crime_df["datetime"] = pd.to_datetime(
    crime_df["DATE OCC"] + " " +
    crime_df["TIME OCC"].str[:2] + ":" +
    crime_df["TIME OCC"].str[2:],
    errors="coerce"
)

# Remove invalid rows
print("Missing LAT:", crime_df["LAT"].isna().sum())
print("Missing LON:", crime_df["LON"].isna().sum())
print("Missing datetime:", crime_df["datetime"].isna().sum())

crime_df = crime_df.dropna(subset=["datetime", "LAT", "LON"])

print("Datetime conversion done.")

# 5. FILTER ONLY LA AREA
crime_df = crime_df[
    (crime_df["LAT"] > 33) & (crime_df["LAT"] < 35) &
    (crime_df["LON"] < -117) & (crime_df["LON"] > -119)
]

print("Rows after LA filter:", len(crime_df))


# 6. STRONGER LOCATION ROUNDING
# 1 km grid
lat_grid = 1 / 111  # 1 km in latitude degrees
lon_grid = 1 / (111 * np.cos(np.radians(crime_df["LAT"].mean())))

crime_df["lat_round"] = (crime_df["LAT"] / lat_grid).round() * lat_grid
crime_df["lon_round"] = (crime_df["LON"] / lon_grid).round() * lon_grid

# 7. ROUND TIME TO 3-HOUR BLOCKS
crime_df["hour_block"] = crime_df["datetime"].dt.floor("3h")

# 8. CREATE UNIQUE WEATHER REQUESTS
unique_df = crime_df[[
    "hour_block",
    "lat_round",
    "lon_round"
]].drop_duplicates()

print("Unique weather requests:", len(unique_df))
unique_df.to_csv("data/results/unique_weather_requests_reduced.csv", index=False)