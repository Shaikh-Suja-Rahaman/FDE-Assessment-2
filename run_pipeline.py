import logging
from pipeline.logging_utils import setup_logger
from pipeline.config import load_config
from pipeline.extract import extract_data
from pipeline.clean import clean_data
from pipeline.transform import transform_data
from pipeline.save import save_data

def main():
    # Initialize Logger
    setup_logger()
    logging.info("=========================================")
    logging.info("Starting Modular FDE Traffic Pipeline")
    logging.info("=========================================")
    
    # Load Configurations
    config = load_config()
    
    # Execute ETL Pipeline
    df_trips, df_zones, df_weather = extract_data(config)
    df_clean = clean_data(df_trips, config)
    final_table = transform_data(df_clean, df_zones, df_weather, config)
    
    # Save results
    save_data(final_table, config)
    
    logging.info("=========================================")
    logging.info("Pipeline Execution Completed Successfully.")
    logging.info("=========================================")

if __name__ == "__main__":
    main()
