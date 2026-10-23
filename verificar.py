"""
verificar.py

Chequeo de entorno de Bones & Paws.

Responde a una sola pregunta: "¿este equipo tiene todo lo necesario para
correr el proyecto?" — y cuando algo falta, dice exactamente que hacer en
vez de dejar que la aplicacion reviente con un traceback en la primera
consulta a la base de datos.

Lo usan:
    - instalar.py  (al final de la instalacion)
    - run.py       (chequeo rapido antes de levantar el servidor)
    - a mano:      python verificar.py

Solo usa la libreria estandar; las dependencias del proyecto se importan
dentro de try/except porque justamente puede que aun no esten instaladas.
"""
import os
import socket
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tablas que debe tener la base de datos una vez inicializada
TABLAS_ESPERADAS = [
    "carrito", "carrito_producto", "categoria", "cliente", "detalle",
    "empleado", "envio", "factura", "metodo_pago", "producto",
    "proveedor", "pse", "tarjeta", "transferencia_bancaria", "transportadora",
]

OK, FALLO, AVISO = "ok", "fallo", "aviso"

_SIMBOLO = {OK: "[ OK ]", FALLO: "[FALLA]", AVISO: "[AVISO]"}


class Resultado:
    def __init__(self, estado, titulo, detalle="", solucion=""):
        self.estado = estado
        self.titulo = titulo
        self.detalle = detalle
        self.solucion = solucion


def _leer_env():
    """
    Lee .env sin depender de python-dotenv (puede no estar instalado todavia).
    Las variables ya presentes en el entorno del sistema tienen prioridad.
    """
    valores = {}
    ruta = os.path.join(BASE_DIR, ".env")
    if os.path.isfile(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                clave, valor = linea.split("=", 1)
                valores[clave.strip()] = valor.strip()

    for clave in ("DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME",
                  "SECRET_KEY", "FLASK_PORT", "FLASK_DEBUG"):
        if os.getenv(clave) is not None:
            valores[clave] = os.getenv(clave)

    valores.setdefault("DB_HOST", "localhost")
    valores.setdefault("DB_PORT", "3306")
    valores.setdefault("DB_USER", "root")
    valores.setdefault("DB_PASSWORD", "")
    valores.setdefault("DB_NAME", "bandp")
    return valores


# ----------------------------------------------------------------------
# Chequeos individuales
# ----------------------------------------------------------------------

def revisar_python():
    v = sys.version_info
    if v < (3, 9):
        return Resultado(
            FALLO, f"Python {v.major}.{v.minor} es demasiado antiguo",
            "El proyecto necesita Python 3.9 o superior.",
            "Instala Python 3.11 o 3.12 desde https://www.python.org/downloads/",
        )
    return Resultado(OK, f"Python {v.major}.{v.minor}.{v.micro}")


def revisar_dependencias():
    faltantes = []
    for modulo, paquete in (
        ("flask", "Flask"),
        ("flask_sqlalchemy", "Flask-SQLAlchemy"),
        ("mysql.connector", "mysql-connector-python"),
        ("dotenv", "python-dotenv"),
        ("reportlab", "reportlab"),  # PDF de la factura
    ):
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(paquete)

    if faltantes:
        return Resultado(
            FALLO, "Faltan dependencias de Python",
            "No estan instaladas: " + ", ".join(faltantes),
            "Ejecuta:  python instalar.py",
        )
    return Resultado(OK, "Dependencias de Python instaladas")


def revisar_env():
    if not os.path.isfile(os.path.join(BASE_DIR, ".env")):
        return Resultado(
            FALLO, "Falta el archivo .env",
            "Sin el, no se sabe la contrasena de MySQL de este equipo.",
            "Ejecuta:  python instalar.py    (lo crea por ti)",
        )

    env = _leer_env()
    if env.get("SECRET_KEY", "").startswith("cambia-esta-clave"):
        return Resultado(
            AVISO, "El archivo .env existe, pero SECRET_KEY es la de ejemplo",
            "Funciona igual, pero conviene poner una clave aleatoria propia.",
            "Ejecuta:  python instalar.py --regenerar-clave",
        )
    return Resultado(OK, "Archivo .env configurado")


def revisar_servidor_mysql(env):
    """Comprueba que haya algo escuchando en el puerto de MySQL."""
    host, puerto = env["DB_HOST"], int(env["DB_PORT"])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((host, puerto))
        return Resultado(OK, f"Servidor MySQL escuchando en {host}:{puerto}")
    except (socket.timeout, ConnectionRefusedError, OSError):
        return Resultado(
            FALLO, f"No hay ningun servidor MySQL en {host}:{puerto}",
            "El servicio de base de datos esta apagado o usa otro puerto.",
            "Si usas XAMPP: abre el Panel de Control y pulsa 'Start' en MySQL.\n"
            "Si tu MySQL usa otro puerto, cambia DB_PORT en el archivo .env.",
        )
    finally:
        sock.close()


def revisar_credenciales(env):
    try:
        import mysql.connector
        from mysql.connector import Error
    except ImportError:
        return Resultado(AVISO, "No se pudo probar el acceso a MySQL",
                         "Falta el paquete mysql-connector-python.",
                         "Ejecuta:  python instalar.py")

    try:
        conn = mysql.connector.connect(
            host=env["DB_HOST"], port=int(env["DB_PORT"]),
            user=env["DB_USER"], password=env["DB_PASSWORD"],
            connection_timeout=5, use_pure=True,
        )
        conn.close()
        return Resultado(OK, f"Acceso a MySQL correcto (usuario '{env['DB_USER']}')")
    except Error as e:
        return Resultado(
            FALLO, "MySQL rechazo el usuario o la contrasena",
            str(e),
            "Revisa DB_USER y DB_PASSWORD en el archivo .env.\n"
            "En XAMPP el usuario suele ser 'root' con la contrasena vacia.",
        )


def revisar_base_datos(env):
    try:
        import mysql.connector
        from mysql.connector import Error
    except ImportError:
        return Resultado(AVISO, "No se pudo revisar la base de datos", "", "")

    try:
        conn = mysql.connector.connect(
            host=env["DB_HOST"], port=int(env["DB_PORT"]),
            user=env["DB_USER"], password=env["DB_PASSWORD"],
            connection_timeout=5, use_pure=True,
        )
    except Error as e:
        return Resultado(FALLO, "No se pudo conectar a MySQL", str(e),
                         "Revisa los chequeos anteriores.")

    cur = conn.cursor()
    nombre = env["DB_NAME"]
    try:
        cur.execute("SELECT SCHEMA_NAME FROM information_schema.schemata WHERE SCHEMA_NAME = %s", (nombre,))
        if not cur.fetchone():
            return Resultado(
                FALLO, f"La base de datos '{nombre}' no existe",
                "MySQL funciona, pero el proyecto aun no tiene sus tablas.",
                "Ejecuta:  python database/init_db.py",
            )

        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s", (nombre,))
        tablas = {fila[0].lower() for fila in cur.fetchall()}
        faltantes = [t for t in TABLAS_ESPERADAS if t not in tablas]
        if faltantes:
            return Resultado(
                FALLO, f"A la base '{nombre}' le faltan tablas",
                "No estan: " + ", ".join(faltantes),
                "Ejecuta:  python database/init_db.py",
            )

        cur.execute(f"SELECT COUNT(*) FROM `{nombre}`.producto")
        productos = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM `{nombre}`.empleado")
        empleados = cur.fetchone()[0]

        # Tabla que llego con una migracion, no con el esquema original.
        # Es un AVISO y no un FALLO a proposito: la base por lo demas sirve,
        # y la solucion no es volver a crearla (eso borraria los datos) sino
        # correr la migracion. Sin ella, "¿Olvidaste tu contraseña?" falla.
        if "codigo_recuperacion" not in tablas:
            return Resultado(
                AVISO, f"A la base '{nombre}' le falta la tabla 'codigo_recuperacion'",
                "Sin ella no funciona recuperar la contrasena por correo. "
                "El resto de la tienda si funciona.",
                "Ejecuta:  mysql -u root -p bandp < database/migracion_codigo_recuperacion.sql",
            )

        if productos == 0 or empleados == 0:
            return Resultado(
                AVISO, f"La base '{nombre}' existe pero esta vacia",
                f"{productos} producto(s), {empleados} empleado(s). "
                "Sin el empleado admin no podras entrar a /admin.",
                "Ejecuta:  python database/init_db.py",
            )

        return Resultado(OK, f"Base de datos '{nombre}' lista",
                         f"{len(tablas)} tablas, {productos} productos")
    finally:
        cur.close()
        conn.close()


def revisar_objetos(env):
    """Vistas, funciones, procedimientos y triggers (el 'escudo logico')."""
    try:
        import mysql.connector
        from mysql.connector import Error
    except ImportError:
        return Resultado(AVISO, "No se pudieron revisar los objetos de BD", "", "")

    nombre = env["DB_NAME"]
    try:
        conn = mysql.connector.connect(
            host=env["DB_HOST"], port=int(env["DB_PORT"]),
            user=env["DB_USER"], password=env["DB_PASSWORD"],
            database=nombre, connection_timeout=5, use_pure=True,
        )
    except Error:
        return Resultado(AVISO, "No se pudieron revisar los objetos de BD", "", "")

    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM information_schema.views WHERE table_schema = %s", (nombre,))
        vistas = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM information_schema.routines "
                    "WHERE routine_schema = %s AND routine_type = 'FUNCTION'", (nombre,))
        funciones = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM information_schema.routines "
                    "WHERE routine_schema = %s AND routine_type = 'PROCEDURE'", (nombre,))
        procedimientos = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = %s", (nombre,))
        triggers = cur.fetchone()[0]

        detalle = (f"{vistas} vistas, {funciones} funciones, "
                   f"{procedimientos} procedimientos, {triggers} triggers")

        if triggers == 0:
            return Resultado(
                AVISO, "Faltan los objetos programables de la base de datos", detalle,
                "Sin los triggers, el stock no se descuenta al vender.\n"
                "Ejecuta:  python database/init_db.py",
            )

        # Los triggers de producto escriben en auditoria_producto: si la
        # tabla falta, toda venta falla al descontar stock.
        cur.execute("SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = %s AND table_name = 'auditoria_producto'", (nombre,))
        if cur.fetchone()[0] == 0:
            return Resultado(
                FALLO, "Falta la tabla auditoria_producto", detalle,
                "Los triggers la usan al descontar stock: sin ella no se puede\n"
                "completar ninguna compra. Ejecuta:  python database/init_db.py",
            )
        return Resultado(OK, "Objetos de base de datos creados", detalle)
    finally:
        cur.close()
        conn.close()


# ----------------------------------------------------------------------
# Ejecucion
# ----------------------------------------------------------------------

def diagnosticar(incluir_bd=True):
    """Corre todos los chequeos y devuelve la lista de resultados."""
    resultados = [revisar_python(), revisar_dependencias(), revisar_env()]

    # Si faltan dependencias o .env, los chequeos de MySQL no aportan nada util
    if not incluir_bd or any(r.estado == FALLO for r in resultados):
        return resultados

    env = _leer_env()
    resultados.append(revisar_servidor_mysql(env))
    if resultados[-1].estado == FALLO:
        return resultados

    resultados.append(revisar_credenciales(env))
    if resultados[-1].estado == FALLO:
        return resultados

    resultados.append(revisar_base_datos(env))
    if resultados[-1].estado == FALLO:
        return resultados

    resultados.append(revisar_objetos(env))
    return resultados


def imprimir(resultados):
    print()
    for r in resultados:
        print(f"  {_SIMBOLO[r.estado]}  {r.titulo}")
        if r.detalle:
            print(f"          {r.detalle}")
        if r.solucion and r.estado != OK:
            # Las soluciones de varias lineas se alinean bajo la flecha
            lineas = [l.strip() for l in r.solucion.split("\n") if l.strip()]
            print(f"          -> {lineas[0]}")
            for extra in lineas[1:]:
                print(f"             {extra}")
    print()


def todo_bien(resultados):
    return not any(r.estado == FALLO for r in resultados)


def probar_correo(destinatario=None):
    """
    Manda un correo de prueba con la cuenta de .env y cuenta que paso.

    Existe porque el error tipico al configurar Gmail -la contrasena de
    aplicacion mal copiada- solo se descubre al intentar recuperar una
    contrasena, que son cinco pasos. Asi se comprueba en uno.
    """
    print("=" * 64)
    print("  Bones & Paws - prueba de envio de correo")
    print("=" * 64)
    print()

    sys.path.insert(0, BASE_DIR)
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, ".env"))
        from app import create_app
        from app.services import correo_service
    except ImportError as e:
        print(f"  [FALLA] Faltan dependencias del proyecto: {e}")
        print("          Ejecuta:  python instalar.py")
        print()
        return 1

    aplicacion = create_app()
    with aplicacion.app_context():
        cfg = aplicacion.config
        usuario = cfg.get("MAIL_USUARIO") or "(vacio)"
        print(f"  Servidor : {cfg['MAIL_SERVIDOR']}:{cfg['MAIL_PUERTO']}")
        print(f"  Cuenta   : {usuario}")
        print()

        if not correo_service.esta_configurado():
            print("  [FALLA] Falta MAIL_USUARIO o MAIL_CONTRASENA en el archivo .env.")
            print()
            print("          MAIL_CONTRASENA no es la contrasena del correo: es una")
            print("          'contrasena de aplicacion' de 16 letras de Google.")
            print("          Se genera en https://myaccount.google.com/apppasswords")
            print("          (hace falta tener la verificacion en dos pasos activada).")
            print()
            return 1

        destino = destinatario or cfg["MAIL_USUARIO"]
        print(f"  Enviando una prueba a {destino} ...")
        try:
            correo_service.enviar(
                destinatario=destino,
                asunto="Prueba de envio de Bones & Paws",
                texto=(
                    "Si estas leyendo esto, la cuenta de correo de Bones & Paws "
                    "quedo bien configurada.\n\n"
                    "Ya funciona el codigo de verificacion de "
                    "'Olvidaste tu contrasena?'.\n"
                ),
            )
        except correo_service.CorreoNoEnviado as e:
            print(f"  [FALLA] {e}")
            print()
            print("  Causas mas comunes, en orden:")
            print("    1. La contrasena de aplicacion esta mal copiada.")
            print("       Son 16 letras seguidas, SIN los espacios que muestra Google.")
            print("    2. Se puso la contrasena normal del correo en vez de la de")
            print("       aplicacion. Gmail rechaza la normal desde 2022.")
            print("    3. La verificacion en dos pasos no esta activada en la cuenta.")
            print("       Sin ella Google ni siquiera deja crear la de aplicacion.")
            print("    4. No hay internet, o un firewall bloquea el puerto 587.")
            print()
            return 1

        print()
        print(f"  [ OK ]  Correo enviado. Revisa la bandeja de {destino}")
        print("          (si no aparece, mira en Spam: es el primer correo que")
        print("          manda esta cuenta y puede caer ahi).")
        print()
        return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if "--correo" in argv:
        # El argumento siguiente, si lo hay, es a donde mandar la prueba
        i = argv.index("--correo")
        destino = argv[i + 1] if len(argv) > i + 1 else None
        return probar_correo(destino)

    print("=" * 64)
    print("  Bones & Paws - verificacion del entorno")
    print("=" * 64)

    resultados = diagnosticar()
    imprimir(resultados)

    if todo_bien(resultados):
        print("  Todo listo. Levanta el servidor con:  python run.py")
        print("  Para probar el envio de correo:       python verificar.py --correo")
        print()
        return 0

    print("  Corrige los puntos marcados con [FALLA] y vuelve a ejecutar:")
    print("      python verificar.py")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
