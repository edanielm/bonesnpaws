-- database/migracion_imagen_producto.sql
--
-- Migracion del Sprint 3: fotos de producto (multi-imagen).
--
-- Para quien reconstruye la base de datos desde cero con
-- `python database/init_db.py`, este cambio ya viene incluido en
-- schema.sql y seed.sql: no hace falta correr este archivo.
--
-- Este script es para quien ya tiene una base 'bandp' con datos reales
-- (no de prueba) y no quiere volver a correr init_db.py -que recrea las
-- tablas desde cero y perderia esos datos-. Aplica el mismo cambio de
-- forma incremental:
--   1. Crea `imagen_producto` (una fila por foto, con `es_principal`
--      marcando cual se muestra como miniatura).
--   2. Copia el valor que hoy tiene cada producto en `producto.imagen_url`
--      como su primera foto principal, para no perder lo que ya estaba
--      cargado.
--   3. Elimina `producto.imagen_url`: la reemplaza `imagen_producto`.
--
-- Uso:
--   mysql -u root -p bandp < database/migracion_imagen_producto.sql
-- o pegando el contenido en la pestaña SQL de phpMyAdmin.
--
-- Despues de correr esto, vuelve a ejecutar database/objetos.sql (o
-- `python database/init_db.py`, que ya lo hace): `vista_catalogo_productos`
-- todavia selecciona la vieja columna `producto.imagen_url` hasta que se
-- recrea con la definicion nueva (trae la foto principal de imagen_producto).

-- 1. Tabla nueva ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS `imagen_producto` (
  `id_imagen` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  `es_principal` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_carga` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_imagen`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `imagen_producto_ibfk_1` FOREIGN KEY (`id_producto`)
    REFERENCES `producto` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Migrar la imagen que ya tenia cada producto -------------------------

INSERT INTO `imagen_producto` (`id_producto`, `ruta_imagen`, `es_principal`)
SELECT `id_producto`, `imagen_url`, 1
FROM `producto`
WHERE `imagen_url` IS NOT NULL AND `imagen_url` <> '';

-- 3. La columna vieja queda reemplazada por la tabla ----------------------

ALTER TABLE `producto` DROP COLUMN `imagen_url`;
