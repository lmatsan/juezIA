import logging
from pathlib import Path
import os
import httpx
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Descarga el último snapshot de leyes BOE publicado en GitHub Releases
# y lo restaura en data/leyes_db.json, sobreescribiendo el fichero existente.
#
# Flujo:
#   1. Lee GITHUB_REPOSITORY del entorno para identificar el repositorio
#   2. Consulta la API de GitHub para obtener el último release
#   3. Localiza el asset leyes_db.json y lo descarga
#   4. Lo guarda en data/leyes_db.json

# Configuración 
GITHUB_API_LATEST = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
LEYES_DB_PATH     = Path(__file__).parent.parent.parent / "data" / "leyes_db.json"
OWNER             = os.getenv("GITHUB_OWNER")
REPO              = os.getenv("GITHUB_REPO")

if not OWNER:
    raise EnvironmentError(
        "Variable entorno GITHUB_OWNER no definida.\n"      
    )
if not REPO:
    raise EnvironmentError(
        "Variable entorno GITHUB_REPO no definida.\n"
    )

# Entry point
def main() -> None:
    logger.info("Buscando último snapshot en GitHub Releases...")

    with httpx.Client(timeout=30) as client:
        url_descarga = _obtener_url_descarga(client)
        logger.info(f"Snapshot encontrado: {url_descarga}")
        _descargar_snapshot(client, url_descarga)

    logger.info(f"Snapshot importado correctamente en {LEYES_DB_PATH}")

# Funciones auxiliares
def _obtener_url_descarga(client: httpx.Client) -> str:
    url = GITHUB_API_LATEST.format(owner=OWNER, repo=REPO)
    response = client.get(url, headers={"Accept": "application/vnd.github+json"})
    response.raise_for_status()

    assets = response.json().get("assets", [])
    for asset in assets:
        if asset["name"] == "leyes_db.json":
            return asset["browser_download_url"]

    raise ValueError(
        "No se encontró leyes_db.json en el último release. "
        "Comprueba que el workflow ha publicado el artefacto correctamente."
    )


def _descargar_snapshot(client: httpx.Client, url: str) -> None:
    # NOTA: si leyes_db.json crece significativamente en el futuro,
    # considerar cambiar a descarga en streaming con client.stream()
    # para evitar cargar el fichero completo en memoria.
    response = client.get(url, follow_redirects=True)
    response.raise_for_status()
    LEYES_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEYES_DB_PATH.write_bytes(response.content)


if __name__ == "__main__":
    main()