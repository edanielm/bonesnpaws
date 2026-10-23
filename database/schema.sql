-- phpMyAdmin SQL Dump
-- version 5.2.1
-- httpswww.phpmyadmin.net
--
-- Servidor 127.0.0.1
-- Tiempo de generación 30-07-2026 a las 020557
-- Versión del servidor 10.4.32-MariaDB
-- Versión de PHP 8.2.12

SET SQL_MODE = NO_AUTO_VALUE_ON_ZERO;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos `bandp`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrito`
--

CREATE TABLE `carrito` (
  `id_carrito` int(11) NOT NULL,
  `id_usuario` varchar(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `carrito`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrito_producto`
--

CREATE TABLE `carrito_producto` (
  `id_carrito` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `carrito_producto`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categoria`
--

CREATE TABLE `categoria` (
  `id_categoria` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `categoria`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cliente`
--

CREATE TABLE `cliente` (
  `id_usuario` varchar(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `cliente`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `codigo_recuperacion`
--

CREATE TABLE `codigo_recuperacion` (
  `id_codigo` int(11) NOT NULL,
  `id_usuario` varchar(11) NOT NULL,
  `codigo_hash` varchar(255) NOT NULL,
  `creado_en` datetime NOT NULL,
  `expira_en` datetime NOT NULL,
  `intentos` int(11) NOT NULL DEFAULT 0,
  `usado` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- NOTA: tabla nueva del Sprint 5 (no existia en el bandp.sql original).
-- Guarda el codigo de un solo uso que la tienda manda por correo cuando
-- un cliente olvida su contrasena. De cada codigo se guarda solo el hash
-- -igual que con las contrasenas-, mas su vencimiento, cuantas veces se
-- escribio mal (`intentos`) y si ya se gasto (`usado`). Los codigos se
-- borran con el cliente (ON DELETE CASCADE): no son historico contable
-- como las facturas.

--
-- Volcado de datos para la tabla `codigo_recuperacion`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle`
--

CREATE TABLE `detalle` (
  `id_detalle` int(11) NOT NULL,
  `numero_factura` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal_producto` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `detalle`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol`
--
-- Catalogo de roles del personal de la tienda. Define que puede hacer cada
-- empleado dentro del panel: el Administrador ve todo (estadisticas, cuentas
-- de clientes y catalogo) y el Vendedor solo gestiona catalogo y consulta
-- clientes. Se separa en su propia tabla en vez de guardar el rol como texto
-- en `empleado` para que los roles sean un dato controlado (no se pueden
-- escribir mal) y para poder agregar roles nuevos sin tocar la estructura.
--

CREATE TABLE `rol` (
  `id_rol` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `rol`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleado`
--
-- 'id_rol' es el unico campo agregado respecto al bandp.sql original:
-- enlaza cada empleado con su rol. Por defecto 2 (Vendedor), que es el
-- permiso mas restringido, para que un empleado nuevo nunca quede como
-- administrador por descuido.
--

CREATE TABLE `empleado` (
  `id_empleado` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `id_rol` int(11) NOT NULL DEFAULT 2,
  `activo` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- NOTA: 'activo' se agrego en el panel de gestion de personal. Un empleado
-- que ya no sigue en la empresa no se borra (sus facturas son parte del
-- historico de ventas y la llave foranea factura -> empleado no permite
-- dejarlas huerfanas): se pone activo=0, que le bloquea el login
-- (AuthService.login_empleado exige activo=True) y le cierra cualquier
-- sesion que ya tuviera abierta (ver requiere_staff en decoradores.py).

--
-- Volcado de datos para la tabla `empleado`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `envio`
--

CREATE TABLE `envio` (
  `id_envio` int(11) NOT NULL,
  `numero_factura` int(11) NOT NULL,
  `id_transportadora` int(11) NOT NULL,
  `numero_guia` varchar(50) NOT NULL,
  `fecha_envio` date DEFAULT NULL,
  `fecha_entrega_estimada` date DEFAULT NULL,
  `fecha_entrega_real` date DEFAULT NULL,
  `estado` enum('Pendiente','En camino','Entregado') DEFAULT 'Pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `envio`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `factura`
--

CREATE TABLE `factura` (
  `numero_factura` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `iva` decimal(10,2) NOT NULL,
  `costo_envio` decimal(10,2) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `id_usuario` varchar(11) NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `metodo_pago` enum('Tarjeta','PSE','Transferencia') NOT NULL DEFAULT 'Tarjeta'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `factura`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodo_pago`
--

CREATE TABLE `metodo_pago` (
  `id_metodo` int(11) NOT NULL,
  `nombre_metodo` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `metodo_pago`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto`
--

CREATE TABLE `producto` (
  `id_producto` int(11) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `id_categoria` int(11) NOT NULL,
  `id_proveedor` int(11) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- NOTA: 'activo' y 'codigo' son los UNICOS cambios de esquema respecto al
-- bandp.sql original. Aprobados explicitamente por el cliente:
--   - activo: borrado logico. Un producto ya vendido no se puede borrar de
--     verdad (la llave foranea detalle -> producto lo impide, para no dejar
--     facturas historicas huerfanas). En vez de eso, "Eliminar" pone
--     activo=0: el producto desaparece de la tienda y del catalogo activo,
--     pero la fila sigue existiendo para que las facturas viejas conserven
--     su nombre y precio.
--   - codigo: codigo unico de referencia del producto (PER-0001, GAT-0012,
--     OTR-0007...). Es el identificador que usa la tienda para no cargar dos
--     veces el mismo articulo: la restriccion UNIQUE de mas abajo hace que la
--     base de datos rechace un producto repetido, sin depender de que la
--     aplicacion lo valide.
--
--     'id_producto' sigue siendo la llave numerica interna que referencian
--     `detalle` y `carrito_producto` (por eso no se elimina: romperia el
--     historial de facturas) y lo asigna el motor con AUTO_INCREMENT.
--
--     NOTA DE SPRINT: durante un tiempo se le quito el AUTO_INCREMENT y el
--     id lo calculaba la aplicacion con MAX(id_producto)+1, creyendo que asi
--     se evitaban productos duplicados. No era necesario -quien impide el
--     duplicado es el UNIQUE de `codigo`- y ademas era peligroso: si dos
--     personas guardaban un producto al mismo tiempo, las dos leian el mismo
--     maximo y la segunda chocaba con la llave primaria. Se restituyo el
--     AUTO_INCREMENT (ver database/migracion_producto_autoincrement.sql).

--
-- Volcado de datos para la tabla `producto`
--


--
-- Productos nuevos agregados en las categorias restantes (Perros, Gatos, Otros)
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `imagen_producto`
--

CREATE TABLE `imagen_producto` (
  `id_imagen` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  `es_principal` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_carga` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- NOTA: tabla nueva del Sprint 3 (no existia en el bandp.sql original).
-- Un producto puede tener varias fotos; `es_principal` marca cual se usa
-- como miniatura en catalogo, listado admin, detalle y carrito. Se
-- relaciona por 'id_producto' -igual que `detalle` y `carrito_producto`-
-- para no romper la convencion de llaves foraneas del resto del esquema:
-- 'codigo' sigue siendo solo el identificador de negocio del producto, no
-- una llave real. Reemplaza a la antigua columna `producto.imagen_url`
-- (una sola imagen por producto), eliminada en este mismo archivo.

--
-- Volcado de datos para la tabla `imagen_producto`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedor`
--

CREATE TABLE `proveedor` (
  `id_proveedor` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `asesor` varchar(100) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `proveedor`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pse`
--

CREATE TABLE `pse` (
  `id_pse` int(11) NOT NULL,
  `numero_factura` int(11) NOT NULL,
  `banco` varchar(100) NOT NULL,
  `monto` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `pse`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tarjeta`
--

CREATE TABLE `tarjeta` (
  `id_tarjeta` int(11) NOT NULL,
  `numero_factura` int(11) NOT NULL,
  `numero_tarjeta` varchar(20) NOT NULL,
  `cvv` varchar(4) NOT NULL,
  `fecha_vencimiento` date NOT NULL,
  `franquicia` varchar(50) NOT NULL,
  `monto` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `tarjeta`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `transferencia_bancaria`
--

CREATE TABLE `transferencia_bancaria` (
  `id_transferencia` int(11) NOT NULL,
  `numero_factura` int(11) NOT NULL,
  `banco` varchar(100) NOT NULL,
  `numero_cuenta` varchar(30) NOT NULL,
  `titular` varchar(100) NOT NULL,
  `monto` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `transferencia_bancaria`
--


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `transportadora`
--

CREATE TABLE `transportadora` (
  `id_transportadora` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `transportadora`
--


--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `carrito`
--
ALTER TABLE `carrito`
  ADD PRIMARY KEY (`id_carrito`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `carrito_producto`
--
ALTER TABLE `carrito_producto`
  ADD PRIMARY KEY (`id_carrito`,`id_producto`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `categoria`
--
ALTER TABLE `categoria`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Indices de la tabla `cliente`
--
ALTER TABLE `cliente`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- Indices de la tabla `codigo_recuperacion`
--
ALTER TABLE `codigo_recuperacion`
  ADD PRIMARY KEY (`id_codigo`),
  ADD KEY `ix_codigo_recuperacion_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `detalle`
--
ALTER TABLE `detalle`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `numero_factura` (`numero_factura`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `rol`
--
ALTER TABLE `rol`
  ADD PRIMARY KEY (`id_rol`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `empleado`
--
ALTER TABLE `empleado`
  ADD PRIMARY KEY (`id_empleado`),
  ADD UNIQUE KEY `correo` (`correo`),
  ADD KEY `id_rol` (`id_rol`);

--
-- Indices de la tabla `envio`
--
ALTER TABLE `envio`
  ADD PRIMARY KEY (`id_envio`),
  ADD UNIQUE KEY `numero_factura` (`numero_factura`),
  ADD UNIQUE KEY `numero_guia` (`numero_guia`),
  ADD KEY `id_transportadora` (`id_transportadora`);

--
-- Indices de la tabla `factura`
--
ALTER TABLE `factura`
  ADD PRIMARY KEY (`numero_factura`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_empleado` (`id_empleado`);

--
-- Indices de la tabla `metodo_pago`
--
ALTER TABLE `metodo_pago`
  ADD PRIMARY KEY (`id_metodo`);

--
-- Indices de la tabla `producto`
--
ALTER TABLE `producto`
  ADD PRIMARY KEY (`id_producto`),
  -- Esta es la restriccion que impide productos duplicados: dos filas no
  -- pueden compartir el mismo codigo, lo intente la aplicacion, phpMyAdmin
  -- o un script suelto.
  ADD UNIQUE KEY `uq_producto_codigo` (`codigo`),
  ADD KEY `id_categoria` (`id_categoria`),
  ADD KEY `id_proveedor` (`id_proveedor`),
  -- Indice de texto completo para el buscador del catalogo.
  -- El buscador usaba `nombre LIKE '%texto%'`, y un LIKE que empieza por
  -- comodin no puede aprovechar ningun indice: obliga a recorrer la tabla
  -- entera en cada busqueda. Con FULLTEXT, MySQL si usa el indice
  -- (ver ProductoService._aplicar_busqueda, que emplea MATCH ... AGAINST).
  ADD FULLTEXT KEY `ft_producto_busqueda` (`nombre`, `descripcion`);

--
-- Indices de la tabla `imagen_producto`
--
ALTER TABLE `imagen_producto`
  ADD PRIMARY KEY (`id_imagen`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `proveedor`
--
ALTER TABLE `proveedor`
  ADD PRIMARY KEY (`id_proveedor`);

--
-- Indices de la tabla `pse`
--
ALTER TABLE `pse`
  ADD PRIMARY KEY (`id_pse`),
  ADD UNIQUE KEY `numero_factura` (`numero_factura`);

--
-- Indices de la tabla `tarjeta`
--
ALTER TABLE `tarjeta`
  ADD PRIMARY KEY (`id_tarjeta`),
  ADD UNIQUE KEY `numero_factura` (`numero_factura`);

--
-- Indices de la tabla `transferencia_bancaria`
--
ALTER TABLE `transferencia_bancaria`
  ADD PRIMARY KEY (`id_transferencia`),
  ADD UNIQUE KEY `numero_factura` (`numero_factura`);

--
-- Indices de la tabla `transportadora`
--
ALTER TABLE `transportadora`
  ADD PRIMARY KEY (`id_transportadora`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `carrito`
--
ALTER TABLE `carrito`
  MODIFY `id_carrito` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT de la tabla `categoria`
--
ALTER TABLE `categoria`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `codigo_recuperacion`
--
ALTER TABLE `codigo_recuperacion`
  MODIFY `id_codigo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle`
--
ALTER TABLE `detalle`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=273;

--
-- AUTO_INCREMENT de la tabla `empleado`
--
ALTER TABLE `empleado`
  MODIFY `id_empleado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=104;

--
-- AUTO_INCREMENT de la tabla `envio`
--
ALTER TABLE `envio`
  MODIFY `id_envio` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=111;

--
-- AUTO_INCREMENT de la tabla `factura`
--
ALTER TABLE `factura`
  MODIFY `numero_factura` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=121;

--
-- AUTO_INCREMENT de la tabla `imagen_producto`
--
ALTER TABLE `imagen_producto`
  MODIFY `id_imagen` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=111;

--
-- AUTO_INCREMENT de la tabla `metodo_pago`
--
ALTER TABLE `metodo_pago`
  MODIFY `id_metodo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `producto`
--
-- El id lo asigna el motor, no la aplicacion (ver la nota de sprint junto a
-- la definicion de la tabla). Su identificador de negocio sigue siendo
-- `codigo`, protegido por el UNIQUE `uq_producto_codigo`.
--
ALTER TABLE `producto`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=86;

--
-- AUTO_INCREMENT de la tabla `rol`
--
ALTER TABLE `rol`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `proveedor`
--
ALTER TABLE `proveedor`
  MODIFY `id_proveedor` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=72;

--
-- AUTO_INCREMENT de la tabla `pse`
--
ALTER TABLE `pse`
  MODIFY `id_pse` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de la tabla `tarjeta`
--
ALTER TABLE `tarjeta`
  MODIFY `id_tarjeta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- AUTO_INCREMENT de la tabla `transferencia_bancaria`
--
ALTER TABLE `transferencia_bancaria`
  MODIFY `id_transferencia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de la tabla `transportadora`
--
ALTER TABLE `transportadora`
  MODIFY `id_transportadora` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=61;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `carrito`
--
ALTER TABLE `carrito`
  ADD CONSTRAINT `carrito_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `cliente` (`id_usuario`);

--
-- Filtros para la tabla `carrito_producto`
--
ALTER TABLE `carrito_producto`
  ADD CONSTRAINT `carrito_producto_ibfk_1` FOREIGN KEY (`id_carrito`) REFERENCES `carrito` (`id_carrito`),
  ADD CONSTRAINT `carrito_producto_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`);

--
-- Filtros para la tabla `codigo_recuperacion`
--
ALTER TABLE `codigo_recuperacion`
  ADD CONSTRAINT `codigo_recuperacion_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `cliente` (`id_usuario`) ON DELETE CASCADE;

--
-- Filtros para la tabla `detalle`
--
ALTER TABLE `detalle`
  ADD CONSTRAINT `detalle_ibfk_1` FOREIGN KEY (`numero_factura`) REFERENCES `factura` (`numero_factura`),
  ADD CONSTRAINT `detalle_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`);

--
-- Filtros para la tabla `empleado`
--
ALTER TABLE `empleado`
  ADD CONSTRAINT `empleado_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);

--
-- Filtros para la tabla `envio`
--
ALTER TABLE `envio`
  ADD CONSTRAINT `envio_ibfk_1` FOREIGN KEY (`numero_factura`) REFERENCES `factura` (`numero_factura`),
  ADD CONSTRAINT `envio_ibfk_2` FOREIGN KEY (`id_transportadora`) REFERENCES `transportadora` (`id_transportadora`);

--
-- Filtros para la tabla `factura`
--
ALTER TABLE `factura`
  ADD CONSTRAINT `factura_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `cliente` (`id_usuario`),
  ADD CONSTRAINT `factura_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`);

--
-- Filtros para la tabla `producto`
--
ALTER TABLE `producto`
  ADD CONSTRAINT `producto_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `producto_ibfk_2` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`);

--
-- Filtros para la tabla `imagen_producto`
--
ALTER TABLE `imagen_producto`
  ADD CONSTRAINT `imagen_producto_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`);

--
-- Filtros para la tabla `pse`
--
ALTER TABLE `pse`
  ADD CONSTRAINT `pse_ibfk_1` FOREIGN KEY (`numero_factura`) REFERENCES `factura` (`numero_factura`) ON DELETE CASCADE;

--
-- Filtros para la tabla `tarjeta`
--
ALTER TABLE `tarjeta`
  ADD CONSTRAINT `tarjeta_ibfk_1` FOREIGN KEY (`numero_factura`) REFERENCES `factura` (`numero_factura`) ON DELETE CASCADE;

--
-- Filtros para la tabla `transferencia_bancaria`
--
ALTER TABLE `transferencia_bancaria`
  ADD CONSTRAINT `transferencia_bancaria_ibfk_1` FOREIGN KEY (`numero_factura`) REFERENCES `factura` (`numero_factura`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;