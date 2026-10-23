"""
app/services/recuperacion_service.py

Recuperar la contrasena con un codigo que llega al correo del cliente.

El flujo tiene dos pasos, y cada uno es una ruta distinta:

  1. solicitar_codigo(documento, correo)
     Comprueba que el documento y el correo sean de un mismo cliente,
     sortea un codigo de 6 digitos, lo guarda **hasheado** en la tabla
     `codigo_recuperacion` con vencimiento de 15 minutos y lo manda al
     correo registrado.

  2. restablecer(documento, correo, codigo, nueva_contrasena)
     Busca el ultimo codigo vigente de ese cliente, lo compara y recien
     ahi cambia la contrasena. Cada codigo sirve una sola vez.

Por que un codigo de 6 digitos y no un enlace con token: el enlace exige
que el correo sepa a que dominio apuntar, y este proyecto corre en
localhost con un puerto que cambia de equipo a equipo. Un codigo que la
persona copia en el mismo formulario donde lo pidio no depende de eso.

Defensas
--------
- Se piden documento + correo, no solo el correo: quien no conozca los dos
  datos no puede disparar correos a la cuenta de otra persona.
- Maximo 5 intentos por codigo (INTENTOS_MAXIMOS); al sexto, el codigo
  queda quemado y hay que pedir otro.
- Solo se admite un codigo vigente a la vez: pedir uno nuevo anula el
  anterior, para que no queden varios codigos validos dando vueltas.
- Espera minima entre envios (ESPERA_ENTRE_ENVIOS_SEGUNDOS), para que el
  boton no se pueda usar como maquina de spam contra el correo del cliente.
"""
import secrets
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import Cliente, CodigoRecuperacion
from app.models.codigo_recuperacion import INTENTOS_MAXIMOS, VIGENCIA_MINUTOS
from app.services import correo_service

LONGITUD_CODIGO = 6
ESPERA_ENTRE_ENVIOS_SEGUNDOS = 60
LONGITUD_MINIMA_CONTRASENA = 6


def _generar_codigo():
    """
    Codigo de 6 digitos con el generador criptografico de Python
    (secrets, no random: random es predecible si se conoce su estado).
    """
    numero = secrets.randbelow(10 ** LONGITUD_CODIGO)
    return str(numero).zfill(LONGITUD_CODIGO)


def _buscar_cliente(documento, correo):
    documento = (documento or "").strip()
    correo = (correo or "").strip()
    if not documento or not correo:
        raise ValueError("Escribe tu número de documento y tu correo.")

    cliente = Cliente.query.filter_by(id_usuario=documento, correo=correo).first()
    if not cliente:
        raise ValueError(
            "No encontramos una cuenta con ese número de documento y ese correo."
        )
    return cliente


def solicitar_codigo(documento, correo):
    """
    Paso 1. Manda el codigo al correo del cliente y devuelve el correo
    enmascarado (ej. 'an**************s@gmail.com') para confirmarle a
    donde fue sin repetir la direccion completa en la pantalla.
    """
    cliente = _buscar_cliente(documento, correo)

    pendiente = _ultimo_vigente(cliente.id_usuario)
    if pendiente:
        segundos = (datetime.now() - pendiente.creado_en).total_seconds()
        if segundos < ESPERA_ENTRE_ENVIOS_SEGUNDOS:
            espera = int(ESPERA_ENTRE_ENVIOS_SEGUNDOS - segundos)
            raise ValueError(
                "Ya te enviamos un código. Revisa tu correo o espera "
                + str(espera)
                + " segundos para pedir otro."
            )

    # Los codigos anteriores se invalidan: solo el ultimo sirve.
    _anular_pendientes(cliente.id_usuario)

    codigo = _generar_codigo()
    registro = CodigoRecuperacion(
        id_usuario=cliente.id_usuario,
        codigo_hash=generate_password_hash(codigo),
        creado_en=datetime.now(),
        expira_en=CodigoRecuperacion.vencimiento_desde_ahora(),
    )
    db.session.add(registro)
    db.session.commit()

    try:
        correo_service.enviar(
            destinatario=cliente.correo,
            asunto="Tu código para recuperar la contraseña: " + codigo,
            texto=_texto_plano(cliente, codigo),
            html=_texto_html(cliente, codigo),
        )
    except correo_service.CorreoNoEnviado:
        # Si el correo no salio, el codigo no le sirve a nadie: se descarta
        # para que la persona pueda reintentar de inmediato sin toparse con
        # la espera entre envios.
        db.session.delete(registro)
        db.session.commit()
        raise

    return enmascarar_correo(cliente.correo)


def restablecer(documento, correo, codigo, nueva_contrasena):
    """
    Paso 2. Valida el codigo y cambia la contrasena.
    """
    cliente = _buscar_cliente(documento, correo)

    codigo = (codigo or "").strip().replace(" ", "")
    if not codigo:
        raise ValueError("Escribe el código que te llegó al correo.")
    if len(nueva_contrasena or "") < LONGITUD_MINIMA_CONTRASENA:
        raise ValueError(
            "La nueva contraseña debe tener al menos "
            + str(LONGITUD_MINIMA_CONTRASENA)
            + " caracteres."
        )

    registro = _ultimo_vigente(cliente.id_usuario)
    if not registro:
        raise ValueError("El código venció o ya se usó. Pide uno nuevo para continuar.")

    if not check_password_hash(registro.codigo_hash, codigo):
        registro.intentos += 1
        db.session.commit()

        restantes = INTENTOS_MAXIMOS - registro.intentos
        if restantes <= 0:
            raise ValueError(
                "Código incorrecto. Agotaste los intentos de este código: pide uno nuevo."
            )
        if restantes == 1:
            raise ValueError("Código incorrecto. Te queda 1 intento.")
        raise ValueError("Código incorrecto. Te quedan " + str(restantes) + " intentos.")

    cliente.contrasena = generate_password_hash(nueva_contrasena)
    registro.usado = True
    db.session.commit()
    return cliente


