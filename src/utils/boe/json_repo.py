
import json
from pathlib import Path
from typing import Optional

from src.utils.boe.base import LeyRepositoryBase
from src.schemas.ley import LeyMetadata

_DB_PATH = Path("data/leyes_db.json")


class JsonLeyRepository(LeyRepositoryBase):

    def _cargar(self) -> dict:
        if not _DB_PATH.exists():
            return {}
        return json.loads(_DB_PATH.read_text(encoding="utf-8"))

    def _guardar(self, datos: dict) -> None:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _DB_PATH.write_text(
            json.dumps(datos, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    async def upsert(self, metadata: LeyMetadata, contenido: str) -> None:
        datos = self._cargar()
        datos[metadata.identifier] = {
            "metadata": metadata.model_dump(mode="json"),
            "contenido": contenido,
        }
        self._guardar(datos)

    async def get(self, identifier: str) -> Optional[tuple[LeyMetadata, str]]:
        datos = self._cargar()
        entrada = datos.get(identifier)
        if entrada is None:
            return None
        return LeyMetadata(**entrada["metadata"]), entrada["contenido"]

    async def list_all(self) -> list[LeyMetadata]:
        datos = self._cargar()
        return [LeyMetadata(**v["metadata"]) for v in datos.values()]