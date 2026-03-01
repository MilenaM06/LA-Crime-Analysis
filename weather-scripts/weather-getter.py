import geopandas as gpd
import pandas as pd
import requests
import time

divisions_geojson_path = "data/districts-data/LAPD_Division.geojson"


divisions = gpd.read_file(divisions_geojson_path)

divisions = divisions[["OBJECTID", "APREC", "geometry"]]

# Convert to WGS84 (lat/lon)
divisions = divisions.to_crs("EPSG:4326")

# Compute centroid
divisions["centroid"] = divisions.geometry.centroid

# Extract latitude and longitude
divisions["lat"] = divisions.centroid.y
divisions["lon"] = divisions.centroid.x

# Keep only what we need
divisions = divisions[["APREC", "lat", "lon"]]

print(divisions)

START_YEAR = 2010
END_YEAR = 2019

all_weather_data = []

for index, row in divisions.iterrows():

    division_name = row["APREC"]
    lat = row["lat"]
    lon = row["lon"]

    for year in range(START_YEAR, END_YEAR + 1):

        print(f"Downloading {division_name} - {year}")

        url = "https://archive-api.open-meteo.com/v1/archive"

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": f"{year}-01-01",
            "end_date": f"{year}-12-31",
            "hourly": "temperature_2m,precipitation,wind_speed_10m",
            "timezone": "America/Los_Angeles"
        }

        success = False

        while not success:

            response = requests.get(url, params=params)
            data = response.json()

            # 🔥 RATE LIMIT DETECTED
            if "reason" in data and "limit exceeded" in data["reason"].lower():
                print("Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                continue

            # 🔥 OTHER ERROR
            if "hourly" not in data:
                print("Unexpected error:")
                print(json.dumps(data, indent=4))
                break

            # SUCCESS
            hourly = data["hourly"]

            weather_df = pd.DataFrame({
                "datetime": hourly["time"],
                "temperature": hourly["temperature_2m"],
                "precipitation": hourly["precipitation"],
                "wind_speed": hourly["wind_speed_10m"]
            })

            weather_df["APREC"] = division_name
            weather_df["datetime"] = pd.to_datetime(weather_df["datetime"])

            all_weather_data.append(weather_df)

            success = True

            time.sleep(2)  # small delay between successful calls


# Combine everything
weather_all = pd.concat(all_weather_data, ignore_index=True)

weather_all.to_csv("data/results/weather_2010_2019_hourly.csv", index=False)

print("Download complete.")