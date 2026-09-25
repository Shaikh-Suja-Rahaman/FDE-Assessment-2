import logging

def transform_data(df_clean, df_zones, df_weather, config):
    logging.info("--- TRANSFORM PHASE ---")
    
    # 1. Map Zone Names
    logging.info("Mapping pickup and dropoff zones...")
    df_clean = df_clean.merge(df_zones[['LocationID', 'Zone']], left_on='PULocationID', right_on='LocationID', how='left')
    df_clean = df_clean.rename(columns={'Zone': 'Pickup_Zone'})
    df_clean = df_clean.merge(df_zones[['LocationID', 'Zone']], left_on='DOLocationID', right_on='LocationID', how='left')
    df_clean = df_clean.rename(columns={'Zone': 'Dropoff_Zone'})
    df_clean['Route'] = df_clean['Pickup_Zone'] + " to " + df_clean['Dropoff_Zone']
    
    # 2. Temporal Modeling (Rush Hour)
    logging.info("Applying Temporal Rush Hour Modeling...")
    df_clean['pickup_hour'] = df_clean['tpep_pickup_datetime'].dt.hour
    m_start = config['business_logic']['morning_rush_start_hour']
    m_end = config['business_logic']['morning_rush_end_hour']
    e_start = config['business_logic']['evening_rush_start_hour']
    e_end = config['business_logic']['evening_rush_end_hour']
    
    def categorize_time(hour):
        if m_start <= hour <= m_end: return 'Morning Rush'
        elif e_start <= hour <= e_end: return 'Evening Rush'
        else: return 'Off-Peak'
        
    df_clean['time_of_day'] = df_clean['pickup_hour'].apply(categorize_time)
    
    # 3. Weather Merge
    logging.info("Joining hourly weather API data to trip timestamps...")
    df_clean['weather_join_time'] = df_clean['tpep_pickup_datetime'].dt.floor('h')
    df_clean = df_clean.merge(df_weather[['time', 'is_raining']], left_on='weather_join_time', right_on='time', how='left')
    
    # 4. Advanced Metrics Aggregation
    logging.info("Calculating worst bottlenecks based on metrics config limits...")
    route_stats = df_clean.groupby('Route').agg(
        overall_speed_mph=('speed_mph', 'mean'),
        average_distance_miles=('trip_distance', 'mean'),
        total_trips=('speed_mph', 'count')
    ).reset_index()
    
    min_trips = config['metrics']['min_total_trips']
    min_dist = config['metrics']['min_distance_miles']
    top_n = config['metrics']['top_n_worst_routes']
    
    route_stats = route_stats[
        (route_stats['total_trips'] >= min_trips) & 
        (route_stats['average_distance_miles'] >= min_dist)
    ]
    
    top_worst = route_stats.sort_values('overall_speed_mph').head(top_n)
    worst_route_names = top_worst['Route'].tolist()
    
    # Pivot final report
    df_worst = df_clean[df_clean['Route'].isin(worst_route_names)]
    pivot_report = df_worst.pivot_table(
        index='Route',
        columns=['time_of_day', 'is_raining'],
        values='speed_mph',
        aggfunc='mean'
    ).round(2)
    
    pivot_report.columns = [f"{time} (Rain: {rain})" for time, rain in pivot_report.columns]
    flat_report = pivot_report.reset_index()
    
    final_table = flat_report.merge(top_worst, on='Route', how='left')
    final_table['average_distance_miles'] = final_table['average_distance_miles'].round(2)
    final_table = final_table.sort_values('overall_speed_mph', ascending=True)
    
    logging.info(f"Transformation complete! Isolated the Top {top_n} worst routes.")
    return final_table
