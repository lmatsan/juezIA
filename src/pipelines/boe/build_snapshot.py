import os  
from dotenv import load_dotenv
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import date
import sys

print(f"DEBUG: PYTHONPATH es {sys.path[0]}")
print(f"DEBUG: Directorio actual es {os.getcwd()}")

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Calculamos la raíz del proyecto (juezIA) para asegurar que podemos importar los módulos de src sin problemas.
root_path = Path(__file__).resolve().parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

LEYES_RELEVANTES_PATH = root_path / "data" / "leyes_relevantes.json"
LEGALIZE_ES_RAW_URL   = "https://github.com/legalize-dev/legalize-es/blob/main/es/{identifier}.md"
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_INGESTAR_URL = f"{API_BASE_URL}/v1/leyes/ingestar"
API_LEY_URL      = f"{API_BASE_URL}/v1/leyes/{{identifier}}"

def main() -> None:
    identifiers = _cargar_identifiers()
    logger.info(f"Iniciando build_snapshot con {len(identifiers)} leyes.")

    resultados = {"actualizada": [], "omitida": [], "error": []}

    with httpx.Client(timeout=30) as client:
        for identifier in identifiers:
            try:
                contenido_md = _descargar_ley(client, identifier)
                last_updated_repo = _extraer_last_updated(contenido_md)
                last_updated_local = _obtener_last_updated_local(client, identifier)

                if _necesita_actualizacion(last_updated_repo, last_updated_local):
                    _ingestar_ley(client, identifier, contenido_md)
                    resultados["actualizada"].append(identifier)
                    logger.info(f"[ACTUALIZADA] {identifier} → {last_updated_repo}")
                else:
                    resultados["omitida"].append(identifier)
                    logger.info(f"[OMITIDA] {identifier} ya está al día.")

            except Exception as exc:
                resultados["error"].append(identifier)
                logger.error(f"[ERROR] {identifier}: {exc}")

    logger.info(
        f"Build completado. "
        f"Actualizadas: {len(resultados['actualizada'])} | "
        f"Omitidas: {len(resultados['omitida'])} | "
        f"Errores: {len(resultados['error'])}"
    )
    if resultados["error"]:
        logger.warning(f"Leyes con error: {resultados['error']}")

def _cargar_identifiers() -> list[str]:
    with open(LEYES_RELEVANTES_PATH, encoding="utf-8") as f:
        datos = json.load(f)
    return datos["leyes"]


def _descargar_ley(client: httpx.Client, identifier: str) -> str:
    url = LEGALIZE_ES_RAW_URL.format(identifier=identifier)
    response = client.get(url)
    response.raise_for_status()
    return response.text


def _extraer_last_updated(contenido_md: str) -> Optional[date]:
    from src.utils.boe.parser_ley import parsear_ley
    metadata, _ = parsear_ley(contenido_md)
    return metadata.last_updated


def _obtener_last_updated_local(client: httpx.Client, identifier: str) -> Optional[date]:
    url = API_LEY_URL.format(identifier=identifier)
    response = client.get(url)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    datos = response.json()
    raw = datos.get("last_updated")
    return date.fromisoformat(raw) if raw else None


def _necesita_actualizacion(
    repo: Optional[date],
    local: Optional[date],
) -> bool:
    if local is None:
        return True
    if repo is None:
        return True
    return repo > local


def _ingestar_ley(client: httpx.Client, identifier: str, contenido_md: str) -> None:
    response = client.post(API_INGESTAR_URL, json={"contenido_md": contenido_md})
    response.raise_for_status()


if __name__ == "__main__":
    main()