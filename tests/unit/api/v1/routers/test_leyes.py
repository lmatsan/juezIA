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
identifier: "BOE-A-2015-11430"
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
    assert response.json()["identifier"] == "BOE-A-2015-11430"
    mock_repo.upsert.assert_called_once()

def test_ingestar_ley_error():
    # Prueba error de validación de Pydantic (422) si falta el campo obligatorio.
    # Este test NO es async porque la validación de FastAPI ocurre antes de entrar a la función
    payload = {"campo_incorrecto": "error"}
    
    response = client.post("/v1/leyes/ingestar", json=payload)
    
    assert response.status_code == 422

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
    assert data["identifier"] == "BOE-A-2015-11430"
    assert data["status"] == "vigente"     # Resultado del normalizar_status

@pytest.mark.asyncio
async def test_listar_leyes_vacia():
    # Prueba el comportamiento cuando no hay leyes indexadas.
    mock_repo.list_all = AsyncMock(return_value=[])

    response = client.get("/v1/leyes")

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_obtener_ley_not_found():
    # Prueba el error 404 cuando la ley no existe.
    mock_repo.get = AsyncMock(return_value=None)
    
    response = client.get("/v1/leyes/ID-INEXISTENTE")
    
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]


@pytest.mark.asyncio
async def test_ingestar_ley_value_error_cobertura():
    # Prueba destinada a cubrir las líneas de excepción en leyes.py
    # Enviamos algo que sabemos que romperá el parser
    payload = {"contenido_md": "formato_totalmente_invalido_sin_yaml"}
    
    response = client.post("/v1/leyes/ingestar", json=payload)
    
    assert response.status_code == 422
    assert "detail" in response.json()