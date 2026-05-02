from abc import ABC, abstractmethod
from src.schemas.ley import LeyMetadata


class LeyRepositoryBase(ABC):

    @abstractmethod
    async def upsert(self, metadata: LeyMetadata, contenido: str) -> None:
        """Guarda o sobreescribe una ley."""

    @abstractmethod
    async def get(self, identifier: str) -> tuple[LeyMetadata, str] | None:
        """Devuelve (metadata, contenido) o None si no existe."""

    @abstractmethod
    async def list_all(self) -> list[LeyMetadata]:
        """Devuelve los metadatos de todas las leyes."""