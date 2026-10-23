"""
run.py

Punto de entrada unico del proyecto. Levanta el servidor de desarrollo Flask.

Antes de arrancar hace un chequeo rapido del entorno (dependencias, .env,
MySQL encendido, base de datos creada). Si algo falta, lo dice en un
mensaje claro en vez de dejar que la aplicacion falle mas adelante con un
traceback de SQLAlchemy en mitad de una peticion.

Uso:
    python run.py               levanta el servidor
    python run.py --sin-chequeo salta la verificacion previa
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def chequeo_previo():
    """Devuelve True si el entorno esta listo para levantar el servidor."""
    import verificar

    resultados = verificar.diagnosticar()
    if verificar.todo_bien(resultados):
        return True

    print()
    print("=" * 64)
    print("  No se puede iniciar Bones & Paws todavia")
    print("=" * 64)
    verificar.imprimir(resultados)
    print("  Si es la primera vez que abres el proyecto en este equipo:")
    print("      python instalar.py")
    print()
    return False


def main():
    saltar = "--sin-chequeo" in sys.argv

    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, ".env"))
    except ImportError:
        print("\n  Falta instalar las dependencias del proyecto.")
        print("  Ejecuta:  python instalar.py\n")
        return 1

    if not saltar and not chequeo_previo():
        return 1

    from app import create_app

    app = create_app()
    puerto = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True") == "True"

    print()
    print("=" * 64)
    print("  Bones & Paws en marcha")
    print(f"    Tienda:  http://localhost:{puerto}")
    print(f"    Admin:   http://localhost:{puerto}/admin   (admin / admin123)")
    print("  Ctrl+C para detener.")
    print("=" * 64)
    print()

    # host 0.0.0.0 para poder abrirlo tambien desde otro equipo de la red local
    app.run(host="0.0.0.0", port=puerto, debug=debug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
