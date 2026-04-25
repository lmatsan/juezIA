import pytest
import sys
import os

# Se fuerza la raíz del proyecto para que Python encuentre la carpeta 'src'
# Esto añade la raíz del proyecto al path para que los tests 
# puedan hacer 'from src.api... import ...' sin errores.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))