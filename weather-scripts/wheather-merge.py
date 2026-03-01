import pandas as pd

# Load Crime Data
crime_csv_path = "data/crime-data/crime_data_2010_2019.csv"
crime = pd.read_csv(crime_csv_path)

print("Original rows:", len(crime))

# Clean Date & Time
crime["DATE OCC"] = pd.to_datetime(crime["DATE OCC"], errors="coerce")

# Fix TIME OCC (force 4-digit format)
crime["TIME OCC"] = (
    crime["TIME OCC"]
    .astype(str)
    .str.replace(".0", "", regex=False)
    .str.zfill(4)
)

# Extract hour / minute safely
crime["hour"] = crime["TIME OCC"].str[:2].astype(int)
crime["minute"] = crime["TIME OCC"].str[2:].astype(int)

# Create full datetime
crime["datetime"] = (
    crime["DATE OCC"]
    + pd.to_timedelta(crime["hour"], unit="h")
    + pd.to_timedelta(crime["minute"], unit="m")
)

# Drop helper columns (optional but cleaner)
crime.drop(columns=["hour", "minute"], inplace=True)

# Round DOWN to closest hour
crime["datetime"] = crime["datetime"].dt.floor("h")

# Standardize Area Name
crime["APREC"] = crime["AREA NAME"].astype(str).str.strip().str.upper()

print("Datetime transformation done.")
print(crime[["AREA NAME", "APREC", "datetime"]].head())

# Load Weather Data
weather_all = pd.read_csv("data/results/weather_2010_2019_hourly.csv")

# Convert datetime
weather_all["datetime"] = pd.to_datetime(weather_all["datetime"], errors="coerce")

# Standardize area column in weather (adjust column name if needed)
if "APREC" in weather_all.columns:
    weather_all["APREC"] = weather_all["APREC"].astype(str).str.strip().str.upper()
else:
    raise ValueError("Weather file must contain 'APREC' column for merge.")

# Merge
final = crime.merge(
    weather_all,
    on=["APREC", "datetime"],
    how="left",
    validate="m:1"  # helps detect duplicates issues
)

print("Merge completed.")
print(final.head())

# Save Final Dataset
final.to_csv("data/results/crime_weather_hourly_merged.csv", index=False)

print("File saved successfully.")