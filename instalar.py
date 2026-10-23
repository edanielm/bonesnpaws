"""
instalar.py

Instalador de Bones & Paws. Deja el proyecto listo para correr en un
equipo nuevo, sea Windows, macOS o Linux, con un solo comando:

    python instalar.py

Hace, en orden:
    1. Comprueba la version de Python.
    2. Crea el entorno virtual .venv (o lo reutiliza si ya sirve).
    3. Instala las dependencias de requirements.txt dentro de ese entorno.
    4. Crea el archivo .env con una SECRET_KEY aleatoria y los datos de MySQL.
    5. Inicializa la base de datos ejecutando database/init_db.py.
    6. Verifica que todo quedo bien.

Opciones:
    --auto              No pregunta nada: usa los valores por defecto
                        (o el .env existente). Util para reinstalar rapido.
    --regenerar-clave   Solo cambia SECRET_KEY del .env por una nueva aleatoria.
    --sin-bd            Salta la creacion de la base de datos.

IMPORTANTE: este archivo solo usa la libreria estandar de Python, porque
se ejecuta ANTES de que exista el entorno virtual y sus dependencias.
"""
import argparse
import os
import platform
import secrets
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, ".venv")
ENV_FILE = os.path.join(BASE_DIR, ".env")
ENV_EJEMPLO = os.path.join(BASE_DIR, ".env.example")
REQUISITOS = os.path.join(BASE_DIR, "requirements.txt")

PYTHON_MINIMO = (3, 9)


# ----------------------------------------------------------------------
# Utilidades de presentacion
# ----------------------------------------------------------------------

def titulo(texto):
    print()
    print("=" * 64)
    print(f"  {texto}")
    print("=" * 64)


def paso(numero, texto):
    print(f"\n[{numero}/6] {texto}")


def ok(texto):
    print(f"      OK  {texto}")


def error(texto, solucion=""):
    print(f"      ERROR  {texto}")
    if solucion:
        # Las soluciones de varias lineas se alinean bajo la flecha
        lineas = [l.strip() for l in solucion.split("\n") if l.strip()]
        print(f"             -> {lineas[0]}")
        for extra in lineas[1:]:
            print(f"                {extra}")


def aviso(texto):
    print(f"      !   {texto}")


def preguntar(mensaje, por_defecto="", automatico=False, oculto=False):
    """Pregunta al usuario; en modo --auto devuelve el valor por defecto."""
    if automatico:
        return por_defecto
    sufijo = f" [{por_defecto}]" if por_defecto else " []"
    try:
        if oculto:
            import getpass
            respuesta = getpass.getpass(f"      {mensaje}{sufijo}: ")
        else:
            respuesta = input(f"      {mensaje}{sufijo}: ")
    except (EOFError, KeyboardInterrupt):
        print()
        return por_defecto
    return respuesta.strip() or por_defecto


# ----------------------------------------------------------------------
# Rutas del entorno virtual (cambian segun el sistema operativo)
# ----------------------------------------------------------------------

def python_del_venv():
    if platform.system() == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def comando_activar():
    if platform.system() == "Windows":
        return r".venv\Scripts\activate"
    return "source .venv/bin/activate"


