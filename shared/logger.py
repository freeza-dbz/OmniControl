import logging
import os 
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    
    logger = logging.getLogger(name)
    
    if not logger.hasHandlers():
        return logger;
    
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] "
        "[%(levelname)s] "
        "[%(name)s] "
        "%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File Handler
    
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"{name}.log"),
        maxBytes=5 * 1024 * 1024,   # 5 MB
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger