"""
app/services/correo_service.py

Envio de correo desde la tienda. Usa smtplib y email.message, que vienen
con Python: no hace falta instalar Flask-Mail ni ninguna otra libreria.

La cuenta que firma los correos se configura en .env (MAIL_USUARIO y
MAIL_CONTRASENA). Con Gmail, MAIL_CONTRASENA **no** es la contrasena de la
cuenta sino una "contrasena de aplicacion" de 16 letras; el README explica
como sacarla.

Si la cuenta no esta configurada, el proyecto no se rompe: con
MAIL_A_CONSOLA activo (lo normal en desarrollo, porque sigue a
FLASK_DEBUG) el mensaje se imprime en la consola de Flask -codigo de
verificacion incluido- y el flujo continua como si hubiera salido, asi que
la recuperacion se puede demostrar sin credenciales. Con MAIL_A_CONSOLA
apagado se responde con un error claro en vez de fingir el envio.
"""
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from flask import current_app


class CorreoNoEnviado(Exception):
    """El correo no salio. El mensaje explica por que, en español."""


def esta_configurado():
    """True si en .env hay una cuenta de envio con usuario y contrasena."""
    cfg = current_app.config
    return bool(cfg.get("MAIL_USUARIO") and cfg.get("MAIL_CONTRASENA"))


def enviar(destinatario, asunto, texto, html=None):
    """
    Manda un correo. 'texto' es la version en texto plano (obligatoria,
    es la que ven los lectores que no muestran HTML) y 'html' la version
    con formato, opcional.

    Levanta CorreoNoEnviado si el servidor rechaza el envio.
    """
    cfg = current_app.config

    if not esta_configurado():
        # Una cosa o la otra, nunca las dos: volcar el mensaje en la consola
        # *y* ademas fallar dejaria en pantalla un codigo que el servicio
        # acaba de invalidar.
        if cfg.get("MAIL_A_CONSOLA"):
            _volcar_en_consola(destinatario, asunto, texto)
            return False
        raise CorreoNoEnviado(
            "El envio de correo no esta configurado en el servidor. "
            "Escribenos a " + cfg["EMPRESA"]["correo"] + " para continuar."
        )

    # Gmail exige que el remitente sea la misma cuenta con la que se
    # autentico, asi que si MAIL_REMITENTE quedo vacio se usa MAIL_USUARIO
    # en vez de mandar un "From" sin direccion (que el servidor rechaza).
    remitente = cfg.get("MAIL_REMITENTE") or cfg["MAIL_USUARIO"]

    mensaje = EmailMessage()
    mensaje["Subject"] = asunto
    mensaje["From"] = formataddr((cfg.get("MAIL_NOMBRE_REMITENTE") or "", remitente))
    mensaje["To"] = destinatario
    mensaje.set_content(texto)
    if html:
        mensaje.add_alternative(html, subtype="html")

    try:
        _entregar(mensaje)
    except (smtplib.SMTPException, OSError) as e:
        # El detalle tecnico va al log del servidor; a la persona solo se le
        # dice que no se pudo enviar (un error de SMTP crudo no le sirve y
        # puede filtrar datos del servidor).
        current_app.logger.error("No se pudo enviar el correo a %s: %s", destinatario, e)
        raise CorreoNoEnviado(
            "No pudimos enviar el correo en este momento. Intenta de nuevo en unos minutos."
        ) from e

    return True


def _entregar(mensaje):
    """Abre la conexion con el servidor SMTP y entrega el mensaje."""
    cfg = current_app.config
    servidor = cfg["MAIL_SERVIDOR"]
    puerto = int(cfg["MAIL_PUERTO"])
    usuario = cfg["MAIL_USUARIO"]
    contrasena = cfg["MAIL_CONTRASENA"]
    tiempo_limite = int(cfg.get("MAIL_TIEMPO_LIMITE", 15))
    contexto = ssl.create_default_context()

    # Puerto 465 = SSL desde el saludo inicial; 587 = conexion normal que
    # se cifra despues con STARTTLS. Gmail acepta los dos.
    if cfg.get("MAIL_USAR_SSL"):
        with smtplib.SMTP_SSL(servidor, puerto, timeout=tiempo_limite, context=contexto) as smtp:
            smtp.login(usuario, contrasena)
            smtp.send_message(mensaje)
        return

    with smtplib.SMTP(servidor, puerto, timeout=tiempo_limite) as smtp:
        smtp.ehlo()
        if cfg.get("MAIL_USAR_TLS", True):
            smtp.starttls(context=contexto)
            smtp.ehlo()
        smtp.login(usuario, contrasena)
        smtp.send_message(mensaje)


def _volcar_en_consola(destinatario, asunto, texto):
    """
    Plan B de desarrollo: sin cuenta de correo configurada, el mensaje se
    escribe en la consola de Flask para poder seguir probando el flujo.

    Va por logger.warning y no por print para que salga tambien cuando la
    salida estandar este redirigida a un archivo de log.
    """
    borde = "-" * 62
    current_app.logger.warning(
        "\n%s\n[CORREO SIN ENVIAR — falta configurar MAIL_USUARIO en .env]\n"
        "Para:   %s\nAsunto: %s\n%s\n%s\n%s",
        borde, destinatario, asunto, borde, texto, borde,
    )
