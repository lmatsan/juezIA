import random

class AnalizadorService:
    @staticmethod
    def calcular_probabilidad(datos: dict) -> float:
        # Simulación: si recibe órdenes y no tiene herramientas, la probabilidad sube
        score = 0
        if datos['recibe_ordenes']: score += 40
        if not datos['herramientas_propias']: score += 30
        if not datos['horario_libre']: score += 20
        
        # Añadimos un poco de aleatoriedad para el PMMV
        return min(score + random.randint(0, 10), 100)

    @staticmethod
    def generar_consejo_ia(probabilidad: float) -> str:
        if probabilidad > 70:
            return "Alta probabilidad de falso autónomo. Se recomienda recopilar emails con órdenes directas y facturas correlativas."
        return "Indicios insuficientes. Sería necesario analizar la exclusividad del contrato."