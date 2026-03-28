from pydantic import BaseModel, Field
from typing import Optional

class CuestionarioFalsoAutonomo(BaseModel):
    # Usamos valores de 0 a 1 para que el ML lo entienda mejor después
    herramientas_empresa: bool = Field(..., description="¿Los medios son de la empresa?")
    horario_impuesto: bool = Field(..., description="¿El horario lo fija el cliente?")
    instrucciones_directas: bool = Field(..., description="¿Recibe órdenes de un superior?")
    ajenidad_clientes: bool = Field(..., description="¿La cartera de clientes es de la empresa?")
    retribucion_fija: bool = Field(..., description="¿Cobra lo mismo cada mes sin riesgo?")
    exclusividad_de_facto: bool = Field(..., description="¿Trabaja solo para este cliente?")