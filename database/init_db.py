"""
database/init_db.py

Reconstruccion determinista de la base de datos 'bandp'.
Ejecuta, en orden:
    1. schema.sql   -> estructura (tablas, indices, llaves foraneas)
    2. seed.sql     -> datos iniciales
    3. objetos.sql  -> vistas, funciones, procedimientos y triggers

tal como se explica en el Blueprint Profesional Flask ("El Escudo Logico"
y "Reconstruccion Determinista").

El orden importa: los objetos van al final porque los triggers de `detalle`
descuentan stock. Si existieran durante el seed, los datos historicos de
`bandp.sql` volverian a descontar inventario que ya estaba descontado.

IMPORTANTE: "reconstruccion determinista" significa que la base queda
*exactamente* como la describen esos tres archivos, sin importar como
estuviera antes. Para eso hay que borrarla primero.

Antes esta parte faltaba: el script hacia CREATE DATABASE IF NOT EXISTS y
seguia derecho, asi que sobre una base `bandp` que ya existia todos los
CREATE TABLE fallaban con "ya existe", se contaban como avisos y el
esquema viejo se quedaba tal cual. El resultado era una base a medias
-tablas nuevas creadas, tablas viejas sin las columnas nuevas- que
reventaba al usarla con errores como:

    Unknown column 'producto.codigo' in 'field list'

Ahora la base se borra y se vuelve a crear, previa confirmacion.

Uso:
    python database/init_db.py              pregunta antes de borrar
    python database/init_db.py --forzar     no pregunta (para scripts)
"""
import argparse
import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "bandp")


def split_statements(sql_text):
    """
    Separa un archivo .sql en sentencias individuales.

    Entiende la directiva DELIMITER, necesaria porque los triggers,
    funciones y procedimientos de objetos.sql llevan ';' dentro de su
    cuerpo BEGIN ... END y un split directo por ';' los partiria a la mitad.
    """
    statements = []
    delimiter = ";"
    buffer = ""

    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue

        if stripped.upper().startswith("DELIMITER "):
            if buffer.strip():
                statements.append(buffer.strip())
                buffer = ""
            delimiter = stripped.split(None, 1)[1].strip()
            continue

        buffer += line + "\n"
        # Como el dump no tiene el delimitador dentro de strings de datos
        # reales (los VALUES usan comillas simples sin ';' embebido), buscar
        # el delimitador de forma literal es seguro para estos archivos.
        while delimiter in buffer:
            head, buffer = buffer.split(delimiter, 1)
            if head.strip():
                statements.append(head.strip())

    if buffer.strip():
        statements.append(buffer.strip())

    return statements


def run_sql_file(cursor, path):
    """Ejecuta un archivo .sql completo. Devuelve el numero de errores."""
    # utf-8-sig descarta el BOM que dejan algunos editores al inicio del archivo
    with open(path, "r", encoding="utf-8-sig") as f:
        sql_text = f.read()

    errores = 0
    for stmt in split_statements(sql_text):
        try:
            cursor.execute(stmt)
            # Algunos procedimientos/consultas devuelven filas; hay que
            # consumirlas o la siguiente sentencia falla con "Unread result".
            if cursor.with_rows:
                cursor.fetchall()
        except Error as e:
            errores += 1
            resumen = " ".join(stmt.split())[:80]
            print(f"  [AVISO] {e}\n          en: {resumen}...")

    return errores


def tablas_existentes(cursor):
    """Cuantas tablas tiene ya la base (0 si ni siquiera existe)."""
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s",
        (DB_NAME,),
    )
    return cursor.fetchone()[0]


def confirmar_reconstruccion(cursor, forzar):
    """
    Pide permiso antes de borrar una base que ya tiene datos.

    Si la base no existe o esta vacia no hay nada que perder y no se
    pregunta nada.
    """
    cuantas = tablas_existentes(cursor)
    if cuantas == 0:
        return True
    if forzar:
        print(f"La base '{DB_NAME}' ya existe ({cuantas} tablas): se reconstruye (--forzar).")
        return True

    print()
    print("=" * 64)
    print(f"  La base '{DB_NAME}' ya existe y tiene {cuantas} tablas.")
    print("=" * 64)
    print("  Para dejarla igual a schema.sql + seed.sql + objetos.sql hay")
    print("  que BORRARLA y volver a crearla. Se pierde todo lo que tenga")
    print("  ahora: productos, clientes y facturas que hayas creado tu.")
    print()
    print("  Si quieres guardar una copia primero, cancela y ejecuta:")
    print(f"      mysqldump -u {DB_USER} -p {DB_NAME} > respaldo_{DB_NAME}.sql")
    print()

    try:
        respuesta = input(f"  Escribe el nombre de la base ('{DB_NAME}') para continuar: ")
    except EOFError:
        # Sin terminal interactiva (por ejemplo dentro de otro script) no
        # se puede preguntar, y en la duda no se borra nada.
        print("  No hay terminal para preguntar. Usa --forzar si estas seguro.")
        return False

    if respuesta.strip() != DB_NAME:
        print("  Cancelado: no se toco la base de datos.")
        return False
    return True