def venv_sirve():
    """
    Un venv copiado de otra maquina guarda rutas absolutas del equipo
    original y su python.exe no arranca. Se comprueba ejecutandolo.
    """
    exe = python_del_venv()
    if not os.path.isfile(exe):
        return False
    try:
        r = subprocess.run([exe, "-c", "import sys; print(sys.version)"],
                           capture_output=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


# ----------------------------------------------------------------------
# Pasos
# ----------------------------------------------------------------------

def paso_python():
    paso(1, "Comprobando la version de Python...")
    v = sys.version_info
    if v < PYTHON_MINIMO:
        error(f"Tienes Python {v.major}.{v.minor}, se necesita "
              f"{PYTHON_MINIMO[0]}.{PYTHON_MINIMO[1]} o superior.",
              "Descarga una version nueva en https://www.python.org/downloads/")
        return False
    ok(f"Python {v.major}.{v.minor}.{v.micro} ({platform.system()})")
    return True


def paso_venv():
    paso(2, "Preparando el entorno virtual (.venv)...")

    if os.path.isdir(VENV_DIR):
        if venv_sirve():
            ok("Ya existe un entorno virtual utilizable, se reutiliza.")
            return True
        aviso("El .venv existente esta roto (suele pasar al copiar el "
              "proyecto de otro equipo). Se recrea.")
        try:
            shutil.rmtree(VENV_DIR)
        except OSError as e:
            error(f"No se pudo borrar .venv: {e}",
                  "Cierra los editores o terminales que lo esten usando y reintenta.")
            return False

    print("      Creando .venv (puede tardar unos segundos)...")
    r = subprocess.run([sys.executable, "-m", "venv", VENV_DIR], capture_output=True, text=True)
    if r.returncode != 0:
        error("No se pudo crear el entorno virtual.", (r.stderr or "").strip()[:300])
        return False
    ok("Entorno virtual creado en .venv/")
    return True


def paso_dependencias():
    paso(3, "Instalando dependencias...")
    exe = python_del_venv()

    subprocess.run([exe, "-m", "pip", "install", "--upgrade", "pip", "-q"],
                   capture_output=True, text=True)

    r = subprocess.run([exe, "-m", "pip", "install", "-r", REQUISITOS, "-q",
                        "--disable-pip-version-check"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        error("Fallo la instalacion de dependencias.")
        print((r.stderr or r.stdout or "").strip()[-900:])
        print("\n             -> Revisa tu conexion a internet y reintenta.")
        return False

    listado = subprocess.run([exe, "-m", "pip", "list", "--format=freeze"],
                             capture_output=True, text=True)
    instalados = [l for l in listado.stdout.splitlines()
                  if l.lower().startswith(("flask", "mysql-connector", "python-dotenv", "werkzeug"))]
    ok("Dependencias instaladas: " + ", ".join(instalados))
    return True


def paso_env(automatico, solo_clave=False):
    paso(4, "Configurando el archivo .env...")

    valores = {
        "SECRET_KEY": secrets.token_hex(32),
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "root",
        "DB_PASSWORD": "",
        "DB_NAME": "bandp",
        "FLASK_DEBUG": "True",
        "FLASK_PORT": "5000",
        # Correo saliente. Se dejan vacios: sin ellos la app funciona igual
        # (en desarrollo el codigo de recuperacion sale por consola), y
        # rellenarlos es un paso aparte que explica el README.
        "MAIL_SERVIDOR": "smtp.gmail.com",
        "MAIL_PUERTO": "587",
        "MAIL_USAR_TLS": "True",
        "MAIL_USAR_SSL": "False",
        "MAIL_USUARIO": "",
        "MAIL_CONTRASENA": "",
        "MAIL_NOMBRE_REMITENTE": "Bones & Paws",
        "MAIL_A_CONSOLA": "True",
    }

    existente = {}
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith("#") and "=" in linea:
                    k, v = linea.split("=", 1)
                    existente[k.strip()] = v.strip()

    # Se conserva lo que ya estaba configurado, menos la SECRET_KEY de ejemplo
    for clave, valor in existente.items():
        if clave == "SECRET_KEY" and valor.startswith("cambia-esta-clave"):
            continue
        valores[clave] = valor

    if solo_clave:
        valores["SECRET_KEY"] = secrets.token_hex(32)
    elif not automatico:
        print("      Datos de conexion a MySQL (Enter para dejar el valor entre corchetes):")
        valores["DB_HOST"] = preguntar("Servidor", valores["DB_HOST"])
        valores["DB_PORT"] = preguntar("Puerto", valores["DB_PORT"])
        valores["DB_USER"] = preguntar("Usuario", valores["DB_USER"])
        actual = valores["DB_PASSWORD"]
        pista = "(vacia)" if not actual else "(la actual)"
        respuesta = preguntar(f"Contrasena {pista}", "", oculto=True)
        valores["DB_PASSWORD"] = respuesta if respuesta else actual
        valores["DB_NAME"] = preguntar("Base de datos", valores["DB_NAME"])

    contenido = f"""# Configuracion local de Bones & Paws.
# Generado por instalar.py — este archivo NO se comparte (esta en .gitignore),
# porque la contrasena de MySQL cambia en cada equipo.

SECRET_KEY={valores['SECRET_KEY']}

DB_HOST={valores['DB_HOST']}
DB_PORT={valores['DB_PORT']}
DB_USER={valores['DB_USER']}
DB_PASSWORD={valores['DB_PASSWORD']}
DB_NAME={valores['DB_NAME']}

FLASK_DEBUG={valores['FLASK_DEBUG']}
FLASK_PORT={valores['FLASK_PORT']}

# Correo saliente (recuperar contrasena). MAIL_CONTRASENA es una
# "contrasena de aplicacion" de 16 letras de Google, NO la del correo:
# https://myaccount.google.com/apppasswords  (ver README)
MAIL_SERVIDOR={valores['MAIL_SERVIDOR']}
MAIL_PUERTO={valores['MAIL_PUERTO']}
MAIL_USAR_TLS={valores['MAIL_USAR_TLS']}
MAIL_USAR_SSL={valores['MAIL_USAR_SSL']}
MAIL_USUARIO={valores['MAIL_USUARIO']}
MAIL_CONTRASENA={valores['MAIL_CONTRASENA']}
MAIL_NOMBRE_REMITENTE={valores['MAIL_NOMBRE_REMITENTE']}
MAIL_A_CONSOLA={valores['MAIL_A_CONSOLA']}
"""
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(contenido)

    ok(f".env listo (MySQL en {valores['DB_HOST']}:{valores['DB_PORT']}, "
       f"usuario '{valores['DB_USER']}', base '{valores['DB_NAME']}')")
    return True


def paso_base_datos(automatico, saltar=False):
    paso(5, "Inicializando la base de datos...")

    if saltar:
        aviso("Saltado por la opcion --sin-bd.")
        return True

    exe = python_del_venv()
    sys.path.insert(0, BASE_DIR)

    # Se recarga el modulo por si .env acaba de cambiar en esta misma corrida
    import importlib
    import verificar as v
    importlib.reload(v)

    env = v._leer_env()
    estado_servidor = v.revisar_servidor_mysql(env)
    if estado_servidor.estado == v.FALLO:
        error(estado_servidor.titulo, estado_servidor.solucion)
        aviso("Cuando MySQL este encendido, ejecuta:  python database/init_db.py")
        return False

    ok("Servidor MySQL detectado.")

    if not automatico:
        print("      Se va a BORRAR y volver a crear la base de datos con su")
        print("      estructura, datos de ejemplo, vistas, procedimientos y")
        print("      triggers. Si ya tiene datos tuyos, se pierden.")
        respuesta = preguntar("Continuar? (s/n)", "s")
        if respuesta.lower() not in ("s", "si", "sí", "y", "yes"):
            aviso("Saltado. Puedes hacerlo luego con:  python database/init_db.py")
            return True

    # --forzar porque la confirmacion ya se pidio aqui arriba. Sin esa
    # opcion init_db.py preguntaria por su cuenta, y como su salida va
    # capturada la pregunta no se veria: el instalador quedaria colgado
    # esperando una respuesta a algo que nadie leyo.
    script = os.path.join(BASE_DIR, "database", "init_db.py")
    r = subprocess.run([exe, script, "--forzar"], capture_output=True, text=True)
    for linea in (r.stdout or "").splitlines():
        if linea.strip():
            print(f"      {linea}")
    if r.returncode != 0:
        error("La inicializacion de la base de datos fallo.")
        print((r.stderr or "").strip()[-600:])
        return False
    return True


def paso_verificacion():
    paso(6, "Verificando la instalacion...")
    exe = python_del_venv()
    r = subprocess.run([exe, os.path.join(BASE_DIR, "verificar.py")],
                       capture_output=True, text=True)
    print(r.stdout.rstrip())
    return r.returncode == 0


# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Instalador de Bones & Paws")
    parser.add_argument("--auto", action="store_true",
                        help="no preguntar nada, usar valores por defecto")
    parser.add_argument("--regenerar-clave", action="store_true",
                        help="solo generar una SECRET_KEY nueva en .env")
    parser.add_argument("--sin-bd", action="store_true",
                        help="no inicializar la base de datos")
    args = parser.parse_args()

    if args.regenerar_clave:
        titulo("Bones & Paws - nueva SECRET_KEY")
        paso_env(automatico=True, solo_clave=True)
        print("\n  Listo.\n")
        return 0

    titulo("Bones & Paws - instalacion")
    print(f"  Carpeta: {BASE_DIR}")

    if not paso_python():
        return 1
    if not paso_venv():
        return 1
    if not paso_dependencias():
        return 1
    if not paso_env(args.auto):
        return 1

    bd_ok = paso_base_datos(args.auto, saltar=args.sin_bd)
    todo_ok = paso_verificacion() and bd_ok

    print("=" * 64)
    if todo_ok:
        print("  INSTALACION COMPLETA")
        print()
        print("  Para levantar el sitio:")
        print(f"      {comando_activar()}")
        print("      python run.py")
        print()
        print("  Y abre http://localhost:5000 en el navegador.")
        print("  Panel de administrador: http://localhost:5000/admin  (admin / admin123)")
    else:
        print("  INSTALACION INCOMPLETA")
        print()
        print("  Revisa los mensajes de arriba. Cuando lo corrijas, comprueba con:")
        print("      python verificar.py")
    print("=" * 64)
    print()
    return 0 if todo_ok else 1


if __name__ == "__main__":
    sys.exit(main())
