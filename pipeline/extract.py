import pandas as pd
import requests
import logging

def extract_data(config):
    logging.info("--- EXTRACT PHASE ---")
    
    # 1. Load Parquet
    parquet_path = config['data_sources']['trip_data_parquet']
    logging.info(f"Loading trip data from {parquet_path}...")
    df_trips = pd.read_parquet(parquet_path)
    
    # 2. Load CSV
    csv_path = config['data_sources']['zone_data_csv']
    logging.info(f"Loading zone data from {csv_path}...")
    df_zones = pd.read_csv(csv_path)
    
    # 3. Load Weather API
    logging.info("Fetching live historical weather data from Open-Meteo API...")
    api_url = config['data_sources']['weather_api_url']
    lat = config['data_sources']['weather_latitude']
    lon = config['data_sources']['weather_longitude']
    start = config['data_sources']['weather_start_date']
    end = config['data_sources']['weather_end_date']
    
    url = f"{api_url}?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&hourly=precipitation"
    weather_data = requests.get(url).json()
    
    df_weather = pd.DataFrame(weather_data['hourly'])
    df_weather['time'] = pd.to_datetime(df_weather['time'])
    df_weather['is_raining'] = df_weather['precipitation'] > 0
    
    logging.info(f"Extracted {len(df_trips):,} trips, {len(df_zones)} zones, and {len(df_weather)} hours of weather data.")
    return df_trips, df_zones, df_weather
