# ⚖️ Juez IA --- Proyecto Júpiter
Juez IA es el Trabajo de Fin de Máster del Máster en Inteligencia Artificial, Cloud Computing y DevOps. El proyecto explora el diseño de un sistema basado en IA generativa capaz de analizar casos complejos, recuperar información relevante y generar decisiones argumentadas, trazable y desplegada bajo buenas prácticas DevOps.

## 🎯 Objetivo

Diseñar e implementar un **MVP funcional** que combine:

-   Modelos de IA generativa (LLMs)\
-   Base de datos vectorial\
-   Arquitectura cloud-native\
-   Pipeline DevOps completo (CI/CD)\
-   Monitorización y métricas de uso

El proyecto no busca reemplazar el juicio humano, sino analizar hasta qué punto la IA puede estructurar, justificar y documentar decisiones complejas bajo criterios definidos.

## 🚧 Estado del proyecto

🟡 Fase inicial --- definición de alcance, arquitectura y caso de uso
definitivo. 

## 🐳⚙️ Uso de Docker Compose

Para levantar el proyecto en local utilizando **Docker Compose**, es necesario seguir los siguientes pasos:

### 1. Construir y arrancar los contenedores

Ejecutar el siguiente comando desde la raíz del proyecto, donde se encuentra el archivo `docker-compose.yml`:

```bash
docker compose up --build
```

Este comando construye o reconstruye la imagen desde el `Dockerfile` y arranca los contenedores definidos en `docker-compose.yml`.

### 2. Validar que la aplicación está funcionando

Una vez que los contenedores estén levantados correctamente, abrir un navegador y acceder a:

```text
http://localhost:8080/docs
```

Si todo funciona correctamente, debería mostrarse la documentación interactiva de la API.

### 3. Detener los contenedores

Para detener la ejecución de los contenedores, se puede usar:

```bash
docker compose down
```

Este comando detiene y elimina los contenedores creados por Docker Compose.