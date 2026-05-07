import requests
import time
import json
from pathlib import Path
from datetime import datetime

TOKEN = "8726779674:AAGzRxWTQ21fE_iHNwSy5t_rbqQBdkOdiL0"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

PREGUNTAS = [
    {
        "categoria": "Dependencia",
        "campo": "centro_trabajo_impuesto",
        "pregunta": "¿Asistes todos los días a un centro de trabajo impuesto por la empresa?",
        "tipo": "boolean"
    },
    {
        "categoria": "Ajenidad",
        "campo": "marca_imagen",
        "pregunta": "¿La marca y la imagen pertenecen a la empresa?",
        "tipo": "boolean"
    },
    {
        "categoria": "Dependencia y ajenidad",
        "campo": "facturacion",
        "pregunta": "Sonrie si alguna vez te han hecho TRAS TRAS por detras",
        "tipo": "texto"
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


def texto_a_booleano(texto):
    texto = texto.strip().lower()

    if texto in ["si", "sí", "s", "yes", "y"]:
        return True

    if texto in ["no", "n"]:
        return False

    return None


def guardar_resultado(chat_id, sesion):
    carpeta = Path("casos")
    carpeta.mkdir(exist_ok=True)

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    archivo = carpeta / f"caso_{chat_id}_{fecha}.json"

    salida = {
        "fecha_creacion": fecha,
        "telegram_user": sesion["telegram_user"],
        "respuestas": sesion["respuestas"]
    }

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=4)

    print(f"Archivo creado en: {archivo.resolve()}")

    return archivo


def obtener_bloque(categoria):
    if categoria == "Dependencia":
        return "dependencia"

    if categoria == "Ajenidad":
        return "ajenidad"

    return "dependencia_y_ajenidad"


def enviar_pregunta(chat_id, pregunta):
    extra = (
        "\n\nResponde: sí o no"
        if pregunta.get("tipo", "texto") == "boolean"
        else "\n\nResponde con texto libre"
    )

    enviar_mensaje(
        chat_id,
        f"{pregunta['categoria']}\n\n{pregunta['pregunta']}{extra}"
    )


def iniciar_sesion(chat_id, usuario_telegram):
    sesiones[chat_id] = {
        "indice": 0,
        "telegram_user": usuario_telegram,
        "respuestas": {
            "dependencia": {},
            "ajenidad": {},
            "dependencia_y_ajenidad": {}
        }
    }

    enviar_pregunta(chat_id, PREGUNTAS[0])


def procesar_respuesta(chat_id, texto):
    sesion = sesiones[chat_id]

    indice = sesion["indice"]

    pregunta_actual = PREGUNTAS[indice]

    categoria = pregunta_actual["categoria"]
    campo = pregunta_actual["campo"]
    tipo = pregunta_actual.get("tipo", "texto")

    bloque = obtener_bloque(categoria)

    if tipo == "boolean":
        valor = texto_a_booleano(texto)

        if valor is None:
            enviar_mensaje(
                chat_id,
                "Respuesta no válida. Por favor responde solo: sí o no"
            )
            return

        sesion["respuestas"][bloque][campo] = {
    "pregunta": pregunta_actual["pregunta"],
    "respuesta": valor
}

    else:
        sesion["respuestas"][bloque][campo] = {
    "pregunta": pregunta_actual["pregunta"],
    "respuesta": texto
}

    sesion["indice"] += 1

    if sesion["indice"] >= len(PREGUNTAS):
        archivo = guardar_resultado(chat_id, sesion)

        enviar_mensaje(
            chat_id,
            f"Cuestionario terminado.\n\nHe guardado el caso en:\n{archivo.name}"
        )

        del sesiones[chat_id]
        return

    siguiente = PREGUNTAS[sesion["indice"]]

    enviar_pregunta(chat_id, siguiente)


print("Bot de JuezIA iniciado...")


while True:
    params = {}

    if ultimo_update_id is not None:
        params["offset"] = ultimo_update_id + 1

    params["timeout"] = 30

    try:
        response = requests.get(
            f"{BASE_URL}/getUpdates",
            params=params,
            timeout=35
        )

        data = response.json()

        print(data)

        for update in data.get("result", []):
            ultimo_update_id = update["update_id"]

            message = update.get("message", {})

            chat = message.get("chat", {})
            from_user = message.get("from", {})

            chat_id = chat.get("id")
            texto = message.get("text", "")

            usuario_telegram = {
                "id": from_user.get("id"),
                "is_bot": from_user.get("is_bot"),
                "first_name": from_user.get("first_name"),
                "last_name": from_user.get("last_name"),
                "username": from_user.get("username"),
                "language_code": from_user.get("language_code"),
                "chat_id": chat.get("id"),
                "chat_type": chat.get("type")
            }

            if not chat_id or not texto:
                continue

            print(f"Mensaje recibido: {texto}")

            if texto.lower() in ["/start", "start", "iniciar"]:
                enviar_mensaje(
                    chat_id,
                    "Hola. Soy JuezIA.\n\nVoy a hacerte unas preguntas para analizar indicios de dependencia y ajenidad."
                )

                iniciar_sesion(chat_id, usuario_telegram)

            elif chat_id in sesiones:
                procesar_respuesta(chat_id, texto)

            else:
                enviar_mensaje(
                    chat_id,
                    "Para empezar el cuestionario escribe /start"
                )

    except requests.exceptions.RequestException as error:
        print(f"Error de conexión con Telegram: {error}")

    except Exception as error:
        print(f"Error inesperado: {error}")

    time.sleep(1)
    