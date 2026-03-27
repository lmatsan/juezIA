from pydantic import BaseModel
from typing import Optional

class CuestionarioAutonomo(BaseModel):
    nombre_usuario: str
    herramientas_propias: bool  # ¿Los medios de producción son suyos?
    horario_libre: bool         # ¿Decide su propio horario?
    recibe_ordenes: bool        # ¿Recibe órdenes directas?
    facturacion_fija: bool      # ¿Factura siempre lo mismo al mismo cliente?
    tiempo_autonomo: int        # Meses de antigüedad