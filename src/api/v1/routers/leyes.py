from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.schemas.ley import LeyMetadata
from src.utils.boe.parser_ley import parsear_ley

router = APIRouter(prefix="/v1/leyes", tags=["leyes"])

class IngestarLeyRequest(BaseModel):
    contenido_md: str

class IngestarLeyResponse(BaseModel):
    identifier: str
    message: str

@router.post(
    "/ingestar",
    response_model=IngestarLeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingestar una ley en ChromaDB",
    description=(
        "Recibe el contenido crudo de un fichero .md de legalize-es, "
        "extrae el frontmatter y el cuerpo, y lo guarda en ChromaDB. "
        "Si la ley ya existe, la sobreescribe (idempotente)."
    ),
)
async def ingestar_ley(request: IngestarLeyRequest) -> IngestarLeyResponse:
    try:
        metadata, contenido = parsear_ley(request.contenido_md)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    await _guardar_en_chromadb(metadata, contenido)

    return IngestarLeyResponse(
        identifier=metadata.identifier,
        message=f"Ley '{metadata.identifier}' ingresada correctamente.",
    )


@router.get(
    "",
    response_model=list[LeyMetadata],
    summary="Listar todas las leyes indexadas",
    description="Devuelve los metadatos de todas las leyes almacenadas en ChromaDB.",
)
async def listar_leyes() -> list[LeyMetadata]:
    return await _listar_desde_chromadb()


@router.get(
    "/{identifier}",
    response_model=LeyMetadata,
    summary="Obtener una ley por identificador",
    description="Devuelve los metadatos de una ley concreta. Ejemplo: BOE-A-2015-11430",
)
async def obtener_ley(identifier: str) -> LeyMetadata:
    ley = await _obtener_desde_chromadb(identifier)
    if ley is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ninguna ley con identifier '{identifier}'.",
        )
    return ley


# Funciones auxiliares para interactuar con ChromaDB (implementación pendiente)
async def _guardar_en_chromadb(metadata: LeyMetadata, contenido: str) -> None:
    """
    TODO: integrar con ChromaDB.

    Operación upsert usando metadata.identifier como document_id
    para garantizar idempotencia.
    """
    raise NotImplementedError

async def _listar_desde_chromadb() -> list[LeyMetadata]:
    """
    TODO: integrar con ChromaDB.

    Recuperar todos los documentos de la colección BOE
    y mapear sus metadatos a LeyMetadata.
    """
    raise NotImplementedError


async def _obtener_desde_chromadb(identifier: str) -> Optional[LeyMetadata]:
    """
    TODO: integrar con ChromaDB.

    Buscar por document_id = identifier.
    Devolver None si no existe.
    """
    raise NotImplementedError