from fastapi import FastAPI
from src.models.caso import CuestionarioAutonomo
from src.services.analisis import AnalizadorService

app = FastAPI(title="JuezIA API - PMMV")

@app.get("/")
def read_root():
    return {"status": "JuezIA API Running"}

@app.post("/analizar")
async def analizar_caso(cuestionario: CuestionarioAutonomo):
    # 1. Transformamos el modelo a diccionario
    datos = cuestionario.dict()
    
    # 2. Llamamos a los servicios dummy
    prob = AnalizadorService.calcular_probabilidad(datos)
    consejo = AnalizadorService.generar_consejo_ia(prob)
    
    # 3. Respuesta que leerá el Chatbot
    return {
        "usuario": cuestionario.nombre_usuario,
        "probabilidad_laboralidad": f"{prob}%",
        "recomendacion": consejo,
        "mensaje": "Análisis realizado con motor experimental PMMV"
    }