def main(forzar=False):
    print(f"Conectando a MySQL/MariaDB en {DB_HOST}:{DB_PORT} ...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
            use_pure=True,
        )
    except Error as e:
        print(f"\nNo se pudo conectar al servidor MySQL: {e}\n")
        print("Revisa que:")
        print("  1. El servidor MySQL este encendido.")
        print("     Si usas XAMPP: abre el Panel de Control y pulsa 'Start' en MySQL.")
        print("  2. Los datos de DB_HOST, DB_PORT, DB_USER y DB_PASSWORD del")
        print("     archivo .env correspondan a tu equipo.")
        print("\nPara un diagnostico completo ejecuta:  python verificar.py\n")
        sys.exit(1)

    cursor = conn.cursor()

    # MySQL en la nube (Aiven, por ejemplo) trae sql_require_primary_key
    # encendido, y schema.sql crea las tablas sin llave primaria para
    # agregarla despues con ALTER TABLE: sin apagarlo, todos los CREATE
    # TABLE fallan. En MySQL local la variable ya esta apagada (o no
    # existe, en MariaDB), asi que si falla se ignora.
    try:
        cursor.execute("SET SESSION sql_require_primary_key = 0")
    except Error:
        pass

    if not confirmar_reconstruccion(cursor, forzar):
        cursor.close()
        conn.close()
        return 1

    # DROP y CREATE, no "CREATE IF NOT EXISTS": si la base sobrevive con su
    # estructura vieja, los CREATE TABLE de schema.sql no se aplican y la
    # base queda a medias (ver el comentario de arriba del archivo).
    print(f"Borrando y creando la base de datos '{DB_NAME}'...")
    cursor.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
    cursor.execute(
        f"CREATE DATABASE `{DB_NAME}` "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
    )
    cursor.execute(f"USE `{DB_NAME}`")

    total_errores = 0
    for archivo, descripcion in (
        ("schema.sql", "estructura"),
        ("seed.sql", "datos iniciales"),
        ("objetos.sql", "vistas, funciones, procedimientos y triggers"),
    ):
        print(f"Ejecutando {archivo} ({descripcion})...")
        total_errores += run_sql_file(cursor, os.path.join(BASE_DIR, archivo))
        conn.commit()

    resumen_objetos(cursor, DB_NAME)

    cursor.close()
    conn.close()

    if total_errores:
        print(f"Base de datos '{DB_NAME}' inicializada con {total_errores} aviso(s).")
    else:
        print(f"Base de datos '{DB_NAME}' inicializada correctamente.")
    return 0


def resumen_objetos(cursor, db_name):
    """Imprime cuantos objetos programables quedaron creados, como verificacion."""
    consultas = {
        "Vistas": (
            "SELECT COUNT(*) FROM information_schema.views "
            "WHERE table_schema = %s"
        ),
        "Funciones": (
            "SELECT COUNT(*) FROM information_schema.routines "
            "WHERE routine_schema = %s AND routine_type = 'FUNCTION'"
        ),
        "Procedimientos": (
            "SELECT COUNT(*) FROM information_schema.routines "
            "WHERE routine_schema = %s AND routine_type = 'PROCEDURE'"
        ),
        "Triggers": (
            "SELECT COUNT(*) FROM information_schema.triggers "
            "WHERE trigger_schema = %s"
        ),
    }

    print("\nObjetos creados en la base de datos:")
    for etiqueta, sql in consultas.items():
        cursor.execute(sql, (db_name,))
        print(f"  {etiqueta:<15} {cursor.fetchone()[0]}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reconstruye la base de datos de Bones & Paws desde cero."
    )
    parser.add_argument("--forzar", action="store_true",
                        help="no preguntar antes de borrar la base existente")
    sys.exit(main(forzar=parser.parse_args().forzar))
