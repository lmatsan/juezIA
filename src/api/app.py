from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

# IMPORTACIONES DE NUESTROS NUEVOS ARCHIVOS
from src.models.caso import CuestionarioFalsoAutonomo
from src.services.analisis import AnalizadorService

# INICIALIZACIÓN
app = FastAPI(title="JuezIA API - PMMV", description="JuezIA API - PMMV", version="1.0.0")

# CONFIGURACIÓN DE LOGS
logging.basicConfig(
    filename='errores_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

# MANEJADOR DE ERRORES
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    friendly_message = error.get("msg")
    affected_field = error.get("loc")[-1]

    # GUARDAR EN EL ARCHIVO LOG
    logging.warning(f"Validation error in '{affected_field}': {friendly_message}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid data",
            "message": f"{error['loc'][-1]}: {error['msg']}"
        }
    )

# ENDPOINTS DE LA API
@app.get("/")
def read_root():
    return {"status": "JuezIA API Running"}

@app.post("/analizar")
async def analizar_caso(cuestionario: CuestionarioFalsoAutonomo):
    # 1. Se transforma el modelo a diccionario
    datos = cuestionario.dict()
    
    # 2. Se llama a los servicios dummy
    prob = AnalizadorService.calcular_probabilidad(datos)
    consejo = AnalizadorService.generar_consejo_ia(prob)
    
    # 3. Respuesta que leerá el Chatbot
    return {
        "probabilidad_laboralidad": f"{prob}%",
        "recomendacion": consejo,
        "mensaje": "Análisis realizado con motor experimental PMMV"
    }