def _ultimo_vigente(id_usuario):
    """
    El codigo mas reciente de ese cliente que todavia se puede usar: sin
    usar, sin vencer y sin agotar los intentos.
    """
    return (
        CodigoRecuperacion.query
        .filter_by(id_usuario=id_usuario, usado=False)
        .filter(CodigoRecuperacion.expira_en > datetime.now())
        .filter(CodigoRecuperacion.intentos < INTENTOS_MAXIMOS)
        .order_by(CodigoRecuperacion.creado_en.desc())
        .first()
    )


def _anular_pendientes(id_usuario):
    CodigoRecuperacion.query.filter_by(id_usuario=id_usuario, usado=False).update(
        {"usado": True}, synchronize_session=False
    )
    db.session.commit()


def limpiar_vencidos(dias=7):
    """
    Borra los codigos viejos. No lo necesita el flujo -un codigo vencido
    ya no sirve-, pero evita que la tabla crezca para siempre.
    """
    limite = datetime.now() - timedelta(days=dias)
    borrados = CodigoRecuperacion.query.filter(
        CodigoRecuperacion.creado_en < limite
    ).delete(synchronize_session=False)
    db.session.commit()
    return borrados


def enmascarar_correo(correo):
    """
    'antonietawsnpaws@gmail.com' -> 'an*************s@gmail.com'

    Sirve para confirmar a donde se mando el codigo sin escribir la
    direccion completa en una pantalla que puede estar a la vista de otros.
    """
    usuario, _, dominio = (correo or "").partition("@")
    if not dominio:
        return correo
    if len(usuario) <= 3:
        return usuario[:1] + "*" * max(len(usuario) - 1, 1) + "@" + dominio
    return usuario[:2] + "*" * (len(usuario) - 3) + usuario[-1] + "@" + dominio


# ----------------------------------------------------------------------
# Cuerpo del correo
# ----------------------------------------------------------------------
def _texto_plano(cliente, codigo):
    return (
        "Hola " + cliente.nombre + ",\n\n"
        "Pediste restablecer la contraseña de tu cuenta de Bones & Paws.\n\n"
        "Tu código de verificación es: " + codigo + "\n\n"
        "Escríbelo en la ventana de recuperación. Vence en "
        + str(VIGENCIA_MINUTOS)
        + " minutos y solo se puede usar una vez.\n\n"
        "Si no fuiste tú, ignora este mensaje: tu contraseña sigue igual y "
        "nadie puede cambiarla sin este código.\n\n"
        "— El equipo de Bones & Paws\n"
        "Este es un correo automático, no hace falta responderlo.\n"
    )


def _texto_html(cliente, codigo):
    # Estilos en linea (no una hoja aparte): los clientes de correo
    # descartan el CSS externo y buena parte del que va en <style>.
    return (
        '<!doctype html>\n'
        '<html lang="es">\n'
        '<body style="margin:0;padding:24px;background:#faf7f5;'
        'font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#3f3a38;">\n'
        '  <div style="max-width:480px;margin:0 auto;background:#ffffff;'
        'border-radius:16px;padding:32px;border:1px solid #f0e4e4;">\n'
        '    <h1 style="margin:0 0 4px;font-size:20px;color:#9d174d;">Bones &amp; Paws</h1>\n'
        '    <p style="margin:0 0 24px;font-size:13px;color:#8a7f7c;">'
        'Recuperación de contraseña</p>\n'
        '    <p style="margin:0 0 16px;font-size:15px;">Hola <strong>'
        + cliente.nombre +
        '</strong>,</p>\n'
        '    <p style="margin:0 0 24px;font-size:15px;line-height:1.5;">\n'
        '      Pediste restablecer la contraseña de tu cuenta. Este es tu '
        'código de verificación:\n'
        '    </p>\n'
        '    <div style="text-align:center;margin:0 0 24px;">\n'
        '      <span style="display:inline-block;padding:14px 26px;background:#fdf2f6;'
        'border:1px dashed #e8b4c8;border-radius:12px;font-size:30px;font-weight:700;'
        'letter-spacing:8px;color:#9d174d;">'
        + codigo +
        '</span>\n'
        '    </div>\n'
        '    <p style="margin:0 0 16px;font-size:14px;line-height:1.5;">\n'
        '      Escríbelo en la ventana de recuperación de la tienda. Vence en\n'
        '      <strong>' + str(VIGENCIA_MINUTOS) + ' minutos</strong> y solo se '
        'puede usar una vez.\n'
        '    </p>\n'
        '    <p style="margin:0 0 24px;font-size:13px;color:#8a7f7c;line-height:1.5;">\n'
        '      Si no fuiste tú, puedes ignorar este mensaje: tu contraseña sigue igual\n'
        '      y nadie puede cambiarla sin este código.\n'
        '    </p>\n'
        '    <hr style="border:none;border-top:1px solid #f0e4e4;margin:0 0 16px;" />\n'
        '    <p style="margin:0;font-size:12px;color:#a69b98;">\n'
        '      Correo automático de Bones &amp; Paws. No hace falta responderlo.\n'
        '    </p>\n'
        '  </div>\n'
        '</body>\n'
        '</html>'
    )
