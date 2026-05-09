import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

BASE_URL = DEEPSEEK_BASE_URL
MODEL_NAME = DEEPSEEK_MODEL
REPORTS_DIR = "reports/"
MAX_HISTORY_LENGTH = 20
DATA_PATH = "data/"
