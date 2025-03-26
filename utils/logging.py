import logging

def setup_logger(name, level=logging.INFO):
    """Set up a logger with a specified name and level."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Create a default logger for the library
mltracker_logger = setup_logger('mltracker')
