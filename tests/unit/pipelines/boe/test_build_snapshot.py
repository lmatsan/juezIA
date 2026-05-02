import re
import pytest
import respx
from httpx import Response
from pathlib import Path
from unittest.mock import patch, mock_open
from src.pipelines.boe.build_snapshot import main, API_INGESTAR_URL

# Mock de los identificadores que leería del archivo JSON
MOCK_IDENTIFIERS = '{"leyes": ["BOE-A-2015-11430"]}'

# Mock de un contenido Markdown mínimo para el parser
MOCK_MD = """---
identifier: BOE-A-2015-11430
title: Ley de Test
rank: ley
last_updated: 2024-01-01
---
Contenido de la ley"""

@respx.mock
def test_build_snapshot_ingesta_nueva():
    # Prueba el siguiente caso: La ley no existe en nuestra API local, debe ingestarla.
    # 1. Mock de lectura de archivo leyes_relevantes.json
    with patch("builtins.open", mock_open(read_data=MOCK_IDENTIFIERS)):
        
        # 2. Mock de descarga desde GitHub (Legalize-es)
        respx.get(url=re.compile(r"raw\.githubusercontent.com/.*")).mock(
            return_value=Response(200, text=MOCK_MD)
        )
        
        # 3. Mock de consulta a nuestra API local (Devuelve 404 porque no existe)
        respx.get(url=re.compile(r"/v1/leyes/BOE-A-2015-11430")).mock(
            return_value=Response(404)
        )
        
        # 4. Mock del POST de ingesta a nuestra API local (Devuelve 201 Created)
        ingesta_route = respx.post(API_INGESTAR_URL).mock(
            return_value=Response(201, json={"identifier": "BOE-A-2015-11430", "message": "ok"})
        )

        main()

        # Verificamos que se intentó ingestar
        assert ingesta_route.called

@respx.mock
def test_build_snapshot_omitida_ya_al_dia():
    # Prueba el siguiente caso: Cubre el bloque 'else': la ley local ya está actualizada."""
    with patch("builtins.open", mock_open(read_data=MOCK_IDENTIFIERS)):
        # 1. GitHub devuelve una ley con last_updated: 2024-01-01
        respx.get(url=re.compile(r"raw\.githubusercontent\.com/.*")).mock(
            return_value=Response(200, text=MOCK_MD)
        )
        
        # 2. Tu API responde que ya tiene la versión de 2024-01-01
        respx.get(url=re.compile(r".*/v1/leyes/BOE-A-2015-11430")).mock(
            return_value=Response(200, json={"last_updated": "2024-01-01"})
        )
        
        # 3. Preparamos el mock de ingesta (pero no debería llamarse)
        ingesta_route = respx.post(re.compile(r".*/v1/leyes/ingestar")).mock(
            return_value=Response(201)
        )

        main()

        # Verificamos que NO se llamó a la ingesta
        assert not ingesta_route.called

@respx.mock
def test_build_snapshot_error_capturado():
    # Prueba el siguiente caso: Cubre el bloque 'except Exception': algo falla durante el proceso.
    with patch("builtins.open", mock_open(read_data=MOCK_IDENTIFIERS)):
        # Forzamos un error 500 en GitHub para que salte la excepción
        respx.get(url=re.compile(r"raw\.githubusercontent\.com/.*")).mock(
            return_value=Response(500)
        )
        try:
            main()
        except Exception as e:
            pytest.fail(f"El main() debería haber capturado la excepción internamente: {e}")
        