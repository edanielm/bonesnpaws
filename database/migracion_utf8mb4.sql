-- =====================================================================
-- database/migracion_utf8mb4.sql
--
-- Pasa toda la base `bandp` de latin1 a utf8mb4.
--
-- EL PROBLEMA
-- Las tablas venian del dump original creadas con
-- `CHARSET=latin1 COLLATE=latin1_swedish_ci`, pero la aplicacion se conecta
-- pidiendo utf8mb4 (ver SQLALCHEMY_DATABASE_URI en app/config.py). Ese
-- desajuste entre lo que guarda la tabla y lo que habla la conexion es la
-- causa tipica de que las tildes y la "ñ" se vean mal ("Medellín" ->
-- "MedellÃ­n"), y en el catalogo de Bones & Paws casi todo lleva tilde:
-- nombres de clientes, ciudades, descripciones de producto.
--
-- LA SOLUCION
-- CONVERT TO CHARACTER SET reescribe las columnas de texto de cada tabla al
-- juego de caracteres nuevo, convirtiendo los datos que ya estan dentro. Se
-- usa utf8mb4 (no el viejo utf8 de MySQL, que solo cubre 3 bytes) con la
-- collation utf8mb4_unicode_ci, que ordena y compara segun las reglas del
-- espanol.
--
-- CUANDO EJECUTARLO
-- Solo en una base `bandp` que ya existia antes de este sprint. Si la base
-- se crea desde cero con `python database/init_db.py`, no hace falta:
-- schema.sql ya crea todas las tablas en utf8mb4.
--
-- Uso:
--     mysql -u root -p bandp < database/migracion_utf8mb4.sql
--
-- Es idempotente: correrlo dos veces no rompe nada (la segunda vez las
-- tablas ya estan en utf8mb4 y la conversion no cambia nada).
--
-- IMPORTANTE: haz una copia de la base antes de ejecutarlo, como con
-- cualquier migracion que toca datos:
--     mysqldump -u root -p bandp > respaldo_bandp.sql
-- =====================================================================

-- 1. La base de datos en si, para que las tablas nuevas nazcan en utf8mb4
ALTER DATABASE `bandp`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Se retiran temporalmente las dos llaves foraneas de columnas de TEXTO.
--
--    Las dos puntas de una llave foranea tienen que estar en el mismo juego
--    de caracteres. Como las tablas se convierten de a una, en el momento de
--    convertir la primera las puntas dejarian de coincidir y MariaDB aborta:
--
--        ERROR 1832: Cannot change column 'id_usuario':
--                    used in a foreign key constraint 'carrito_ibfk_1'
--
--    Y no basta con `SET FOREIGN_KEY_CHECKS = 0`: MariaDB sigue rechazando
--    el cambio de charset de una columna con llave foranea aunque las
--    comprobaciones esten apagadas. Hay que quitar la restriccion, convertir
--    y volver a ponerla.
--
--    Solo hacen falta estas dos de todo el esquema. El resto de llaves
--    foraneas son sobre columnas INT, y un entero no tiene juego de
--    caracteres, asi que la conversion no las afecta:
--
--        SELECT k.CONSTRAINT_NAME, k.TABLE_NAME, k.COLUMN_NAME
--          FROM information_schema.KEY_COLUMN_USAGE k
--          JOIN information_schema.COLUMNS c
--            ON c.TABLE_SCHEMA = k.TABLE_SCHEMA
--           AND c.TABLE_NAME   = k.TABLE_NAME
--           AND c.COLUMN_NAME  = k.COLUMN_NAME
--         WHERE k.TABLE_SCHEMA = 'bandp'
--           AND k.REFERENCED_TABLE_NAME IS NOT NULL
--           AND c.CHARACTER_SET_NAME IS NOT NULL;
--
--    Ambas son `id_usuario VARCHAR(11)` apuntando a `cliente.id_usuario`.
ALTER TABLE `carrito` DROP FOREIGN KEY `carrito_ibfk_1`;
ALTER TABLE `factura` DROP FOREIGN KEY `factura_ibfk_1`;

-- 3. Cada tabla con sus datos
--    (el orden no importa: ya no hay ninguna dependencia de charset entre
--    ellas mientras dura la conversion)
ALTER TABLE `carrito`                CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `carrito_producto`       CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `categoria`              CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `cliente`                CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `detalle`                CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `rol`                    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `empleado`               CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `envio`                  CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `factura`                CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `metodo_pago`            CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `producto`               CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `imagen_producto`        CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `proveedor`              CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `pse`                    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `tarjeta`                CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `transferencia_bancaria` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `transportadora`         CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- La tabla de auditoria solo existe si ya se ejecuto objetos.sql
ALTER TABLE `auditoria_producto`     CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 4. Se vuelven a poner las dos llaves foraneas, identicas a como estaban
--    (sin ON DELETE ni ON UPDATE, igual que en schema.sql). Ahora las dos
--    puntas estan en utf8mb4 y MariaDB las acepta sin problema.
--
--    Que este ALTER pase sin error es, ademas, la prueba de que no quedaron
--    filas huerfanas: MariaDB valida todas las existentes al crear la
--    restriccion.
ALTER TABLE `carrito`
  ADD CONSTRAINT `carrito_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `cliente` (`id_usuario`);
ALTER TABLE `factura`
  ADD CONSTRAINT `factura_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `cliente` (`id_usuario`);

-- =====================================================================
-- COMPROBACION
-- Despues de correrlo, esta consulta no debe devolver ninguna fila:
--
--     SELECT table_name, table_collation
--       FROM information_schema.tables
--      WHERE table_schema = 'bandp'
--        AND table_collation NOT LIKE 'utf8mb4%';
--
-- Y las tildes deben verse bien:
--     SELECT nombre, direccion FROM cliente WHERE direccion LIKE '%Medell%';
-- =====================================================================
