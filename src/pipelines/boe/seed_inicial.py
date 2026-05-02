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

def main() -> None:
    """
    Orquesta el proceso de seeding: carga identificadores, descarga leyes 
    e ingesta el contenido en la API.

    Pasos:
    1. Recupera identificadores desde el archivo de configuración.
    2. Itera cada identificador usando un cliente HTTP con timeout de 30s.
    3. Descarga el contenido Markdown de cada ley y lo envía al endpoint de ingesta.
    4. Clasifica los resultados en 'ok' o 'error' según el éxito de la operación.
    5. Genera un reporte final en los logs con el resumen de la ejecución.
    """

    identifiers = _cargar_identifiers()
    logger.info(f"Iniciando seed con {len(identifiers)} leyes.")

    resultados = {"ok": [], "error": []}

    with httpx.Client(timeout=30) as client:
        for identifier in identifiers:
            try:
                contenido_md = _descargar_ley(client, identifier)
                _ingestar_ley(client, identifier, contenido_md)
                resultados["ok"].append(identifier)
                logger.info(f"[OK] {identifier}")
            except Exception as exc:
                resultados["error"].append(identifier)
                logger.error(f"[ERROR] {identifier}: {exc}")

    logger.info(
        f"Seed completado. "
        f"OK: {len(resultados['ok'])} | "
        f"Errores: {len(resultados['error'])}"
    )
    if resultados["error"]:
        logger.warning(f"Leyes con error: {resultados['error']}")