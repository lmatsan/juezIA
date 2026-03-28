import random

class AnalizadorService:
    @staticmethod
    def calcular_probabilidad(datos: dict) -> float:
        # Se definen los pesos de cada indicio (Total = 100)obabilidad sube
        PESOS = {
            "instrucciones_directas": 30,  # El indicio más fuerte de dependencia
            "herramientas_empresa": 20,    # Indicio clave de ajenidad en los medios
            "retribucion_fija": 20,        # Indicio de ajenidad en la retribución
            "horario_impuesto": 15,        # Control del tiempo
            "ajenidad_clientes": 10,       # Ajenidad en el mercado
            "exclusividad_de_facto": 5     # Indicio concomitante
        }
        
        probabilidad = 0.0
        
        # Iteramos sobre los datos recibidos y sumamos si el valor es True
        for indicio, peso in PESOS.items():
            if datos.get(indicio) is True:
                probabilidad += peso
                
        return float(probabilidad)

    @staticmethod
    def generar_consejo_ia(probabilidad: float) -> str:
        if probabilidad > 70:
            return "Alta probabilidad de falso autónomo. Se recomienda recopilar emails con órdenes directas y facturas correlativas."
        return "Indicios insuficientes. Sería necesario analizar la exclusividad del contrato."