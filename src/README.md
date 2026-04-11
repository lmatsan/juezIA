## 📂 Estructura del Proyecto

El código sigue una arquitectura modular y profesional, separando la lógica de negocio de la infraestructura y asegurando la calidad mediante una suite de pruebas externa al código fuente:

* **`.venv/`**: Entorno virtual de Python donde se gestionan las dependencias de forma aislada.
* **`src/`**: Carpeta principal que contiene el código fuente de la aplicación.
    * **`api/v1/`**: Versión 1 de la API. Contiene `app.py`, que registra los routers y configura FastAPI.
    * **`core/`**: Configuración transversal, gestión de variables de entorno (`config.py`) y excepciones personalizadas.
    * **`schemas/`**: Modelos de Pydantic para la validación de datos. 
    * **`services/`**: Capa de orquestación. `analisis.py` procesa la lógica entre la API y los módulos específicos.
    * **`modules/`**: El cerebro del asistente. Contiene la lógica jurídica organizada por jurisdicciones (ej. `laboral/autonomos`).
    * **`utils/`**: Funciones de soporte reutilizables, como parseadores de archivos o herramientas de texto.
* **`tests/`**: Ubicada en la raíz para separar el código de producción del de pruebas.
    * **`unit/`**: Pruebas unitarias de funciones y reglas aisladas.
    * **`conftest.py`**: Configuración global de Pytest y definición de fixtures.
* **`requirements.txt`**: Listado de dependencias necesarias (FastAPI, Pytest, Uvicorn, etc.).
* **`.gitignore`**: Configuración para excluir archivos temporales, logs y el entorno virtual del repositorio.
---
## 🏗️ Arquitectura del Sistema
El siguiente diagrama describe la organización modular de JuezIA, detallando el flujo de datos desde la interfaz de usuario hasta los motores de decisión clínica y legal.
```mermaid
graph TD
    subgraph Frontend_App [Carpeta: /frontend]
        UI[main.py - Interfaz Streamlit]
    end

    subgraph API_Layer [Carpeta: /src/api]
        Main[main.py - FastAPI: Endpoints + Lógica de Entrada]
    end

    subgraph Data_Models [Carpeta: /src/models]
        Pyd[caso.py - Esquemas Pydantic]
    end

    subgraph Business_Logic [Carpeta: /src/services]
        Service[analisis.py - AnalizadorService]
        AI[ai_engine.py - Conexión LLM]
    end

    subgraph ML_Assets [Carpeta: /src/data]
        Model[.pkl - Modelo Entrenado]
    end

    %% Flujo de ejecución corregido
    UI -->|1. Envía datos| Main
    Main -->|2. Valida con| Pyd
    Pyd -->|3. Retorna objeto limpio| Main
    
    Main -->|4. Llama al servicio| Service
    
    %% El "Cuadrado" de Lógica de Negocio
    Service -->|5. Predicción numérica| Model
    Model -->|6. % Probabilidad| Service
    Service -->|7. Petición de texto| AI
    AI -->|8. Recomendación legal| Service
    
    %% Cierre del ciclo
    Service -->|9. Resultado completo| Main
    Main -->|10. Respuesta JSON| UI

    %% Estética
    style UI fill:#1E3A8A,color:#fff
    style Main fill:#2563EB,color:#fff
    style Service fill:#7C3AED,color:#fff,stroke-width:4px
    style Model fill:#10B981,color:#fff
```

## 🚀 Guía de Ejecución

Puedes ejecutar este proyecto de dos formas: mediante un entorno local o usando Docker.

### Opción A: Entorno Local (Desarrollo)
#### 1. Configuración del Entorno Virtual
Es necesario crear un entorno para aislar las dependencias:
```bash
python3.11 -m venv .venv
```
Activación:
    **Windows**: 
    ```bash 
    .venv\Scripts\activate
    ```
    **macOS/Linux**: 
    ```bash 
    source .venv/bin/activate
    ```

#### 2. Instalación de Dependencias
Una vez activado el entorno, instala todos los paquetes necesarios utilizando el archivo de requerimientos: 
```bash
pip install -r requirements.txt
```

### 3. Ejecución del Servidor
Para lanzar la API, ubicate en la raiz del proyecto JuezIA:
```bash
python -m uvicorn src.api.v1.app:app --reload
```
Puedes acceder a la documentación interactiva en:
*  Swagger UI: http://127.0.0.1:8000/docs
*  ReDoc: http://127.0.0.1:8000/redoc

### Opción B: Docker (Recomendado para Despliegue)
PDTE DE IMPLEMENTAR


### 4. Poblado de Datos (Opcional)


### 5. Ejecución de Tests

## 🧪 Calidad de Código (CI)

Este proyecto utiliza **GitHub Actions** para validar cada cambio automáticamente.
* **Unit Tests:** Se ejecutan con `pytest`.
* **Coverage:** Se requiere un mínimo del 80% de cobertura de código para permitir el despliegue.