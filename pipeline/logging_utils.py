import logging
import os
from datetime import datetime

def setup_logger():
    os.makedirs('logs', exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = f'logs/pipeline_{today}.log'
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # File handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger
