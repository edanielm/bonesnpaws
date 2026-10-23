"""
app/config.py

Configuracion central de la aplicacion. Lee todo desde variables de entorno
(.env) para no dejar credenciales ni secretos escritos en el codigo.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "bandp")

    # use_pure=true: la extension en C de mysql-connector-python se cuelga
    # (access violation) al abrir conexion en Python 3.14 de Windows; la
    # implementacion pura en Python evita el problema.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4&use_pure=true"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ------------------------------------------------------------------
    # Correo saliente (recuperacion de contrasena)
    # ------------------------------------------------------------------
    # La cuenta que firma los correos de la tienda. Con Gmail hay que usar
    # una "contrasena de aplicacion" de 16 letras (no la del correo): se
    # genera en https://myaccount.google.com/apppasswords y exige tener la
    # verificacion en dos pasos activada. El README lo explica paso a paso.
    #
    # Si MAIL_USUARIO queda vacio, la app sigue funcionando: en modo
    # desarrollo el correo -y el codigo de verificacion- se imprimen en la
    # consola de Flask en vez de enviarse.
    MAIL_SERVIDOR = os.getenv("MAIL_SERVIDOR", "smtp.gmail.com")
    MAIL_PUERTO = int(os.getenv("MAIL_PUERTO", "587"))
    # Puerto 587 -> STARTTLS (lo normal en Gmail). Puerto 465 -> SSL directo.
    MAIL_USAR_TLS = os.getenv("MAIL_USAR_TLS", "True").lower() in ("1", "true", "si", "yes")
    MAIL_USAR_SSL = os.getenv("MAIL_USAR_SSL", "False").lower() in ("1", "true", "si", "yes")
    MAIL_USUARIO = os.getenv("MAIL_USUARIO", "")
    MAIL_CONTRASENA = os.getenv("MAIL_CONTRASENA", "")
    # Gmail exige que el remitente sea la misma cuenta autenticada, asi que
    # por defecto se usa MAIL_USUARIO.
    MAIL_REMITENTE = os.getenv("MAIL_REMITENTE") or os.getenv("MAIL_USUARIO", "")
    MAIL_NOMBRE_REMITENTE = os.getenv("MAIL_NOMBRE_REMITENTE", "Bones & Paws")
    MAIL_TIEMPO_LIMITE = int(os.getenv("MAIL_TIEMPO_LIMITE", "15"))

    # Que hacer cuando no hay cuenta de correo configurada:
    #   True  -> el mensaje (con el codigo) se imprime en la consola de
    #            Flask y el flujo sigue como si hubiera salido. Sirve para
    #            demostrar la recuperacion sin credenciales.
    #   False -> se responde con un error claro, sin fingir que salio.
    #
    # Se lee de FLASK_DEBUG y no de app.config["DEBUG"] a proposito:
    # Flask reescribe DEBUG con lo que reciba app.run(debug=...), asi que
    # ese valor no es confiable para decidir esto.
    MAIL_A_CONSOLA = os.getenv(
        "MAIL_A_CONSOLA", os.getenv("FLASK_DEBUG", "True")
    ).lower() in ("1", "true", "si", "yes")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    # MAX_CONTENT_LENGTH limita la petición completa (Flask la rechaza antes
    # de llegar a la ruta); como el formulario de producto ahora permite
    # subir varias fotos a la vez, va holgado para no bloquear un lote
    # valido. MAX_IMAGE_SIZE es el limite por archivo que valida ImagenService.
    MAX_CONTENT_LENGTH = 30 * 1024 * 1024  # 30 MB por peticion (varias fotos)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB por foto
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    IVA_PORCENTAJE = 0.19  # 19% IVA Colombia

    # ------------------------------------------------------------------
    # Envio
    # ------------------------------------------------------------------
    # Antes el envio costaba siempre lo mismo sin importar a donde iba el
    # pedido. Ahora la tarifa depende de la ciudad que aparezca en la
    # direccion del cliente: Bogota es la mas barata (la tienda esta ahi) y
    # el resto sube segun la distancia. Si la direccion no menciona ninguna
    # de estas ciudades se cobra ENVIO_TARIFA_DEFECTO.
    ENVIO_TARIFAS = {
        "Bogotá": 8000,
        "Soacha": 8000,
        "Medellín": 10000,
        "Cali": 11000,
        "Bucaramanga": 11000,
        "Ibagué": 11000,
        "Villavicencio": 11000,
        "Tunja": 11000,
        "Pereira": 12000,
        "Manizales": 12000,
        "Armenia": 12000,
        "Neiva": 12000,
        "Cúcuta": 13000,
        "Barranquilla": 14000,
        "Cartagena": 14000,
        "Santa Marta": 15000,
        "Montería": 15000,
        "Sincelejo": 15000,
        "Valledupar": 15000,
        "Popayán": 15000,
        "Pasto": 16000,
    }
    ENVIO_TARIFA_DEFECTO = 14000
    # Compras grandes viajan sin costo de envio: es la promocion tipica de
    # una tienda en linea y ademas deja ver en la factura que el envio se
    # calcula, no es un valor fijo escrito a mano.
    ENVIO_GRATIS_DESDE = 250000
    # Dias habiles que tarda la entrega segun la tarifa (a mas lejos, mas
    # dias). Se usa para la fecha estimada de entrega de la guia.
    ENVIO_DIAS_ESTIMADOS = 5

    # Empleado "del sistema" al que se le atribuyen las ventas hechas por la
    # tienda en linea (nadie del equipo las atiende a mano). Es una fila
    # sembrada en `empleado`; se deja aqui para no repetir el numero suelto
    # dentro de los servicios.
    ID_EMPLEADO_SISTEMA = 999

    # ------------------------------------------------------------------
    # Paginacion
    # ------------------------------------------------------------------
    # Los listados largos (catalogo publico, catalogo del panel y cuentas de
    # clientes) ya no traen todas las filas de una sola vez.
    PRODUCTOS_POR_PAGINA = 12
    PRODUCTOS_ADMIN_POR_PAGINA = 15
    USUARIOS_POR_PAGINA = 15

    # ------------------------------------------------------------------
    # Datos del vendedor que se imprimen en la factura
    # ------------------------------------------------------------------
    # Bones & Paws es una tienda ficticia creada para este proyecto
    # academico: los datos de abajo son de muestra. Estan en un solo lugar
    # para poder cambiarlos sin tocar plantillas ni el generador de PDF.
    EMPRESA = {
        "nombre": "Bones & Paws S.A.S.",
        "nit": "901.234.567-8",
        "direccion": "Calle 123 # 45-67, Local 3",
        "ciudad": "Bogotá D.C., Colombia",
        "telefono": "+57 321 390 1883",
        "correo": "antonietawsnpaws@gmail.com",
        # Sin la arroba: las plantillas la ponen para mostrarla y la URL de
        # Instagram no la lleva.
        "instagram": "bonespaws_666",
        "web": "www.bonesandpaws.co",
        "horario": "Lunes a sábado, 8:00 a.m. – 6:00 p.m.",
    }

    # Prefijo del consecutivo: la factura 42 se muestra como BP-000042
    FACTURA_PREFIJO = "BP"

    # Aviso al pie. El proyecto es academico y la tienda no existe, asi que
    # el documento se identifica como tal para que no se confunda con una
    # factura electronica real validada ante la DIAN.
    FACTURA_NOTA = (
        "Documento generado por Bones & Paws, proyecto académico. "
        "Tienda ficticia: este comprobante no tiene validez fiscal "
        "ni corresponde a una factura electrónica validada por la DIAN."
    )
