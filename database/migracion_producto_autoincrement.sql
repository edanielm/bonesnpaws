-- =====================================================================
-- database/migracion_producto_autoincrement.sql
--
-- Devuelve el AUTO_INCREMENT a `producto.id_producto` y crea el indice
-- FULLTEXT del buscador del catalogo.
--
-- EL PROBLEMA
-- En un sprint anterior se le quito el AUTO_INCREMENT a `id_producto` para
-- evitar que el mismo articulo entrara dos veces al catalogo, y el id pasaba
-- a calcularlo la aplicacion asi:
--
--     siguiente_id = SELECT MAX(id_producto) + 1 FROM producto
--
-- Eso no hacia falta -quien impide el duplicado es la restriccion UNIQUE de
-- `codigo`, que sigue puesta- y ademas abria un problema nuevo: si dos
-- personas del equipo guardaban un producto al mismo tiempo, las dos leian
-- el mismo MAX y la segunda chocaba con una llave primaria ya usada. El
-- mismo patron estaba en factura, detalle y carrito, donde el
-- AUTO_INCREMENT nunca se habia quitado y el calculo manual solo estorbaba.
--
-- LA SOLUCION
-- El id lo vuelve a asignar el motor, que es el unico que puede hacerlo sin
-- condiciones de carrera. La aplicacion ya no lo calcula
-- (ver app/services/producto_service.py).
--
-- CUANDO EJECUTARLO
-- Solo en una base `bandp` que ya existia antes de este sprint. Si se crea
-- desde cero con `python database/init_db.py`, schema.sql ya la deja bien.
--
-- Uso:
--     mysql -u root -p bandp < database/migracion_producto_autoincrement.sql
-- =====================================================================

-- 1. AUTO_INCREMENT de vuelta.
--    El contador arranca despues del id mas alto que ya exista, para no
--    chocar con los productos sembrados.
SET @siguiente = (SELECT COALESCE(MAX(id_producto), 0) + 1 FROM producto);

ALTER TABLE `producto`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT;

SET @sql = CONCAT('ALTER TABLE `producto` AUTO_INCREMENT = ', @siguiente);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. Indice FULLTEXT para el buscador.
--    El catalogo buscaba con `nombre LIKE '%texto%'`, y un LIKE que empieza
--    con comodin no puede usar ningun indice: recorre la tabla entera. Con
--    este indice, MySQL resuelve la busqueda con MATCH ... AGAINST
--    (ver ProductoService._aplicar_busqueda).
--
--    Si el indice ya existe, MySQL avisa con un error 1061 que se puede
--    ignorar sin problema.
ALTER TABLE `producto`
  ADD FULLTEXT KEY `ft_producto_busqueda` (`nombre`, `descripcion`);

-- =====================================================================
-- COMPROBACION
--
--   SHOW CREATE TABLE producto;
--     -> `id_producto` int(11) NOT NULL AUTO_INCREMENT
--     -> FULLTEXT KEY `ft_producto_busqueda` (`nombre`,`descripcion`)
--
--   -- El buscador ya usa el indice en vez de recorrer la tabla:
--   EXPLAIN SELECT * FROM producto
--    WHERE MATCH(nombre, descripcion) AGAINST ('+alimento*' IN BOOLEAN MODE);
--     -> type: fulltext
-- =====================================================================
