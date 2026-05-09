import pytest
import httpx
from unittest.mock import patch, MagicMock

import src.pipelines.boe.import_snapshot as import_snapshot

# Tests de _obtener_url_descarga
def test_obtener_url_descarga_ok():
    # Verifica que devuelve la URL cuando el asset leyes_db.json existe en el release
    client = MagicMock()
    client.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "assets": [
                {"name": "leyes_db.json", "browser_download_url": "https://example.com/leyes_db.json"},
            ]
        },
    )
    url = import_snapshot._obtener_url_descarga(client, "JuezIAProject", "juezIA")
    assert url == "https://example.com/leyes_db.json"


def test_obtener_url_descarga_404():
    # Verifica que lanza ValueError cuando no hay ningún release publicado
    client = MagicMock()
    client.get.return_value = MagicMock(status_code=404)
    with pytest.raises(ValueError, match="No se encontró ningún release"):
        import_snapshot._obtener_url_descarga(client, "JuezIAProject", "juezIA")


def test_obtener_url_descarga_sin_asset():
    # Verifica que lanza ValueError cuando el release no contiene leyes_db.json
    client = MagicMock()
    client.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"assets": []},
    )
    with pytest.raises(ValueError, match="No se encontró leyes_db.json"):
        import_snapshot._obtener_url_descarga(client, "JuezIAProject", "juezIA")

# Tests de _descargar_snapshot
def test_descargar_snapshot_escribe_fichero(tmp_path):
    # Verifica que el contenido descargado se escribe correctamente en LEYES_DB_PATH
    client = MagicMock()
    client.get.return_value = MagicMock(
        status_code=200,
        content=b'{"leyes": []}',
    )
    client.get.return_value.raise_for_status = MagicMock()

    with patch.object(import_snapshot, "LEYES_DB_PATH", tmp_path / "leyes_db.json"):
        import_snapshot._descargar_snapshot(client, "https://example.com/leyes_db.json")
        assert (tmp_path / "leyes_db.json").read_bytes() == b'{"leyes": []}'

# Tests de main orquestación y manejo de errores

def test_main_ok():
    # Verifica que main orquesta correctamente la descarga cuando todo está en orden
    with patch.dict("os.environ", {"GITHUB_OWNER": "JuezIAProject", "GITHUB_REPO": "juezIA"}), \
         patch.object(import_snapshot, "_obtener_url_descarga", return_value="https://example.com/leyes_db.json"), \
         patch.object(import_snapshot, "_descargar_snapshot") as mock_descargar:
        import_snapshot.main()
        mock_descargar.assert_called_once()


def test_main_sin_release(caplog):
    # Verifica que main loguea el error sin explotar cuando no hay releases publicados
    with patch.dict("os.environ", {"GITHUB_OWNER": "JuezIAProject", "GITHUB_REPO": "juezIA"}), \
         patch.object(import_snapshot, "_obtener_url_descarga", side_effect=ValueError("No se encontró ningún release")):
        import_snapshot.main()
        assert "No se encontró ningún release" in caplog.text


def test_main_error_red(caplog):
    # Verifica que main loguea el error sin explotar cuando hay un fallo de red
    with patch.dict("os.environ", {"GITHUB_OWNER": "JuezIAProject", "GITHUB_REPO": "juezIA"}), \
         patch.object(import_snapshot, "_obtener_url_descarga", side_effect=httpx.HTTPError("timeout")):
        import_snapshot.main()
        assert "Error de red" in caplog.text