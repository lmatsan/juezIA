import os  
from dotenv import load_dotenv
import json
import logging
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

LEYES_RELEVANTES_PATH = Path(__file__).parent.parent.parent / "data" / "leyes_relevantes.json"
LEGALIZE_ES_RAW_URL   = "https://raw.githubusercontent.com/legalize-dev/legalize-es/main/es/{identifier}.md"
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_INGESTAR_URL = f"{API_BASE_URL}/v1/leyes/ingestar"

