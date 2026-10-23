"""
app/services/chatbot_service.py

Motor de respuestas automaticas del chat de atencion basica. Cada caso que
el bot sabe responder es una entrada en INTENCIONES: una lista de palabras
clave y la funcion que arma la respuesta. Agregar un caso nuevo es agregar
una entrada a esa lista (o registrarla con @intencion), sin tocar la logica
de deteccion ni las demas respuestas.

Es deteccion por palabras clave, no un modelo de lenguaje: suficiente para
un chat de atencion basica con un puñado de temas fijos (horarios, compras,
pagos, catalogo). Si el mensaje no calza con ninguna, se devuelve una
respuesta por defecto que ofrece contacto humano.
"""
import unicodedata

from flask import current_app

from app.services.producto_service import ProductoService

INTENCIONES = []


def intencion(nombre, palabras):
    """
    Decorador para registrar un caso nuevo: la funcion decorada recibe el
    mensaje original del usuario y devuelve el texto de la respuesta.
    Quien agregue un caso solo escribe la funcion y la decora; no necesita
    tocar ChatbotService.responder().
    """
    def registrar(func):
        INTENCIONES.append({"nombre": nombre, "palabras": palabras, "responder": func})
        return func
    return registrar


def _normalizar(texto):
    """Minusculas y sin tildes, para que la deteccion no dependa de acentos."""
    sin_tildes = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode("ascii")
    return sin_tildes.lower()


# ----------------------------------------------------------------------
# Casos cubiertos (orden: del mas especifico al mas general; el saludo va
# de ultimo para no "robarle" el mensaje a una pregunta mas concreta que
# tambien empiece con un saludo, ej. "hola, como pago mi pedido").
# ----------------------------------------------------------------------

@intencion(
    "compra_pedido",
    ["comprar", "compro", "pedido", "orden", "mi factura", "estado de mi", "seguimiento", "rastrear", "guia de envio"],
)
def _responder_compra(mensaje):
    return (
        "Para comprar: entra al catálogo, agrega los productos al carrito y en el pago eliges el "
        "método y la dirección de envío. Si ya hiciste un pedido, revisa su estado y la guía de "
        "envío en «Mi perfil» → «Compras realizadas», o abre directamente tu factura."
    )


@intencion(
    "pagos_envios",
    ["pago", "pagos", "pse", "tarjeta", "transferencia", "envio", "envios", "domicilio", "cuanto cuesta el envio"],
)
def _responder_pagos_envios(mensaje):
    return (
        "Aceptamos PSE, tarjeta y transferencia bancaria. El costo del envío depende de tu dirección "
        "y se calcula automáticamente en el pago, antes de confirmar la compra."
    )


@intencion(
    "productos_categorias",
    ["producto", "productos", "categoria", "categorias", "catalogo", "tienen", "venden", "alimento", "juguete", "buscar"],
)
def _responder_productos(mensaje):
    categorias = ProductoService.listar_categorias()
    nombres = ", ".join(c.nombre for c in categorias) or "perros, gatos y otras mascotas"
    return (
        f"Manejamos productos para: {nombres}. Puedes buscarlos por nombre o código desde "
        "«Productos» en el menú, o cuéntame qué categoría te interesa y te digo qué tenemos."
    )


@intencion(
    "horarios_contacto",
    ["horario", "horarios", "atienden", "abren", "cierran", "contacto", "telefono", "direccion", "ubicacion", "donde estan", "correo"],
)
def _responder_horarios(mensaje):
    empresa = current_app.config["EMPRESA"]
    # empresa['horario'] ya termina en punto ("...6:00 p.m."), por eso no se agrega otro aqui.
    return (
        f"Atendemos {empresa['horario'].lower()} Puedes escribirnos a {empresa['correo']} o "
        f"llamarnos al {empresa['telefono']}. Estamos en {empresa['direccion']}, {empresa['ciudad']}."
    )


@intencion("saludo", ["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "que mas", "hey"])
def _responder_saludo(mensaje):
    return (
        "¡Hola! Soy Chantonieta, el asistente de Bones & Paws. Puedo ayudarte con horarios y contacto, "
        "cómo comprar o el estado de un pedido, métodos de pago y envío, o el catálogo de productos. "
        "¿En qué te ayudo?"
    )


def _respuesta_por_defecto():
    empresa = current_app.config["EMPRESA"]
    return (
        "No estoy seguro de haber entendido tu pregunta. Puedo ayudarte con horarios y contacto, "
        "cómo comprar o el estado de un pedido, métodos de pago y envío, o el catálogo de "
        "productos. Si prefieres hablar con una persona, escríbenos a "
        f"{empresa['correo']} o visita la sección de Contacto."
    )


class ChatbotService:

    @staticmethod
    def responder(mensaje):
        """
        Devuelve {"respuesta": str, "intencion": str|None} para un mensaje
        del usuario. Recorre INTENCIONES en orden y usa la primera cuyas
        palabras clave aparezcan en el mensaje normalizado (sin tildes ni
        mayusculas). Si ninguna coincide, devuelve la respuesta por defecto
        con la opcion de escribir a contacto humano.
        """
        texto = _normalizar(mensaje)
        if not texto.strip():
            return {"respuesta": "Escribe tu pregunta y te ayudo con gusto.", "intencion": None}

        for caso in INTENCIONES:
            if any(palabra in texto for palabra in caso["palabras"]):
                return {"respuesta": caso["responder"](mensaje), "intencion": caso["nombre"]}

        return {"respuesta": _respuesta_por_defecto(), "intencion": None}
