from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

from src.utils.boe.base import LeyRepositoryBase
from src.utils.boe.json_repo import JsonLeyRepository
from src.schemas.ley import LeyMetadata
from src.utils.boe.parser_ley import parsear_ley
from src.schemas.ley import LeyMetadata
from src.utils.boe.parser_ley import parsear_ley

router = APIRouter(prefix="/v1/leyes", tags=["Leyes BOE"])

class IngestarLeyRequest(BaseModel):
    contenido_md: str

class IngestarLeyResponse(BaseModel):
    identifier: str
    message: str

def get_repository() -> LeyRepositoryBase:
    return JsonLeyRepository()

@router.post(
    "/ingestar",
    response_model=IngestarLeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingestar una ley en base de datos",
    description=(
        "Recibe el contenido crudo de un fichero .md de legalize-es, "
        "extrae el frontmatter y el cuerpo, y lo guarda en BD. "
        "Si la ley ya existe, la sobreescribe (idempotente)."
    ),
)
async def ingestar_ley(
    request: IngestarLeyRequest,
    repo: LeyRepositoryBase = Depends(get_repository),
    ) -> IngestarLeyResponse:
    
    try:
        metadata, contenido = parsear_ley(request.contenido_md)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    await repo.upsert(metadata, contenido)

    return IngestarLeyResponse(
        identifier=metadata.identifier,
        message=f"Ley '{metadata.identifier}' ingresada correctamente.",
    )


@router.get(
    "",
    response_model=list[LeyMetadata],
    summary="Listar todas las leyes indexadas",
    description="Devuelve los metadatos de todas las leyes almacenadas en BD.",
)
async def listar_leyes(repo: LeyRepositoryBase = Depends(get_repository)) -> list[LeyMetadata]:
    return await repo.list_all()


@router.get(
    "/{identifier}",
    response_model=LeyMetadata,
    summary="Obtener una ley por identificador",
    description="Devuelve los metadatos de una ley concreta. Ejemplo: BOE-A-2015-11430",
)
async def obtener_ley(identifier: str, repo: LeyRepositoryBase = Depends(get_repository)) -> LeyMetadata:
    
    ley = await repo.get(identifier)
    if ley is None:
        raise HTTPException(status_code=404, detail=f"Ley '{identifier}' no encontrada.")
    metadata, _ = ley
    return metadata


