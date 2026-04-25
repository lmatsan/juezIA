import pytest
from src.services.analisis import AnalizadorService

class TestAnalizadorService:

    def test_calcular_probabilidad_maxima(self):
        """Prueba que si todos los indicios son True, la probabilidad es 100"""
        datos_completos = {
            "instrucciones_directas": True,
            "herramientas_empresa": True,
            "retribucion_fija": True,
            "horario_impuesto": True,
            "ajenidad_clientes": True,
            "exclusividad_de_facto": True
        }
        resultado = AnalizadorService.calcular_probabilidad(datos_completos)
        assert resultado == 100.0

    def test_calcular_probabilidad_nula(self):
        """Prueba que si todos los indicios son False, la probabilidad es 0"""
        datos_vacios = {
            "instrucciones_directas": False,
            "herramientas_empresa": False
        }
        resultado = AnalizadorService.calcular_probabilidad(datos_vacios)
        assert resultado == 0.0

    def test_calcular_probabilidad_parcial(self):
        """Prueba una combinación específica de indicios"""
        # Instrucciones (30) + Horario (15) = 45.0
        datos = {
            "instrucciones_directas": True,
            "horario_impuesto": True,
            "herramientas_empresa": False
        }
        resultado = AnalizadorService.calcular_probabilidad(datos)
        assert resultado == 45.0

    def test_generar_consejo_alta_probabilidad(self):
        """Prueba el mensaje cuando la probabilidad es > 70"""
        consejo = AnalizadorService.generar_consejo_ia(75.0)
        assert "Alta probabilidad" in consejo
        assert "recopilar emails" in consejo

    def test_generar_consejo_baja_probabilidad(self):
        """Prueba el mensaje cuando la probabilidad es <= 70"""
        consejo = AnalizadorService.generar_consejo_ia(40.0)
        assert "Indicios insuficientes" in consejo
        
    def test_generar_consejo_limite(self):
        """Prueba el valor frontera (70 exactamente)"""
        # Según tu código: if probabilidad > 70 (70 no entra en 'Alta')
        consejo = AnalizadorService.generar_consejo_ia(70.0)
        assert "Indicios insuficientes" in consejo