from datetime import date
from typing import Any, Optional

import frontmatter

from src.schemas.ley import EstadoNormativo, LeyMetadata, RangoNormativo

def parsear_ley(contenido_md: str) -> tuple[LeyMetadata, str]:
    """
    Parsea el contenido crudo de un fichero .md de legalize-es.

    Devuelve una tupla (metadata, cuerpo) donde:
    - metadata: instancia validada de LeyMetadata
    - cuerpo:   texto markdown sin el bloque frontmatter

    Raises:
        ValueError: si el fichero no tiene frontmatter válido
                    o le faltan campos obligatorios (identifier, title).
    """
    try:
        post = frontmatter.loads(contenido_md)
    except Exception as exc:
        raise ValueError(f"No se pudo parsear el frontmatter: {exc}") from exc

    return _construir_metadata(post.metadata), post.content.strip()

def _construir_metadata(datos: dict[str, Any]) -> LeyMetadata:
    """
    Construye una instancia de LeyMetadata a partir de un diccionario de datos.

    Realiza validaciones adicionales para asegurar que los campos cumplen con las expectativas.
    """
    identifier = datos.get("identifier")
    title = datos.get("title")

    if not identifier:
        raise ValueError("El frontmatter no contiene el campo obligatorio 'identifier'.")
    if not title:
        raise ValueError("El frontmatter no contiene el campo obligatorio 'title'.")

    return LeyMetadata(
        identifier=identifier,
        title=title,
        eli=datos.get("eli"),
        rank=datos.get("rank", RangoNormativo.OTRO),
        department=datos.get("department"),
        subjects=_normalizar_subjects(datos.get("subjects")),
        publication_date=_normalizar_fecha(datos.get("publication_date")),
        last_updated=_normalizar_fecha(datos.get("last_updated")),
        status=datos.get("status", EstadoNormativo.DESCONOCIDO),
    )

def _normalizar_subjects(valor: Any) -> list[str]:
    if isinstance(valor, list):
        return [str(v).strip() for v in valor if str(v).strip()]
    elif isinstance(valor, str):
        return [v.strip() for v in valor.split(",") if v.strip()]
    else:
        return []
    
def _normalizar_fecha(valor: Any) -> Optional[date]:
    if isinstance(valor, date):
        return valor
    elif isinstance(valor, str):
        try:
            return date.fromisoformat(valor)
        except ValueError:
            raise ValueError(f"Fecha no válida: '{valor}'. Se esperaba formato ISO (YYYY-MM-DD).")
    else:
        return None