import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.v1.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "JuezIA API Running"}

# Usamos patch para "congelar" el servicio real
# Nota: La ruta debe ser donde se USA el servicio, no donde se define
@patch("src.api.v1.app.AnalizadorService")
def test_analizar_caso_mocked(mock_service):
    """Testeamos la API sin tocar la lógica real de AnalizadorService"""
    
    # 1. Configuramos el comportamiento del Mock
    # Simulamos que calcular_probabilidad siempre devuelve 85
    mock_service.calcular_probabilidad.return_value = 85
    # Simulamos que generar_consejo_ia devuelve un texto fijo
    mock_service.generar_consejo_ia.return_value = "Consejo de prueba"

    # 2. Ejecutamos la petición
    payload = {
        "nombre_trabajador": "Test Bot",
        "tiene_horario": True,
        "herramientas_empresa": True,
        "instrucciones_directas": True,
        "horario_impuesto": True,
        "ajenidad_clientes": True,
        "retribucion_fija": True,
        "exclusividad_de_facto": True
    }
    response = client.post("/analizar", json=payload)

    # 3. Verificaciones
    assert response.status_code == 200
    data = response.json()
    
    # Verificamos que la API usó los datos de nuestro Mock
    assert data["probabilidad_laboralidad"] == "85%"
    assert data["recomendacion"] == "Consejo de prueba"
    
    # Verificamos que el servicio fue llamado exactamente con los datos que enviamos
    mock_service.calcular_probabilidad.assert_called_once()