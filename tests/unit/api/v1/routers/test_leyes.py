import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.api.v1.app import app
from src.api.v1.routers.leyes import get_repository
from src.schemas.ley import LeyMetadata

client = TestClient(app)

# Creamos un Mock del repositorio
mock_repo = MagicMock()
mock_repo.upsert = AsyncMock()
mock_repo.list_all = AsyncMock()
mock_repo.get = AsyncMock()

# Inyectamos el mock en la aplicación
app.dependency_overrides[get_repository] = lambda: mock_repo

# Datos de prueba
METADATA = {
    "identifier": "BOE-A-2015-11430",
    "title": "Estatuto de los Trabajadores",
    "rank": "real decreto ley", 
    "department": "Ministerio de Empleo",
    "subjects": ["Laboral", "Empleo"],
    "publication_date": "2015-10-24",
    "status": "active"         
}
LEY_METADATA = LeyMetadata(**METADATA)
# Contenido Markdown simulado con frontmatter
LEY_MD = """---
identifier: BOE-T-001
title: Ley de Test
rank: ley
---
Cuerpo de la norma de prueba."""

# Limpia los mocks antes de cada test si es necesario"""
def test_setup():
    
    mock_repo.reset_mock()

def test_ingestar_ley_success():
    # El test valida que el router extraiga correctamente los metadatos 
    # del frontmatter YAML incluido en el cuerpo.

    # Simulamos el contenido de un archivo .md
    payload = {"contenido_md": LEY_MD}
    mock_repo.upsert = AsyncMock()
    
    response = client.post("/v1/leyes/ingestar", json=payload)
    
    assert response.status_code == 201
    assert response.json()["identifier"] == "BOE-T-001"
    mock_repo.upsert.assert_called_once()

@pytest.mark.asyncio
async def test_obtener_ley_success():
    # El test verifica que el router sabe manejar la tupla (metadata, contenido) 
    # que devuelve el repositorio
    
    # IMPORTANTE: El repo devuelve una tupla (Metadata, String)
    mock_repo.get = AsyncMock(return_value=(LEY_METADATA, "# Cuerpo de la ley"))
    
    response = client.get(f"/v1/leyes/{METADATA['identifier']}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificamos que la normalización funcionó
    assert METADATA["identifier"] == data["identifier"]
    assert METADATA["rank"] == data["rank"] # Resultado del normalizar_rank
    assert METADATA["status"] == data["status"]        # Resultado del normalizar_status