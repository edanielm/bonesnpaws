-- =====================================================================
-- database/objetos.sql
--
-- Objetos programables de la base de datos `bandp`:
--   1. Tabla de apoyo para auditoria (unica tabla nueva, solo aditiva)
--   2. Vistas          (vista_*)
--   3. Funciones       (fn_*)
--   4. Procedimientos  (sp_*)
--   5. Triggers        (trg_*)
--
-- Se ejecuta DESPUES de schema.sql y seed.sql (ver database/init_db.py).
-- El archivo es idempotente: cada objeto se elimina antes de recrearse,
-- por lo que puede correrse las veces que haga falta.
--
-- NOTA IMPORTANTE SOBRE EL STOCK
-- El descuento de stock quedo centralizado en los triggers de `detalle`
-- (trg_detalle_ai / trg_detalle_au / trg_detalle_ad). La capa Python ya
-- NO descuenta stock a mano, para que no se descuente dos veces.
-- Ver app/services/factura_service.py.
-- =====================================================================


-- =====================================================================
-- 1. TABLA DE APOYO: auditoria_producto
--    Unica tabla nueva. No modifica ninguna tabla del bandp.sql original,
--    solo registra el historial de cambios que producen los triggers.
-- =====================================================================

CREATE TABLE IF NOT EXISTS `auditoria_producto` (
  `id_auditoria` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `accion` enum('ALTA','PRECIO','STOCK','BAJA') NOT NULL,
  `valor_anterior` varchar(100) DEFAULT NULL,
  `valor_nuevo` varchar(100) DEFAULT NULL,
  `usuario_bd` varchar(100) NOT NULL,
  `fecha` datetime NOT NULL,
  PRIMARY KEY (`id_auditoria`),
  KEY `idx_auditoria_producto` (`id_producto`),
  KEY `idx_auditoria_fecha` (`fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================================================
-- 2. VISTAS
-- =====================================================================

DROP VIEW IF EXISTS `vista_catalogo_productos`;
DROP VIEW IF EXISTS `vista_stock_critico`;
DROP VIEW IF EXISTS `vista_carrito_detalle`;
DROP VIEW IF EXISTS `vista_ventas_detalle`;
DROP VIEW IF EXISTS `vista_resumen_facturas`;
DROP VIEW IF EXISTS `vista_ventas_por_categoria`;
DROP VIEW IF EXISTS `vista_top_productos`;
DROP VIEW IF EXISTS `vista_historial_cliente`;
DROP VIEW IF EXISTS `vista_envios_pendientes`;
DROP VIEW IF EXISTS `vista_equipo`;

--
-- vista_catalogo_productos
-- Catalogo publico ya resuelto: producto + su categoria + su proveedor.
-- Evita repetir el mismo JOIN en cada consulta de la tienda.
--
CREATE VIEW `vista_catalogo_productos` AS
SELECT
    p.id_producto,
    p.codigo,
    p.nombre,
    p.descripcion,
    p.precio,
    p.stock,
    -- Foto principal del producto (Sprint 3: imagen_producto reemplazo a la
    -- columna producto.imagen_url). Si ninguna esta marcada como principal,
    -- se usa la mas antigua cargada; si el producto no tiene fotos, NULL.
    (
        SELECT ip.ruta_imagen
        FROM imagen_producto ip
        WHERE ip.id_producto = p.id_producto
        ORDER BY ip.es_principal DESC, ip.fecha_carga ASC
        LIMIT 1
    )                  AS imagen_url,
    c.id_categoria,
    c.nombre           AS categoria,
    pr.id_proveedor,
    pr.nombre          AS proveedor,
    pr.asesor          AS asesor_proveedor,
    CASE
        WHEN p.stock <= 0  THEN 'Agotado'
        WHEN p.stock < 10  THEN 'Stock bajo'
        ELSE 'Disponible'
    END                AS estado_stock
FROM producto p
JOIN categoria  c  ON c.id_categoria  = p.id_categoria
JOIN proveedor  pr ON pr.id_proveedor = p.id_proveedor
WHERE p.activo = 1;

--
-- vista_stock_critico
-- Productos que hay que reabastecer, con los datos de contacto del proveedor.
--
CREATE VIEW `vista_stock_critico` AS
SELECT
    p.id_producto,
    p.codigo,
    p.nombre           AS producto,
    p.stock,
    c.nombre           AS categoria,
    pr.nombre          AS proveedor,
    pr.asesor,
    pr.telefono        AS telefono_proveedor,
    pr.correo          AS correo_proveedor
FROM producto p
JOIN categoria  c  ON c.id_categoria  = p.id_categoria
JOIN proveedor  pr ON pr.id_proveedor = p.id_proveedor
WHERE p.stock < 10 AND p.activo = 1;

--
-- vista_carrito_detalle
-- Contenido del carrito de cada cliente con el subtotal ya calculado.
--
CREATE VIEW `vista_carrito_detalle` AS
SELECT
    ca.id_carrito,
    ca.id_usuario,
    CONCAT(cl.nombre, ' ', cl.apellido) AS cliente,
    p.id_producto,
    p.nombre                            AS producto,
    p.precio,
    cp.cantidad,
    (p.precio * cp.cantidad)            AS subtotal_linea,
    p.stock                             AS stock_disponible
FROM carrito ca
JOIN cliente          cl ON cl.id_usuario  = ca.id_usuario
JOIN carrito_producto cp ON cp.id_carrito  = ca.id_carrito
JOIN producto         p  ON p.id_producto  = cp.id_producto;

--
-- vista_ventas_detalle
-- Una fila por producto vendido: es la vista base de los reportes.
--
CREATE VIEW `vista_ventas_detalle` AS
SELECT
    f.numero_factura,
    f.fecha,
    f.metodo_pago,
    cl.id_usuario,
    CONCAT(cl.nombre, ' ', cl.apellido) AS cliente,
    cl.correo,
    p.id_producto,
    p.nombre                            AS producto,
    cat.nombre                          AS categoria,
    d.cantidad,
    d.precio_unitario,
    d.subtotal_producto,
    f.total                             AS total_factura
FROM factura   f
JOIN cliente   cl  ON cl.id_usuario   = f.id_usuario
JOIN detalle   d   ON d.numero_factura = f.numero_factura
JOIN producto  p   ON p.id_producto   = d.id_producto
JOIN categoria cat ON cat.id_categoria = p.id_categoria;

--
-- vista_resumen_facturas
-- Una fila por factura, lista para el listado del panel admin.
--
CREATE VIEW `vista_resumen_facturas` AS
SELECT
    f.numero_factura,
    f.fecha,
    CONCAT(cl.nombre, ' ', cl.apellido) AS cliente,
    cl.correo,
    CONCAT(e.nombre, ' ', e.apellido)   AS atendido_por,
    f.metodo_pago,
    f.subtotal,
    f.iva,
    f.costo_envio,
    f.total,
    COUNT(d.id_detalle)                 AS lineas,
    COALESCE(SUM(d.cantidad), 0)        AS unidades,
    COALESCE(en.estado, 'Sin envio')    AS estado_envio
FROM factura  f
JOIN cliente  cl ON cl.id_usuario  = f.id_usuario
JOIN empleado e  ON e.id_empleado  = f.id_empleado
LEFT JOIN detalle d  ON d.numero_factura  = f.numero_factura
LEFT JOIN envio   en ON en.numero_factura = f.numero_factura
GROUP BY
    f.numero_factura, f.fecha, cl.nombre, cl.apellido, cl.correo,
    e.nombre, e.apellido, f.metodo_pago, f.subtotal, f.iva,
    f.costo_envio, f.total, en.estado;

--
-- vista_ventas_por_categoria
-- Cuanto vendio cada categoria (reporte gerencial).
--
CREATE VIEW `vista_ventas_por_categoria` AS
SELECT
    cat.id_categoria,
    cat.nombre                          AS categoria,
    COUNT(DISTINCT d.numero_factura)    AS facturas,
    SUM(d.cantidad)                     AS unidades_vendidas,
    SUM(d.subtotal_producto)            AS ingresos,
    ROUND(AVG(d.precio_unitario), 2)    AS precio_promedio
FROM categoria cat
JOIN producto  p ON p.id_categoria  = cat.id_categoria
JOIN detalle   d ON d.id_producto   = p.id_producto
GROUP BY cat.id_categoria, cat.nombre;

--
-- vista_top_productos
-- Ranking de productos mas vendidos.
--
CREATE VIEW `vista_top_productos` AS
SELECT
    p.id_producto,
    p.nombre                         AS producto,
    cat.nombre                       AS categoria,
    p.precio,
    p.stock,
    SUM(d.cantidad)                  AS unidades_vendidas,
    SUM(d.subtotal_producto)         AS ingresos,
    COUNT(DISTINCT d.numero_factura) AS veces_facturado
FROM producto  p
JOIN categoria cat ON cat.id_categoria = p.id_categoria
JOIN detalle   d   ON d.id_producto    = p.id_producto
GROUP BY p.id_producto, p.nombre, cat.nombre, p.precio, p.stock
ORDER BY unidades_vendidas DESC;

--
-- vista_historial_cliente
-- Cuanto ha comprado cada cliente en total.
--
CREATE VIEW `vista_historial_cliente` AS
SELECT
    cl.id_usuario,
    CONCAT(cl.nombre, ' ', cl.apellido) AS cliente,
    cl.correo,
    cl.telefono,
    COUNT(DISTINCT f.numero_factura)    AS compras,
    COALESCE(SUM(f.total), 0)           AS total_comprado,
    MIN(f.fecha)                        AS primera_compra,
    MAX(f.fecha)                        AS ultima_compra
FROM cliente cl
LEFT JOIN factura f ON f.id_usuario = cl.id_usuario
GROUP BY cl.id_usuario, cl.nombre, cl.apellido, cl.correo, cl.telefono;

--
-- vista_envios_pendientes
-- Envios que todavia no llegaron, con los dias que llevan en transito.
--
CREATE VIEW `vista_envios_pendientes` AS
SELECT
    en.id_envio,
    en.numero_factura,
    en.numero_guia,
    en.estado,
    en.fecha_envio,
    en.fecha_entrega_estimada,
    DATEDIFF(CURDATE(), en.fecha_envio) AS dias_en_transito,
    CASE
        WHEN en.fecha_entrega_estimada < CURDATE() THEN 'Atrasado'
        ELSE 'En tiempo'
    END                                 AS cumplimiento,
    t.nombre                            AS transportadora,
    t.telefono                          AS telefono_transportadora,
    CONCAT(cl.nombre, ' ', cl.apellido) AS cliente,
    cl.direccion,
    f.total
FROM envio          en
JOIN transportadora t  ON t.id_transportadora = en.id_transportadora
JOIN factura        f  ON f.numero_factura    = en.numero_factura
JOIN cliente        cl ON cl.id_usuario       = f.id_usuario
WHERE en.estado <> 'Entregado';

--
-- vista_equipo
-- El personal de la tienda con su rol ya resuelto y cuantas ventas ha
-- atendido cada uno. Evita repetir el JOIN empleado -> rol y es la consulta
-- que responde "quien es administrador y quien es vendedor".
--
CREATE VIEW `vista_equipo` AS
SELECT
    e.id_empleado,
    CONCAT(e.nombre, ' ', e.apellido) AS empleado,
    e.correo,
    e.telefono,
    r.id_rol,
    r.nombre                          AS rol,
    r.descripcion                     AS permisos,
    COUNT(f.numero_factura)           AS ventas_atendidas,
    COALESCE(SUM(f.total), 0)         AS total_facturado
FROM empleado e
JOIN rol      r ON r.id_rol = e.id_rol
LEFT JOIN factura f ON f.id_empleado = e.id_empleado
GROUP BY e.id_empleado, e.nombre, e.apellido, e.correo, e.telefono,
         r.id_rol, r.nombre, r.descripcion;


-- =====================================================================
-- 3. FUNCIONES
-- =====================================================================

DROP FUNCTION IF EXISTS `fn_stock_disponible`;
DROP FUNCTION IF EXISTS `fn_estado_stock`;
DROP FUNCTION IF EXISTS `fn_total_carrito`;
DROP FUNCTION IF EXISTS `fn_total_comprado_cliente`;

DELIMITER $$

--
-- Stock actual de un producto (0 si el producto no existe).
--
CREATE FUNCTION `fn_stock_disponible`(p_id_producto INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_stock INT;
    SELECT stock INTO v_stock FROM producto WHERE id_producto = p_id_producto;
    RETURN COALESCE(v_stock, 0);
END$$

--
-- Etiqueta legible del estado de inventario de un producto.
--
CREATE FUNCTION `fn_estado_stock`(p_id_producto INT)
RETURNS VARCHAR(20)
READS SQL DATA
BEGIN
    DECLARE v_stock INT;
    SET v_stock = fn_stock_disponible(p_id_producto);

    IF v_stock <= 0 THEN
        RETURN 'Agotado';
    ELSEIF v_stock < 10 THEN
        RETURN 'Stock bajo';
    ELSE
        RETURN 'Disponible';
    END IF;
END$$

--
-- Subtotal (sin IVA ni envio) del carrito activo de un cliente.
--
CREATE FUNCTION `fn_total_carrito`(p_id_usuario VARCHAR(11))
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(10,2);
    SELECT COALESCE(SUM(p.precio * cp.cantidad), 0)
      INTO v_total
      FROM carrito          c
      JOIN carrito_producto cp ON cp.id_carrito = c.id_carrito
      JOIN producto         p  ON p.id_producto = cp.id_producto
     WHERE c.id_usuario = p_id_usuario;
    RETURN v_total;
END$$

--
-- Cuanto ha gastado historicamente un cliente.
--
CREATE FUNCTION `fn_total_comprado_cliente`(p_id_usuario VARCHAR(11))
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(12,2);
    SELECT COALESCE(SUM(total), 0) INTO v_total
      FROM factura WHERE id_usuario = p_id_usuario;
    RETURN v_total;
END$$

DELIMITER ;


-- =====================================================================
-- 4. PROCEDIMIENTOS ALMACENADOS
-- =====================================================================

DROP PROCEDURE IF EXISTS `sp_agregar_al_carrito`;
DROP PROCEDURE IF EXISTS `sp_vaciar_carrito`;
DROP PROCEDURE IF EXISTS `sp_registrar_venta`;
DROP PROCEDURE IF EXISTS `sp_registrar_pago`;
DROP PROCEDURE IF EXISTS `sp_registrar_envio`;
DROP PROCEDURE IF EXISTS `sp_actualizar_estado_envio`;
DROP PROCEDURE IF EXISTS `sp_cambiar_precio`;
DROP PROCEDURE IF EXISTS `sp_reponer_stock_masivo`;
DROP PROCEDURE IF EXISTS `sp_reporte_ventas`;
DROP PROCEDURE IF EXISTS `sp_purgar_auditoria`;

DELIMITER $$

--
-- sp_agregar_al_carrito
-- Crea el carrito del cliente si aun no tiene, y suma la cantidad pedida.
-- Valida stock antes de tocar nada.
--
CREATE PROCEDURE `sp_agregar_al_carrito`(
    IN p_id_usuario  VARCHAR(11),
    IN p_id_producto INT,
    IN p_cantidad    INT
)
BEGIN
    DECLARE v_id_carrito INT;
    DECLARE v_actual     INT DEFAULT 0;
    DECLARE v_stock      INT;

    IF p_cantidad < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cantidad debe ser al menos 1.';
    END IF;

    SELECT stock INTO v_stock FROM producto WHERE id_producto = p_id_producto;
    IF v_stock IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto no existe.';
    END IF;

    SELECT id_carrito INTO v_id_carrito
      FROM carrito WHERE id_usuario = p_id_usuario LIMIT 1;

    IF v_id_carrito IS NULL THEN
        INSERT INTO carrito (id_usuario) VALUES (p_id_usuario);
        SET v_id_carrito = LAST_INSERT_ID();
    END IF;

    SELECT cantidad INTO v_actual
      FROM carrito_producto
     WHERE id_carrito = v_id_carrito AND id_producto = p_id_producto;

    SET v_actual = COALESCE(v_actual, 0);

    IF v_stock < (v_actual + p_cantidad) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay suficiente stock disponible.';
    END IF;

    INSERT INTO carrito_producto (id_carrito, id_producto, cantidad)
    VALUES (v_id_carrito, p_id_producto, p_cantidad)
    ON DUPLICATE KEY UPDATE cantidad = cantidad + p_cantidad;
END$$

--
-- sp_vaciar_carrito
--
CREATE PROCEDURE `sp_vaciar_carrito`(IN p_id_usuario VARCHAR(11))
BEGIN
    DELETE cp FROM carrito_producto cp
      JOIN carrito c ON c.id_carrito = cp.id_carrito
     WHERE c.id_usuario = p_id_usuario;
END$$

--
-- sp_registrar_venta
-- Caso de uso completo "Registrar Venta", en una sola transaccion:
--   1. valida que el carrito no este vacio y que haya stock de todo
--   2. calcula subtotal / IVA / envio / total
--   3. crea la factura y su detalle (los triggers descuentan el stock)
--   4. vacia el carrito
-- Devuelve el numero de factura generado en p_numero_factura.
--
CREATE PROCEDURE `sp_registrar_venta`(
    IN  p_id_usuario     VARCHAR(11),
    IN  p_id_empleado    INT,
    IN  p_iva_porcentaje DECIMAL(5,4),
    IN  p_costo_envio    DECIMAL(10,2),
    IN  p_metodo_pago    VARCHAR(20),
    OUT p_numero_factura INT
)
BEGIN
    DECLARE v_subtotal  DECIMAL(10,2);
    DECLARE v_iva       DECIMAL(10,2);
    DECLARE v_total     DECIMAL(10,2);
    DECLARE v_lineas    INT DEFAULT 0;
    DECLARE v_sin_stock INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        DROP TEMPORARY TABLE IF EXISTS tmp_venta;
        RESIGNAL;
    END;

    -- El carrito se congela en una tabla temporal antes de facturar.
    --
    -- No es un capricho: si el INSERT de `detalle` leyera `producto`
    -- directamente, MySQL abortaria con el error 1442, porque el trigger
    -- trg_detalle_ai actualiza esa misma tabla que la sentencia esta
    -- leyendo. Copiando antes los precios, el INSERT solo lee la temporal
    -- y el trigger queda libre para descontar el stock.
    DROP TEMPORARY TABLE IF EXISTS tmp_venta;
    CREATE TEMPORARY TABLE tmp_venta AS
        SELECT cp.id_producto,
               cp.cantidad,
               p.precio,
               p.stock
          FROM carrito          c
          JOIN carrito_producto cp ON cp.id_carrito = c.id_carrito
          JOIN producto         p  ON p.id_producto = cp.id_producto
         WHERE c.id_usuario = p_id_usuario;

    SELECT COUNT(*), COALESCE(SUM(precio * cantidad), 0)
      INTO v_lineas, v_subtotal
      FROM tmp_venta;

    IF v_lineas = 0 THEN
        DROP TEMPORARY TABLE IF EXISTS tmp_venta;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El carrito esta vacio.';
    END IF;

    -- Si algun item pide mas unidades de las que hay, se aborta antes de facturar.
    SELECT COUNT(*) INTO v_sin_stock FROM tmp_venta WHERE stock < cantidad;

    IF v_sin_stock > 0 THEN
        DROP TEMPORARY TABLE IF EXISTS tmp_venta;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente para uno o mas productos del carrito.';
    END IF;

    SET v_iva   = ROUND(v_subtotal * p_iva_porcentaje, 2);
    SET v_total = v_subtotal + v_iva + p_costo_envio;

    START TRANSACTION;

    INSERT INTO factura (fecha, subtotal, iva, costo_envio, total,
                         id_usuario, id_empleado, metodo_pago)
    VALUES (CURDATE(), v_subtotal, v_iva, p_costo_envio, v_total,
            p_id_usuario, p_id_empleado, p_metodo_pago);

    SET p_numero_factura = LAST_INSERT_ID();

    -- Una linea de detalle por cada item. El trigger trg_detalle_ai
    -- se encarga de descontar el stock de cada producto.
    INSERT INTO detalle (numero_factura, id_producto, cantidad,
                         precio_unitario, subtotal_producto)
    SELECT p_numero_factura, id_producto, cantidad,
           precio, (precio * cantidad)
      FROM tmp_venta;

    DELETE cp FROM carrito_producto cp
      JOIN carrito c ON c.id_carrito = cp.id_carrito
     WHERE c.id_usuario = p_id_usuario;

    COMMIT;

    DROP TEMPORARY TABLE IF EXISTS tmp_venta;
END$$

--
-- sp_registrar_pago
-- Guarda el detalle del medio de pago en la tabla que corresponda.
-- De la tarjeta solo se conservan los ultimos 4 digitos.
--
CREATE PROCEDURE `sp_registrar_pago`(
    IN p_numero_factura INT,
    IN p_metodo_pago    VARCHAR(20),
    IN p_banco          VARCHAR(100),
    IN p_numero_cuenta  VARCHAR(30),
    IN p_titular        VARCHAR(100),
    IN p_numero_tarjeta VARCHAR(20),
    IN p_franquicia     VARCHAR(50),
    IN p_vencimiento    DATE
)
BEGIN
    DECLARE v_monto DECIMAL(10,2);

    SELECT total INTO v_monto FROM factura WHERE numero_factura = p_numero_factura;
    IF v_monto IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La factura indicada no existe.';
    END IF;

    IF p_metodo_pago = 'PSE' THEN
        INSERT INTO pse (numero_factura, banco, monto)
        VALUES (p_numero_factura, COALESCE(p_banco, 'No especificado'), v_monto);

    ELSEIF p_metodo_pago = 'Tarjeta' THEN
        INSERT INTO tarjeta (numero_factura, numero_tarjeta, cvv,
                             fecha_vencimiento, franquicia, monto)
        VALUES (p_numero_factura,
                LPAD(RIGHT(COALESCE(p_numero_tarjeta, '0000'), 4), 16, '*'),
                '***',
                COALESCE(p_vencimiento, CURDATE()),
                COALESCE(p_franquicia, 'No especificada'),
                v_monto);

    ELSEIF p_metodo_pago = 'Transferencia' THEN
        INSERT INTO transferencia_bancaria (numero_factura, banco, numero_cuenta,
                                            titular, monto)
        VALUES (p_numero_factura,
                COALESCE(p_banco, 'No especificado'),
                COALESCE(p_numero_cuenta, 'No especificada'),
                COALESCE(p_titular, 'No especificado'),
                v_monto);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Metodo de pago no reconocido.';
    END IF;
END$$

--
-- sp_registrar_envio
-- Genera la guia de una factura y programa la fecha estimada de entrega.
--
CREATE PROCEDURE `sp_registrar_envio`(
    IN  p_numero_factura    INT,
    IN  p_id_transportadora INT,
    IN  p_dias_estimados    INT,
    OUT p_numero_guia       VARCHAR(50)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM factura WHERE numero_factura = p_numero_factura) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La factura indicada no existe.';
    END IF;

    IF EXISTS (SELECT 1 FROM envio WHERE numero_factura = p_numero_factura) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Esa factura ya tiene un envio registrado.';
    END IF;

    SET p_numero_guia = CONCAT('BP-', LPAD(p_numero_factura, 6, '0'),
                               '-', LPAD(p_id_transportadora, 3, '0'));

    INSERT INTO envio (numero_factura, id_transportadora, numero_guia,
                       fecha_envio, fecha_entrega_estimada, estado)
    VALUES (p_numero_factura, p_id_transportadora, p_numero_guia,
            CURDATE(),
            DATE_ADD(CURDATE(), INTERVAL COALESCE(p_dias_estimados, 5) DAY),
            'Pendiente');
END$$

--
-- sp_actualizar_estado_envio
-- Cambia el estado de un envio. Al marcarlo 'Entregado', el trigger
-- trg_envio_bu sella la fecha de entrega real automaticamente.
--
CREATE PROCEDURE `sp_actualizar_estado_envio`(
    IN p_id_envio INT,
    IN p_estado   VARCHAR(20)
)
BEGIN
    IF p_estado NOT IN ('Pendiente', 'En camino', 'Entregado') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Estado de envio no valido.';
    END IF;

    UPDATE envio SET estado = p_estado WHERE id_envio = p_id_envio;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El envio indicado no existe.';
    END IF;
END$$

--
-- sp_cambiar_precio
-- Cambio de precio controlado (el trigger de auditoria deja el rastro).
--
CREATE PROCEDURE `sp_cambiar_precio`(
    IN p_id_producto  INT,
    IN p_nuevo_precio DECIMAL(10,2)
)
BEGIN
    IF p_nuevo_precio <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El precio debe ser mayor que cero.';
    END IF;

    UPDATE producto SET precio = p_nuevo_precio WHERE id_producto = p_id_producto;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto indicado no existe.';
    END IF;
END$$

--
-- sp_reponer_stock_masivo
-- Sube hasta el objetivo todos los productos por debajo del minimo.
--
-- Primero congela la lista en una tabla temporal y despues la recorre con
-- un CURSOR. Se hace en ese orden a proposito: si el cursor leyera
-- directamente de `producto` mientras el LOOP va actualizando esa misma
-- tabla, el recorrido dependeria de como el motor materialice el cursor.
--
CREATE PROCEDURE `sp_reponer_stock_masivo`(
    IN p_stock_minimo   INT,
    IN p_stock_objetivo INT
)
BEGIN
    DECLARE v_fin INT DEFAULT 0;
    DECLARE v_id  INT;

    DECLARE cur_bajos CURSOR FOR SELECT id_producto FROM tmp_reposicion;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;

    IF p_stock_objetivo <= p_stock_minimo THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El stock objetivo debe ser mayor que el minimo.';
    END IF;

    DROP TEMPORARY TABLE IF EXISTS tmp_reposicion;
    CREATE TEMPORARY TABLE tmp_reposicion AS
        SELECT id_producto,
               stock             AS stock_anterior,
               p_stock_objetivo  AS stock_nuevo
          FROM producto
         WHERE stock < p_stock_minimo;

    OPEN cur_bajos;
    bucle: LOOP
        FETCH cur_bajos INTO v_id;
        IF v_fin = 1 THEN
            LEAVE bucle;
        END IF;

        -- El UPDATE dispara trg_producto_au, que deja el movimiento
        -- registrado en auditoria_producto.
        UPDATE producto SET stock = p_stock_objetivo WHERE id_producto = v_id;
    END LOOP;
    CLOSE cur_bajos;

    SELECT r.id_producto,
           p.nombre AS producto,
           r.stock_anterior,
           r.stock_nuevo
      FROM tmp_reposicion r
      JOIN producto p ON p.id_producto = r.id_producto;

    DROP TEMPORARY TABLE IF EXISTS tmp_reposicion;
END$$

--
-- sp_reporte_ventas
-- Reporte de ventas entre dos fechas, agrupado por dia.
--
CREATE PROCEDURE `sp_reporte_ventas`(
    IN p_fecha_inicio DATE,
    IN p_fecha_fin    DATE
)
BEGIN
    IF p_fecha_inicio > p_fecha_fin THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La fecha inicial no puede ser posterior a la final.';
    END IF;

    -- Las unidades se agregan en una subconsulta y no con un JOIN directo
    -- a `detalle`: unir factura con sus lineas multiplicaria cada factura
    -- por su numero de lineas y falsearia los importes.
    SELECT
        f.fecha,
        COUNT(*)                     AS facturas,
        COALESCE(SUM(u.unidades), 0) AS unidades,
        SUM(f.subtotal)              AS subtotal,
        SUM(f.iva)                   AS iva,
        SUM(f.costo_envio)           AS costo_envio,
        SUM(f.total)                 AS total_dia,
        ROUND(AVG(f.total), 2)       AS ticket_promedio
    FROM factura f
    LEFT JOIN (
        SELECT numero_factura, SUM(cantidad) AS unidades
          FROM detalle
         GROUP BY numero_factura
    ) u ON u.numero_factura = f.numero_factura
    WHERE f.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
    GROUP BY f.fecha
    ORDER BY f.fecha;
END$$

--
-- sp_purgar_auditoria
-- Borra el rastro de auditoria mas viejo que p_dias dias.
--
-- `auditoria_producto` recibe una fila por cada alta, cambio de precio,
-- movimiento de stock y baja de producto. Como cada venta mueve el stock,
-- la tabla crece sola y sin limite: es la unica del esquema que no para de
-- engordar aunque nadie toque el catalogo. Este procedimiento es la
-- politica de retencion: se conserva lo reciente y se descarta lo antiguo.
--
-- No borra nada de golpe sin avisar: primero informa cuantas filas va a
-- quitar y cuantas quedan, para poder ejecutarlo con confianza.
--
--     CALL sp_purgar_auditoria(180);   -- conserva los ultimos 6 meses
--
CREATE PROCEDURE `sp_purgar_auditoria`(IN p_dias INT)
BEGIN
    DECLARE v_corte    DATETIME;
    DECLARE v_a_borrar INT;

    IF p_dias IS NULL OR p_dias < 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Hay que conservar al menos un dia de auditoria.';
    END IF;

    SET v_corte = DATE_SUB(NOW(), INTERVAL p_dias DAY);

    SELECT COUNT(*) INTO v_a_borrar
      FROM auditoria_producto WHERE fecha < v_corte;

    DELETE FROM auditoria_producto WHERE fecha < v_corte;

    SELECT v_corte                              AS purgado_antes_de,
           v_a_borrar                           AS filas_eliminadas,
           (SELECT COUNT(*) FROM auditoria_producto) AS filas_conservadas;
END$$

DELIMITER ;


-- =====================================================================
-- 5. TRIGGERS
-- =====================================================================

DROP TRIGGER IF EXISTS `trg_producto_bi`;
DROP TRIGGER IF EXISTS `trg_producto_ai`;
DROP TRIGGER IF EXISTS `trg_producto_bu`;
DROP TRIGGER IF EXISTS `trg_producto_au`;
DROP TRIGGER IF EXISTS `trg_producto_ad`;
DROP TRIGGER IF EXISTS `trg_carrito_producto_bi`;
DROP TRIGGER IF EXISTS `trg_carrito_producto_bu`;
DROP TRIGGER IF EXISTS `trg_factura_bi`;
DROP TRIGGER IF EXISTS `trg_detalle_bi`;
DROP TRIGGER IF EXISTS `trg_detalle_ai`;
DROP TRIGGER IF EXISTS `trg_detalle_au`;
DROP TRIGGER IF EXISTS `trg_detalle_ad`;
DROP TRIGGER IF EXISTS `trg_envio_bi`;
DROP TRIGGER IF EXISTS `trg_envio_bu`;

DELIMITER $$

-- ---------------------------------------------------------------------
-- producto: validaciones + auditoria
-- ---------------------------------------------------------------------

--
-- No se puede dar de alta un producto con precio, stock o codigo invalidos.
--
-- El codigo se normaliza a mayusculas y sin espacios sobrantes ANTES de
-- guardarlo. Eso es lo que hace util a la restriccion UNIQUE: sin esto,
-- 'per-0001', 'PER-0001 ' y 'PER-0001' serian tres valores distintos para
-- MySQL y el mismo producto entraria tres veces.
--
CREATE TRIGGER `trg_producto_bi` BEFORE INSERT ON `producto`
FOR EACH ROW
BEGIN
    IF NEW.precio <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El precio del producto debe ser mayor que cero.';
    END IF;
    IF NEW.stock < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El stock del producto no puede ser negativo.';
    END IF;
    SET NEW.nombre = TRIM(NEW.nombre);
    SET NEW.codigo = UPPER(TRIM(NEW.codigo));
    IF NEW.codigo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto debe tener un codigo unico.';
    END IF;
END$$

CREATE TRIGGER `trg_producto_ai` AFTER INSERT ON `producto`
FOR EACH ROW
BEGIN
    INSERT INTO auditoria_producto
        (id_producto, accion, valor_anterior, valor_nuevo, usuario_bd, fecha)
    VALUES
        (NEW.id_producto, 'ALTA', NULL,
         CONCAT('precio=', NEW.precio, ' stock=', NEW.stock), CURRENT_USER(), NOW());
END$$

--
-- Las mismas validaciones al editar.
--
CREATE TRIGGER `trg_producto_bu` BEFORE UPDATE ON `producto`
FOR EACH ROW
BEGIN
    IF NEW.precio <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El precio del producto debe ser mayor que cero.';
    END IF;
    IF NEW.stock < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El stock no puede quedar negativo.';
    END IF;
    SET NEW.nombre = TRIM(NEW.nombre);
    SET NEW.codigo = UPPER(TRIM(NEW.codigo));
    IF NEW.codigo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto debe tener un codigo unico.';
    END IF;
END$$

--
-- Deja rastro de cada cambio de precio y de cada movimiento de stock.
--
CREATE TRIGGER `trg_producto_au` AFTER UPDATE ON `producto`
FOR EACH ROW
BEGIN
    IF NEW.precio <> OLD.precio THEN
        INSERT INTO auditoria_producto
            (id_producto, accion, valor_anterior, valor_nuevo, usuario_bd, fecha)
        VALUES
            (NEW.id_producto, 'PRECIO', OLD.precio, NEW.precio, CURRENT_USER(), NOW());
    END IF;

    IF NEW.stock <> OLD.stock THEN
        INSERT INTO auditoria_producto
            (id_producto, accion, valor_anterior, valor_nuevo, usuario_bd, fecha)
        VALUES
            (NEW.id_producto, 'STOCK', OLD.stock, NEW.stock, CURRENT_USER(), NOW());
    END IF;
END$$

CREATE TRIGGER `trg_producto_ad` AFTER DELETE ON `producto`
FOR EACH ROW
BEGIN
    INSERT INTO auditoria_producto
        (id_producto, accion, valor_anterior, valor_nuevo, usuario_bd, fecha)
    VALUES
        (OLD.id_producto, 'BAJA',
         CONCAT(OLD.nombre, ' precio=', OLD.precio, ' stock=', OLD.stock),
         NULL, CURRENT_USER(), NOW());
END$$

-- ---------------------------------------------------------------------
-- carrito_producto: nadie puede reservar mas de lo que hay
-- ---------------------------------------------------------------------

CREATE TRIGGER `trg_carrito_producto_bi` BEFORE INSERT ON `carrito_producto`
FOR EACH ROW
BEGIN
    DECLARE v_stock  INT;
    DECLARE v_activo TINYINT;

    IF NEW.cantidad < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cantidad en el carrito debe ser al menos 1.';
    END IF;

    SELECT stock, activo INTO v_stock, v_activo FROM producto WHERE id_producto = NEW.id_producto;
    IF v_activo = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ese producto ya no esta disponible.';
    END IF;
    IF v_stock < NEW.cantidad THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay suficiente stock para agregar al carrito.';
    END IF;
END$$

CREATE TRIGGER `trg_carrito_producto_bu` BEFORE UPDATE ON `carrito_producto`
FOR EACH ROW
BEGIN
    DECLARE v_stock INT;

    IF NEW.cantidad < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cantidad en el carrito debe ser al menos 1.';
    END IF;

    SELECT stock INTO v_stock FROM producto WHERE id_producto = NEW.id_producto;
    IF v_stock < NEW.cantidad THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay suficiente stock para esa cantidad.';
    END IF;
END$$

-- ---------------------------------------------------------------------
-- factura: coherencia de los totales
-- ---------------------------------------------------------------------

--
-- El total siempre se recalcula en la base: subtotal + iva + envio.
-- Asi ningun cliente (app, phpMyAdmin, script) puede guardar un total falso.
--
CREATE TRIGGER `trg_factura_bi` BEFORE INSERT ON `factura`
FOR EACH ROW
BEGIN
    IF NEW.subtotal < 0 OR NEW.iva < 0 OR NEW.costo_envio < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Los importes de la factura no pueden ser negativos.';
    END IF;

    IF NEW.fecha IS NULL THEN
        SET NEW.fecha = CURDATE();
    END IF;

    SET NEW.total = NEW.subtotal + NEW.iva + NEW.costo_envio;
END$$

-- ---------------------------------------------------------------------
-- detalle: control de stock (unica fuente de verdad)
-- ---------------------------------------------------------------------

--
-- Valida stock y recalcula el subtotal de la linea antes de guardarla.
--
CREATE TRIGGER `trg_detalle_bi` BEFORE INSERT ON `detalle`
FOR EACH ROW
BEGIN
    DECLARE v_stock  INT;
    DECLARE v_nombre VARCHAR(100);
    DECLARE v_activo TINYINT;
    DECLARE v_msg    VARCHAR(255);

    IF NEW.cantidad < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cantidad facturada debe ser al menos 1.';
    END IF;

    SELECT stock, nombre, activo INTO v_stock, v_nombre, v_activo
      FROM producto WHERE id_producto = NEW.id_producto;

    IF v_activo = 0 THEN
        SET v_msg = CONCAT('"', v_nombre, '" ya no esta disponible.');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    IF v_stock < NEW.cantidad THEN
        SET v_msg = CONCAT('Stock insuficiente para "', v_nombre, '".');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    SET NEW.subtotal_producto = NEW.cantidad * NEW.precio_unitario;
END$$

--
-- Descuenta el stock vendido. Es el UNICO lugar donde baja el inventario
-- por una venta: la capa Python ya no lo hace.
--
CREATE TRIGGER `trg_detalle_ai` AFTER INSERT ON `detalle`
FOR EACH ROW
BEGIN
    UPDATE producto
       SET stock = stock - NEW.cantidad
     WHERE id_producto = NEW.id_producto;
END$$

--
-- Si se corrige una linea ya facturada, se ajusta solo la diferencia.
--
CREATE TRIGGER `trg_detalle_au` AFTER UPDATE ON `detalle`
FOR EACH ROW
BEGIN
    IF NEW.id_producto = OLD.id_producto THEN
        UPDATE producto
           SET stock = stock + OLD.cantidad - NEW.cantidad
         WHERE id_producto = NEW.id_producto;
    ELSE
        UPDATE producto SET stock = stock + OLD.cantidad
         WHERE id_producto = OLD.id_producto;
        UPDATE producto SET stock = stock - NEW.cantidad
         WHERE id_producto = NEW.id_producto;
    END IF;
END$$

--
-- Al anular una linea, el stock vuelve al inventario.
--
CREATE TRIGGER `trg_detalle_ad` AFTER DELETE ON `detalle`
FOR EACH ROW
BEGIN
    UPDATE producto
       SET stock = stock + OLD.cantidad
     WHERE id_producto = OLD.id_producto;
END$$

-- ---------------------------------------------------------------------
-- envio: fechas coherentes
-- ---------------------------------------------------------------------

CREATE TRIGGER `trg_envio_bi` BEFORE INSERT ON `envio`
FOR EACH ROW
BEGIN
    IF NEW.fecha_envio IS NULL THEN
        SET NEW.fecha_envio = CURDATE();
    END IF;
    IF NEW.fecha_entrega_estimada IS NULL THEN
        SET NEW.fecha_entrega_estimada = DATE_ADD(NEW.fecha_envio, INTERVAL 5 DAY);
    END IF;
    IF NEW.fecha_entrega_estimada < NEW.fecha_envio THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La entrega estimada no puede ser anterior al envio.';
    END IF;
END$$

--
-- Al pasar a 'Entregado' se sella la fecha real automaticamente;
-- si vuelve atras, se limpia.
--
CREATE TRIGGER `trg_envio_bu` BEFORE UPDATE ON `envio`
FOR EACH ROW
BEGIN
    IF NEW.estado = 'Entregado' AND OLD.estado <> 'Entregado'
       AND NEW.fecha_entrega_real IS NULL THEN
        SET NEW.fecha_entrega_real = CURDATE();
    END IF;

    IF NEW.estado <> 'Entregado' THEN
        SET NEW.fecha_entrega_real = NULL;
    END IF;
END$$

DELIMITER ;
