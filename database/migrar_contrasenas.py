"""
database/migrar_contrasenas.py

Cifra de una sola vez las contrasenas que todavia esten en texto plano.

EL PROBLEMA
-----------
Los clientes y empleados sembrados por seed.sql traen la contrasena escrita
tal cual en la tabla (todos con '123456'). Cualquiera que abra `cliente` en
phpMyAdmin las lee. Las cuentas creadas desde la aplicacion nunca tuvieron
ese problema: se guardan hasheadas con Werkzeug desde el primer dia.

LA SOLUCION
-----------
No hace falta saber cual es la contrasena de cada quien para cifrarla: lo
que esta guardado ES la contrasena, asi que se le aplica el hash y se
reescribe. Quien entraba con '123456' sigue entrando con '123456', pero la
base ya no la tiene a la vista.

La aplicacion tambien migra por su cuenta: cuando alguien inicia sesion con
una contrasena en texto plano, AuthService la reescribe hasheada en ese
momento ("migracion perezosa"). Este script hace lo mismo de una sola vez,
sin esperar a que cada persona entre.

Uso:
    python database/migrar_contrasenas.py            # muestra que haria
    python database/migrar_contrasenas.py --aplicar  # lo hace de verdad

Es idempotente: las cuentas que ya estan hasheadas se saltan, asi que se
puede correr las veces que haga falta.
"""
import os
import sys

# Permite ejecutarlo como `python database/migrar_contrasenas.py` desde la
# raiz del proyecto, sin instalar nada.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from werkzeug.security import generate_password_hash  # noqa: E402

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import Cliente, Empleado  # noqa: E402
from app.services.auth_service import esta_hasheada  # noqa: E402


def cuentas_en_texto_plano(modelo):
    """Las filas de `modelo` cuya contrasena todavia no es un hash."""
    return [fila for fila in modelo.query.all() if not esta_hasheada(fila.contrasena)]


def migrar(aplicar):
    total = 0

    for modelo, etiqueta in ((Cliente, "cliente"), (Empleado, "empleado")):
        pendientes = cuentas_en_texto_plano(modelo)
        total += len(pendientes)

        print(f"\n{etiqueta.upper()}: {len(pendientes)} cuenta(s) en texto plano")
        for fila in pendientes[:5]:
            print(f"  - {fila.correo}")
        if len(pendientes) > 5:
            print(f"  ... y {len(pendientes) - 5} mas")

        if aplicar:
            for fila in pendientes:
                # Lo guardado es la contrasena: se hashea tal cual, asi que
                # nadie tiene que cambiar la suya para poder seguir entrando.
                fila.contrasena = generate_password_hash(fila.contrasena)

    if not total:
        print("\nNo hay nada que migrar: todas las contrasenas ya estan cifradas.")
        return

    if aplicar:
        db.session.commit()
        print(f"\nListo: {total} contrasena(s) cifradas.")
        print("Las credenciales de acceso no cambian; solo dejan de estar a la vista.")
    else:
        print(f"\nSimulacion: se cifrarian {total} contrasena(s).")
        print("Para hacerlo de verdad:  python database/migrar_contrasenas.py --aplicar")


def main():
    aplicar = "--aplicar" in sys.argv

    app = create_app()
    with app.app_context():
        print("Revisando contrasenas guardadas en la base de datos...")
        try:
            migrar(aplicar)
        except Exception as e:  # conexion caida, tabla inexistente, etc.
            print(f"\nNo se pudo completar: {e}")
            print("Comprueba que MySQL este encendido y que la base 'bandp' exista.")
            print("Diagnostico completo:  python verificar.py")
            sys.exit(1)


if __name__ == "__main__":
    main()
