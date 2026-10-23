-- database/migracion_codigo_recuperacion.sql
--
-- Migracion: recuperar la contrasena con un codigo enviado al correo.
--
-- Crea la tabla `codigo_recuperacion`, donde vive el codigo de 6 digitos
-- que la tienda le manda por correo a un cliente que olvido su
-- contrasena. De cada codigo se guarda solo el hash (nunca el numero en
-- claro), cuando vence, cuantas veces se escribio mal y si ya se uso.
--
-- Para quien reconstruye la base desde cero con
-- `python database/init_db.py`, este cambio ya viene incluido en
-- schema.sql: no hace falta correr este archivo.
--
-- Uso:
--   mysql -u root -p bandp < database/migracion_codigo_recuperacion.sql

CREATE TABLE IF NOT EXISTS `codigo_recuperacion` (
  `id_codigo` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` varchar(11) NOT NULL,
  `codigo_hash` varchar(255) NOT NULL,
  `creado_en` datetime NOT NULL,
  `expira_en` datetime NOT NULL,
  `intentos` int(11) NOT NULL DEFAULT 0,
  `usado` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_codigo`),
  KEY `ix_codigo_recuperacion_id_usuario` (`id_usuario`),
  CONSTRAINT `codigo_recuperacion_ibfk_1`
    FOREIGN KEY (`id_usuario`) REFERENCES `cliente` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
