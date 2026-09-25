import logging

def clean_data(df_trips, config):
    logging.info("--- CLEAN PHASE ---")
    initial_count = len(df_trips)
    
    logging.info("Calculating trip durations and checking rules...")
    # Calculate duration in minutes
    df_trips['trip_duration_minutes'] = (df_trips['tpep_dropoff_datetime'] - df_trips['tpep_pickup_datetime']).dt.total_seconds() / 60.0
    
    # Apply rules (No teleportation, no 0 distances)
    df_clean = df_trips[
        (df_trips['trip_distance'] > 0) & 
        (df_trips['trip_duration_minutes'] > 0) & 
        (df_trips['trip_duration_minutes'] < 300)
    ].copy()
    
    df_clean['speed_mph'] = df_clean['trip_distance'] / (df_clean['trip_duration_minutes'] / 60.0)
    
    # Apply YAML Config for Outlier Removal
    max_speed = config['data_cleaning']['max_speed_mph_outlier']
    df_clean = df_clean[df_clean['speed_mph'] <= max_speed]
    
    dropped = initial_count - len(df_clean)
    logging.warning(f"Dropped {dropped:,} invalid rows (Negative time, zero distance, or physics violations > {max_speed} mph).")
    
    return df_clean
