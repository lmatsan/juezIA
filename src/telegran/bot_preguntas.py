import requests
import time
import json
from pathlib import Path

TOKEN = "8726779674:AAGzRxWTQ21fE_iHNwSy5t_rbqQBdkOdiL0"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

PREGUNTAS = [
    {
        "categoria": "Dependencia",
        "campo": "centro_trabajo_impuesto",
        "pregunta": "¿Asistes todos los días a un centro de trabajo impuesto por la empresa?"
    },
    {
        "categoria": "Dependencia",
        "campo": "horario_franjas",
        "pregunta": "¿La empresa fija el horario y las franjas de servicio? ¿Tú eliges libremente cuándo conectarte o tienes que reservar turnos/franjas con antelación en la App?"
    },
    {
        "categoria": "Dependencia",
        "campo": "geolocalizacion_constante",
        "pregunta": "¿Existe geolocalización constante?"
    },
    {
        "categoria": "Dependencia",
        "campo": "instrucciones_detalladas",
        "pregunta": "¿Hay instrucciones detalladas sobre el comportamiento? ¿La empresa te ha dado alguna guía o manual sobre cómo debes saludar al cliente o cómo colocar el casco y la mochila?"
    },
    {
        "categoria": "Dependencia",
        "campo": "permiso_ausencias",
        "pregunta": "¿Se requiere permiso para ausencias?"
    },
    {
        "categoria": "Dependencia",
        "campo": "metricas_puntuacion",
        "pregunta": "¿Existe un sistema de métricas/puntuación? ¿Sientes que si rechazas pedidos o no te conectas los fines de semana, la App te castiga dándote menos trabajo después?"
    },
    {
        "categoria": "Dependencia",
        "campo": "materiales_empresa",
        "pregunta": "¿Los materiales de trabajo son propios o son proporcionados por la empresa?"
    },
    {
        "categoria": "Dependencia",
        "campo": "otras_apps",
        "pregunta": "¿Trabajas o podrías trabajar en otras aplicaciones similares mientras estás dado de alta en esta?"
    },
    {
        "categoria": "Ajenidad",
        "campo": "materiales_trabajo",
        "pregunta": "¿Cuáles son los materiales de trabajo? Por ejemplo: método de transporte, aplicaciones, uniforme, mochila, móvil, etc."
    },
    {
        "categoria": "Ajenidad",
        "campo": "propiedad_materiales",
        "pregunta": "¿Los materiales antes citados son tuyos o de la empresa?"
    },
    {
        "categoria": "Ajenidad",
        "campo": "precio_servicio",
        "pregunta": "¿Quién fija el precio del servicio?"
    },
    {
        "categoria": "Ajenidad",
        "campo": "riesgo_empresarial",
        "pregunta": "¿El trabajador asume riesgo empresarial? Si un día no hay apenas pedidos, ¿tienes garantizado un pago mínimo por hora o solo cobras si entregas algo?"
    },
    {
        "categoria": "Ajenidad",
        "campo": "marca_imagen",
        "pregunta": "¿La marca y la imagen pertenecen a la empresa?"
    },
    {
        "categoria": "Dependencia y ajenidad",
        "campo": "facturacion",
        "pregunta": "A la hora de cobrar, ¿tú haces tu propia factura y se la envías a la empresa, o ellos te envían ya un documento hecho para que lo aceptes?"
    }
]

sesiones = {}
ultimo_update_id = None


def enviar_mensaje(chat_id, texto):
    requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": texto
        }
    )


def guardar_resultado(chat_id, respuestas):
    carpeta = Path("casos")
    carpeta.mkdir(exist_ok=True)

    archivo = carpeta / f"caso_{chat_id}.json"

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(respuestas, f, ensure_ascii=False, indent=4)

    return archivo


def iniciar_sesion(chat_id):
    sesiones[chat_id] = {
        "indice": 0,
        "respuestas": {
            "dependencia": {},
            "ajenidad": {},
            "dependencia_y_ajenidad": {}
        }
    }

    primera = PREGUNTAS[0]
    enviar_mensaje(
        chat_id,
        f"{primera['categoria']}\n\n{primera['pregunta']}"
    )


def procesar_respuesta(chat_id, texto):
    sesion = sesiones[chat_id]
    indice = sesion["indice"]

    pregunta_actual = PREGUNTAS[indice]
    categoria = pregunta_actual["categoria"]
    campo = pregunta_actual["campo"]

    if categoria == "Dependencia":
        bloque = "dependencia"
    elif categoria == "Ajenidad":
        bloque = "ajenidad"
    else:
        bloque = "dependencia_y_ajenidad"

    sesion["respuestas"][bloque][campo] = texto

    sesion["indice"] += 1

    if sesion["indice"] >= len(PREGUNTAS):
        archivo = guardar_resultado(chat_id, sesion["respuestas"])

        enviar_mensaje(
            chat_id,
            f"Cuestionario terminado.\n\nHe guardado el caso en:\n{archivo}"
        )

        del sesiones[chat_id]
        return

    siguiente = PREGUNTAS[sesion["indice"]]

    enviar_mensaje(
        chat_id,
        f"{siguiente['categoria']}\n\n{siguiente['pregunta']}"
    )


print("Bot de JuezIA iniciado...")

while True:
    params = {}

    if ultimo_update_id is not None:
        params["offset"] = ultimo_update_id + 1

    response = requests.get(
        f"{BASE_URL}/getUpdates",
        params=params
    )

    data = response.json()
    print(data)

    for update in data.get("result", []):
        ultimo_update_id = update["update_id"]

        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        texto = message.get("text", "")

        if not chat_id or not texto:
            continue

        if texto.lower() in ["/start", "start", "iniciar"]:
            enviar_mensaje(
                chat_id,
                "Hola. Soy JuezIA.\n\nVoy a hacerte unas preguntas para analizar indicios de dependencia y ajenidad.\n\nResponde con texto libre."
            )
            iniciar_sesion(chat_id)

        elif chat_id in sesiones:
            procesar_respuesta(chat_id, texto)

        else:
            enviar_mensaje(
                chat_id,
                "Para empezar el cuestionario escribe /start"
            )

    time.sleep(2)