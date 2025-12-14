from loguru import logger
import os


LOG_PATH = "logs/runtime.log"
os.makedirs("logs", exist_ok=True)
logger.add(LOG_PATH, rotation="1 MB")