import yaml
import logging

def load_config(config_path='config/config.yaml'):
    logging.info(f"Loading configuration from {config_path}...")
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info("Configuration loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        raise
