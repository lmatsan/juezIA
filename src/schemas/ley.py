from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

class RangoNormativo(str, Enum):
    CONSTITUCION     = "Constitución"
    LEY_ORGANICA     = "Ley Orgánica"
    LEY              = "Ley"
    REAL_DECRETO_LEY = "Real Decreto-ley"
    REAL_DECRETO     = "Real Decreto"
    ORDEN_MINISTERIAL = "Orden"
    RESOLUCION       = "Resolución"
    OTRO             = "Otro"

class EstadoNormativo(str, Enum):
    VIGENTE     = "vigente"
    DEROGADO    = "derogado"
    MODIFICADO  = "modificado"
    DESCONOCIDO = "desconocido"

class LeyMetadata(BaseModel):
    """
    Metadatos de una norma BOE extraídos del frontmatter YAML de legalize-es.
    """

    # Identificación
    identifier: str = Field(
        ...,
        description="Identificador BOE canónico. Clave primaria en ChromaDB.",
        examples=["BOE-A-2015-11430"],
    )
    title: str = Field(
        ...,
        description="Título oficial de la norma.",
    )
    eli: Optional[str] = Field(
        default=None,
        description="European Legislation Identifier (ELI) de la norma, si está disponible. ",
        examples=["https://www.boe.es/eli/es/rdlg/2015/10/23/2/con"],
    )

    # Clasificación
    rank: RangoNormativo = Field(
        default=RangoNormativo.OTRO,
        description="Rango normativo de la norma.",
    )
    department: Optional[str] = Field(
        default=None,
        description="Ministerio u organismo emisor.",
    )
    subjects: list[str] = Field(
        default_factory=list,
        description="Materias temáticas. Útil para filtrado semántico.",
    )

    # Fechas y estado
    publication_date: Optional[date] = Field(
        default=None,
        description="Fecha de publicación en el BOE.",
    )
    last_updated: Optional[date] = Field(
        default=None,
        description="Fecha de la última reforma consolidada. "
                    "Usada por sync_leyes.py para evitar reingestas innecesarias.",
    )
    status: EstadoNormativo = Field(
        default=EstadoNormativo.DESCONOCIDO,
        description="Estado jurídico actual de la norma.",
    )

    @field_validator("rank", mode="before")
    @classmethod
    def normalizar_rank(cls, v: str) -> str:
        mapping = {
            "constitucion":      RangoNormativo.CONSTITUCION,
            "constitución":      RangoNormativo.CONSTITUCION,
            "ley organica":      RangoNormativo.LEY_ORGANICA,
            "ley orgánica":      RangoNormativo.LEY_ORGANICA,
            "ley":               RangoNormativo.LEY,
            "real decreto-ley":  RangoNormativo.REAL_DECRETO_LEY,
            "real decreto ley":  RangoNormativo.REAL_DECRETO_LEY,
            "real decreto":      RangoNormativo.REAL_DECRETO,
            "orden":             RangoNormativo.ORDEN_MINISTERIAL,
            "resolución":        RangoNormativo.RESOLUCION,
            "resolucion":        RangoNormativo.RESOLUCION,
        }
        return mapping.get(str(v).lower().strip(), RangoNormativo.OTRO)

    @field_validator("status", mode="before")
    @classmethod
    def normalizar_status(cls, v: str) -> str:
        mapping = {
            "vigente":   EstadoNormativo.VIGENTE,
            "active":    EstadoNormativo.VIGENTE,
            "derogado":  EstadoNormativo.DEROGADO,
            "derogada":  EstadoNormativo.DEROGADO,
            "repealed":  EstadoNormativo.DEROGADO,
            "modificado": EstadoNormativo.MODIFICADO,
            "modified":  EstadoNormativo.MODIFICADO,
            "amended":   EstadoNormativo.MODIFICADO,
        }
        return mapping.get(str(v).lower().strip(), EstadoNormativo.DESCONOCIDO)

    model_config = {
        "str_strip_whitespace": True,
        "populate_by_name": True,
    }
