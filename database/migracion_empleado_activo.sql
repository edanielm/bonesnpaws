-- database/migracion_empleado_activo.sql
--
-- Migracion: gestion de personal desde el panel (alta de empleados y
-- desactivar/reactivar su acceso).
--
-- Para quien reconstruye la base de datos desde cero con
-- `python database/init_db.py`, este cambio ya viene incluido en
-- schema.sql: no hace falta correr este archivo.
--
-- Para una base 'bandp' ya existente con datos reales, agrega la columna
-- sin tocar nada mas.
--
-- Uso:
--   mysql -u root -p bandp < database/migracion_empleado_activo.sql

ALTER TABLE `empleado`
  ADD COLUMN `activo` tinyint(1) NOT NULL DEFAULT 1 AFTER `id_rol`;
