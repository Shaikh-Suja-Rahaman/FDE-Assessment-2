import os
import logging
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import dataframe_image as dfi

def save_data(final_table, config):
    logging.info("--- SAVE PHASE ---")
    
    # Create dynamic date-based run directory
    today = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_dir = f'data/processed/run_{today}'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Save CSV
    csv_path = os.path.join(output_dir, 'advanced_traffic_report.csv')
    final_table.to_csv(csv_path, index=False)
    logging.info(f"✅ Saved Final CSV Data to: {csv_path}")
    
    # 2. Generate and Save Heatmap (Pandas Styling)
    logging.info("Generating visual reports...")
    try:
        styled_table = final_table.style.background_gradient(
            cmap='RdYlGn', 
            axis=None, 
            subset=[
                col for col in final_table.columns if 'Rain' in col or col == 'overall_speed_mph'
            ]
        )
        heatmap_path = os.path.join(output_dir, 'pandas_heatmap.png')
        dfi.export(styled_table, heatmap_path, table_conversion='matplotlib')
        logging.info(f"✅ Saved Heatmap Image to: {heatmap_path}")
    except Exception as e:
        logging.error(f"⚠️ Could not generate Heatmap (dataframe_image dependency issue): {e}")

    # 3. Generate and Save Bar Chart (Seaborn)
    try:
        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=final_table, 
            x='overall_speed_mph', 
            y='Route', 
            palette='RdYlGn' 
        )
        
        min_dist = config['metrics']['min_distance_miles']
        top_n = config['metrics']['top_n_worst_routes']
        
        plt.title(f'Top {top_n} Worst NYC Traffic Corridors (Dist > {min_dist} Miles)', fontsize=14, pad=15)
        plt.xlabel('Average Speed (MPH)', fontsize=12)
        plt.ylabel('Route Corridor', fontsize=12)
        plt.axvline(x=5.0, color='red', linestyle='--', label='Brisk Walking Speed (5 MPH)')
        plt.legend()
        plt.tight_layout()
        
        chart_path = os.path.join(output_dir, 'bottleneck_chart.png')
        plt.savefig(chart_path, dpi=150)
        plt.close() # Close figure to free memory
        logging.info(f"✅ Saved Bar Chart Image to: {chart_path}")
    except Exception as e:
        logging.error(f"⚠️ Could not generate Bar Chart: {e}")
    
    # 4. Generate Metadata
    metadata = {
        "run_date": today,
        "records_generated": len(final_table),
        "config_used": config
    }
    
    meta_path = os.path.join(output_dir, 'run_metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    logging.info(f"✅ Saved Run Metadata to: {meta_path}")
