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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `carrito`
--

INSERT INTO `carrito` (`id_carrito`, `id_usuario`) VALUES
(33, '10000000003'),
(34, '10000000003'),
(35, '10000000003'),
(6, '10000000005'),
(19, '10000000007'),
(17, '10000000008'),
(18, '10000000009'),
(36, '10000000009'),
(47, '10000000009'),
(27, '10000000010'),
(43, '10000000010'),
(2, '10000000013'),
(28, '10000000013'),
(12, '10000000018'),
(5, '10000000019'),
(48, '10000000021'),
(23, '10000000022'),
(38, '10000000022'),
(3, '10000000024'),
(21, '10000000024'),
(25, '10000000024'),
(7, '10000000025'),
(20, '10000000026'),
(31, '10000000026'),
(9, '10000000029'),
(42, '10000000030'),
(40, '10000000031'),
(8, '10000000033'),
(30, '10000000033'),
(32, '10000000033'),
(46, '10000000033'),
(41, '10000000034'),
(1, '10000000036'),
(4, '10000000036'),
(11, '10000000036'),
(24, '10000000036'),
(29, '10000000039'),
(44, '10000000039'),
(14, '10000000040'),
(16, '10000000040'),
(50, '10000000040'),
(15, '10000000044'),
(37, '10000000046'),
(10, '10000000049'),
(26, '10000000049'),
(22, '10000000051'),
(39, '10000000052'),
(13, '10000000053'),
(45, '10000000058'),
(49, '10000000060');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrito_producto`
--

CREATE TABLE `carrito_producto` (
  `id_carrito` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `carrito_producto`
--

INSERT INTO `carrito_producto` (`id_carrito`, `id_producto`, `cantidad`) VALUES
(1, 1, 3),
(2, 2, 2),
(3, 3, 4),
(4, 4, 3),
(5, 5, 3),
(6, 6, 4),
(7, 7, 3),
(8, 8, 4),
(9, 9, 1),
(10, 10, 3),
(11, 11, 3),
(12, 12, 1),
(13, 13, 4),
(14, 14, 3),
(15, 15, 1),
(16, 16, 4),
(17, 17, 3),
(18, 18, 2),
(19, 19, 1),
(20, 20, 4),
(21, 21, 2),
(22, 22, 4),
(23, 23, 2),
(24, 24, 2),
(25, 25, 1),
(26, 26, 1),
(27, 27, 2),
(28, 28, 1),
(29, 29, 4),
(30, 30, 3),
(31, 31, 4),
(32, 32, 2),
(33, 33, 4),
(34, 34, 2),
(35, 35, 4),
(36, 36, 4),
(37, 37, 1),
(38, 38, 2),
(39, 39, 2),
(40, 40, 3),
(41, 41, 4),
(42, 42, 4),
(43, 43, 3),
(44, 44, 2),
(45, 45, 4),
(46, 46, 3),
(47, 47, 3),
(48, 48, 3),
(49, 49, 4),
(50, 50, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categoria`
--

CREATE TABLE `categoria` (
  `id_categoria` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `categoria`
--

INSERT INTO `categoria` (`id_categoria`, `nombre`) VALUES
(1, 'Perros'),
(2, 'Gatos'),
(3, 'Otros');

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `cliente`
--

INSERT INTO `cliente` (`id_usuario`, `nombre`, `apellido`, `correo`, `contrasena`, `telefono`, `direccion`) VALUES
('10000000001', 'Juan', 'Pérez', 'juan.perez@gmail.com', '123456', '3001234567', 'Calle 10 #20-30 Bogotá'),
('10000000002', 'María', 'Gómez', 'maria.gomez@gmail.com', '123456', '3012345678', 'Carrera 15 #45-20 Medellín'),
('10000000003', 'Carlos', 'Rodríguez', 'carlos.rodriguez@gmail.com', '123456', '3023456789', 'Calle 50 #12-15 Cali'),
('10000000004', 'Laura', 'Martínez', 'laura.martinez@gmail.com', '123456', '3034567890', 'Carrera 30 #18-25 Barranquilla'),
('10000000005', 'Andrés', 'López', 'andres.lopez@gmail.com', '123456', '3045678901', 'Calle 80 #25-10 Cartagena'),
('10000000006', 'Sofía', 'Hernández', 'sofia.hernandez@gmail.com', '123456', '3056789012', 'Carrera 7 #60-40 Bogotá'),
('10000000007', 'Diego', 'Torres', 'diego.torres@gmail.com', '123456', '3067890123', 'Calle 22 #14-50 Pereira'),
('10000000008', 'Valentina', 'Ramírez', 'valentina.ramirez@gmail.com', '123456', '3078901234', 'Carrera 12 #33-18 Manizales'),
('10000000009', 'Sebastián', 'Castro', 'sebastian.castro@gmail.com', '123456', '3089012345', 'Calle 35 #21-60 Bucaramanga'),
('10000000010', 'Camila', 'Moreno', 'camila.moreno@gmail.com', '123456', '3090123456', 'Carrera 50 #10-25 Bogotá'),
('10000000011', 'Miguel', 'Peña', 'miguel.pena11@gmail.com', '123456', '3134744854', 'Carrera 95 #14-87 Valledupar'),
('10000000012', 'Beatriz', 'Martínez', 'beatriz.martinez12@gmail.com', '123456', '3014668136', 'Carrera 65 #78-4 Valledupar'),
('10000000013', 'Karen', 'Nieto', 'karen.nieto13@gmail.com', '123456', '3264698379', 'Diagonal 76 #36-1 Bucaramanga'),
('10000000014', 'Rodrigo', 'Ortiz', 'rodrigo.ortiz14@gmail.com', '123456', '3036647119', 'Calle 12 #49-13 Villavicencio'),
('10000000015', 'Vicente', 'Morales', 'vicente.morales15@gmail.com', '123456', '3079996414', 'Calle 119 #49-11 Valledupar'),
('10000000016', 'Karen', 'Muñoz', 'karen.munoz16@gmail.com', '123456', '3194226067', 'Calle 6 #85-30 Ibagué'),
('10000000017', 'Joaquín', 'Reyes', 'joaquin.reyes17@gmail.com', '123456', '3065663623', 'Diagonal 82 #47-21 Villavicencio'),
('10000000018', 'Liliana', 'Ortiz', 'liliana.ortiz18@gmail.com', '123456', '3213871230', 'Transversal 94 #32-21 Popayán'),
('10000000019', 'Ximena', 'Correa', 'ximena.correa19@gmail.com', '123456', '3284684531', 'Avenida 108 #99-8 Manizales'),
('10000000020', 'Hugo', 'Ramos', 'hugo.ramos20@gmail.com', '123456', '3142110460', 'Carrera 117 #73-92 Cúcuta'),
('10000000021', 'Elena', 'Romero', 'elena.romero21@gmail.com', '123456', '3273396987', 'Avenida 18 #32-96 Valledupar'),
('10000000022', 'Fabián', 'Castro', 'fabian.castro22@gmail.com', '123456', '3197700828', 'Avenida 29 #18-66 Montería'),
('10000000023', 'Paula', 'Sánchez', 'paula.sanchez23@gmail.com', '123456', '3028082668', 'Transversal 9 #50-49 Pasto'),
('10000000024', 'Pablo', 'Morales', 'pablo.morales24@gmail.com', '123456', '3202921859', 'Transversal 97 #35-99 Cúcuta'),
('10000000025', 'Beatriz', 'Flores', 'beatriz.flores25@gmail.com', '123456', '3105418934', 'Transversal 98 #23-65 Barranquilla'),
('10000000026', 'Néstor', 'Correa', 'nestor.correa26@gmail.com', '123456', '3294337174', 'Carrera 48 #98-21 Valledupar'),
('10000000027', 'Mario', 'Vásquez', 'mario.vasquez27@gmail.com', '123456', '3096438436', 'Diagonal 3 #15-47 Ibagué'),
('10000000028', 'Diana', 'Delgado', 'diana.delgado28@gmail.com', '123456', '3019153566', 'Calle 98 #69-99 Cartagena'),
('10000000029', 'Elena', 'Silva', 'elena.silva29@gmail.com', '123456', '3049852897', 'Transversal 55 #28-70 Pereira'),
('10000000030', 'Gustavo', 'Bermúdez', 'gustavo.bermudez30@gmail.com', '123456', '3258350099', 'Transversal 58 #16-32 Manizales'),
('10000000031', 'Ana', 'Castro', 'ana.castro31@gmail.com', '123456', '3234694634', 'Calle 10 #91-81 Medellín'),
('10000000032', 'Tatiana', 'Martínez', 'tatiana.martinez32@gmail.com', '123456', '3119626108', 'Carrera 36 #86-63 Pereira'),
('10000000033', 'Fabián', 'Delgado', 'fabian.delgado33@gmail.com', '123456', '3275076817', 'Diagonal 104 #53-25 Barranquilla'),
('10000000034', 'Beatriz', 'Castillo', 'beatriz.castillo34@gmail.com', '123456', '3168835373', 'Calle 87 #84-83 Barranquilla'),
('10000000035', 'Nubia', 'Vargas', 'nubia.vargas35@gmail.com', '123456', '3034214348', 'Carrera 69 #58-18 Armenia'),
('10000000036', 'Claudia', 'Cruz', 'claudia.cruz36@gmail.com', '123456', '3072642635', 'Calle 84 #70-2 Cali'),
('10000000037', 'Joaquín', 'Cruz', 'joaquin.cruz37@gmail.com', '123456', '3069147706', 'Diagonal 28 #52-8 Bucaramanga'),
('10000000038', 'Gloria', 'Morales', 'gloria.morales38@gmail.com', '123456', '3148096887', 'Transversal 85 #92-63 Cartagena'),
('10000000039', 'Patricia', 'López', 'patricia.lopez39@gmail.com', '123456', '3282022698', 'Avenida 8 #7-75 Montería'),
('10000000040', 'Joaquín', 'Vásquez', 'joaquin.vasquez40@gmail.com', '123456', '3009519948', 'Calle 109 #24-9 Pasto'),
('10000000041', 'Sandra', 'Cruz', 'sandra.cruz41@gmail.com', '123456', '3115130808', 'Transversal 77 #6-80 Cali'),
('10000000042', 'Ingrid', 'Delgado', 'ingrid.delgado42@gmail.com', '123456', '3255374922', 'Carrera 86 #92-41 Manizales'),
('10000000043', 'Carolina', 'Bermúdez', 'carolina.bermudez43@gmail.com', '123456', '3248670955', 'Avenida 119 #97-10 Bogotá'),
('10000000044', 'Ingrid', 'Pérez', 'ingrid.perez44@gmail.com', '123456', '3084576135', 'Transversal 34 #17-45 Cali'),
('10000000045', 'Felipe', 'Gutiérrez', 'felipe.gutierrez45@gmail.com', '123456', '3076075395', 'Transversal 104 #84-68 Bogotá'),
('10000000046', 'Raúl', 'Chávez', 'raul.chavez46@gmail.com', '123456', '3213253031', 'Avenida 15 #14-96 Valledupar'),
('10000000047', 'Adriana', 'Ospina', 'adriana.ospina47@gmail.com', '123456', '3054415796', 'Avenida 65 #63-33 Medellín'),
('10000000048', 'Beatriz', 'Ortiz', 'beatriz.ortiz48@gmail.com', '123456', '3006596150', 'Carrera 82 #34-21 Popayán'),
('10000000049', 'Hernán', 'Silva', 'hernan.silva49@gmail.com', '123456', '3012262382', 'Carrera 70 #5-48 Tunja'),
('10000000050', 'Hernán', 'Ramírez', 'hernan.ramirez50@gmail.com', '123456', '3047117837', 'Calle 116 #46-27 Manizales'),
('10000000051', 'Felipe', 'Duarte', 'felipe.duarte51@gmail.com', '123456', '3263592974', 'Carrera 111 #21-23 Armenia'),
('10000000052', 'Nubia', 'Vargas', 'nubia.vargas52@gmail.com', '123456', '3135476257', 'Carrera 101 #90-14 Neiva'),
('10000000053', 'Joaquín', 'Rojas', 'joaquin.rojas53@gmail.com', '123456', '3038722606', 'Avenida 40 #30-29 Bogotá'),
('10000000054', 'Gustavo', 'Vargas', 'gustavo.vargas54@gmail.com', '123456', '3115682940', 'Avenida 83 #66-52 Valledupar'),
('10000000055', 'Ana', 'Sánchez', 'ana.sanchez55@gmail.com', '123456', '3125453786', 'Calle 14 #77-56 Villavicencio'),
('10000000056', 'Rodrigo', 'Medina', 'rodrigo.medina56@gmail.com', '123456', '3282940214', 'Diagonal 116 #74-25 Santa Marta'),
('10000000057', 'Beatriz', 'García', 'beatriz.garcia57@gmail.com', '123456', '3284305700', 'Avenida 56 #9-86 Cúcuta'),
('10000000058', 'Danilo', 'Sánchez', 'danilo.sanchez58@gmail.com', '123456', '3249508103', 'Avenida 86 #53-42 Neiva'),
('10000000059', 'Raúl', 'Ramírez', 'raul.ramirez59@gmail.com', '123456', '3067361002', 'Carrera 79 #73-39 Neiva'),
('10000000060', 'Miguel', 'Chávez', 'miguel.chavez60@gmail.com', '123456', '3138212326', 'Transversal 78 #84-42 Popayán'),
('10000000061', 'Andrés', 'Zapata', 'andres.zapata61@gmail.com', '123456', '3434744854', 'Carrera 27 #87-70 Cali'),
('10000000062', 'Bibiana', 'Acosta', 'bibiana.acosta62@gmail.com', '123456', '3134903402', 'Transversal 7 #72-26 Santa Marta'),
('10000000063', 'Helena', 'Pardo', 'helena.pardo63@gmail.com', '123456', '3941109031', 'Carrera 109 #44-36 Cartagena'),
('10000000064', 'Zacarías', 'Lozano', 'zacarias.lozano64@gmail.com', '123456', '3117374122', 'Calle 92 #45-78 Manizales'),
('10000000065', 'Yesid', 'Pardo', 'yesid.pardo65@gmail.com', '123456', '3817350753', 'Calle 76 #81-80 Neiva'),
('10000000066', 'Xavier', 'Cifuentes', 'xavier.cifuentes66@gmail.com', '123456', '3035855124', 'Calle 60 #13-49 Manizales'),
('10000000067', 'Úrsula', 'Contreras', 'ursula.contreras67@gmail.com', '123456', '3527210606', 'Avenida 54 #86-35 Cali'),
('10000000068', 'Santiago', 'Zapata', 'santiago.zapata68@gmail.com', '123456', '3328755439', 'Diagonal 70 #82-89 Santa Marta'),
('10000000069', 'Wilson', 'Lozano', 'wilson.lozano69@gmail.com', '123456', '3031538552', 'Avenida 103 #35-9 Bucaramanga'),
('10000000070', 'Gabriela', 'Vargas', 'gabriela.vargas70@gmail.com', '123456', '3768698256', 'Carrera 68 #18-32 Santa Marta'),
('10000000071', 'Yolanda', 'Tovar', 'yolanda.tovar71@gmail.com', '123456', '3697700828', 'Avenida 57 #18-66 Montería'),
('10000000072', 'Zacarías', 'Bermúdez', 'zacarias.bermudez72@gmail.com', '123456', '3123684052', 'Diagonal 17 #50-49 Sincelejo'),
('10000000073', 'Quiterina', 'Ibarra', 'quiterina.ibarra73@gmail.com', '123456', '3802921859', 'Transversal 69 #99-83 Villavicencio'),
('10000000074', 'Kevin', 'Ospina', 'kevin.ospina74@gmail.com', '123456', '3271054447', 'Avenida 129 #98-23 Tunja'),
('10000000075', 'Cristian', 'Vargas', 'cristian.vargas75@gmail.com', '123456', '3484337174', 'Carrera 96 #98-21 Santa Marta'),
('10000000076', 'Ubaldo', 'Lozano', 'ubaldo.lozano76@gmail.com', '123456', '3702876828', 'Avenida 79 #31-8 Pereira'),
('10000000077', 'Diego', 'Zapata', 'diego.zapata77@gmail.com', '123456', '3719937326', 'Carrera 33 #85-61 Santa Marta'),
('10000000078', 'Jorge', 'Restrepo', 'jorge.restrepo78@gmail.com', '123456', '3964553384', 'Transversal 52 #92-40 Pasto'),
('10000000079', 'Olga', 'España', 'olga.españa79@gmail.com', '123456', '3873030113', 'Carrera 58 #9-44 Bogotá'),
('10000000080', 'Tomás', 'Herrera', 'tomas.herrera80@gmail.com', '123456', '3011987737', 'Carrera 18 #5-43 Cali'),
('10000000081', 'Jorge', 'Wilches', 'jorge.wilches81@gmail.com', '123456', '3733219824', 'Transversal 122 #32-61 Armenia'),
('10000000082', 'Esteban', 'Duarte', 'esteban.duarte82@gmail.com', '123456', '3658106470', 'Diagonal 120 #94-7 Barranquilla'),
('10000000083', 'Nicolás', 'Zapata', 'nicolas.zapata83@gmail.com', '123456', '3515171761', 'Carrera 49 #69-58 Cartagena'),
('10000000084', 'Fernanda', 'Ibarra', 'fernanda.ibarra84@gmail.com', '123456', '3732264748', 'Diagonal 26 #7-84 Santa Marta'),
('10000000085', 'Diego', 'Figueroa', 'diego.figueroa85@gmail.com', '123456', '3327818496', 'Diagonal 124 #28-52 Medellín'),
('10000000086', 'Nicolás', 'Acosta', 'nicolas.acosta86@gmail.com', '123456', '3648633773', 'Avenida 109 #90-72 Montería'),
('10000000087', 'Hernán', 'Jiménez', 'hernan.jimenez87@gmail.com', '123456', '3302022698', 'Avenida 15 #7-75 Montería'),
('10000000088', 'Camilo', 'Restrepo', 'camilo.restrepo88@gmail.com', '123456', '3122149597', 'Transversal 18 #87-31 Pasto'),
('10000000089', 'David', 'Tovar', 'david.tovar89@gmail.com', '123456', '3391666754', 'Transversal 21 #54-85 Valledupar'),
('10000000090', 'Erika', 'Ibarra', 'erika.ibarra90@gmail.com', '123456', '3355004485', 'Avenida 102 #17-86 Ibagué'),
('10000000091', 'Karina', 'Figueroa', 'karina.figueroa91@gmail.com', '123456', '3108688755', 'Transversal 26 #10-69 Bucaramanga'),
('10000000092', 'Estefanía', 'Figueroa', 'estefania.figueroa92@gmail.com', '123456', '3515098412', 'Avenida 73 #21-57 Santa Marta'),
('10000000093', 'Tatiana', 'Buitrago', 'tatiana.buitrago93@gmail.com', '123456', '3806022741', 'Calle 35 #34-15 Barranquilla'),
('10000000094', 'Jorge', 'Jiménez', 'jorge.jimenez94@gmail.com', '123456', '3936752576', 'Carrera 68 #65-63 Manizales'),
('10000000095', 'Diego', 'Vargas', 'diego.vargas95@gmail.com', '123456', '3641739653', 'Calle 86 #99-17 Manizales'),
('10000000096', 'Yesid', 'Pardo', 'yesid.pardo96@gmail.com', '123456', '3861162230', 'Calle 20 #89-20 Santa Marta'),
('10000000097', 'Bruno', 'Mendoza', 'bruno.mendoza97@gmail.com', '123456', '3983484601', 'Diagonal 33 #6-40 Neiva'),
('10000000098', 'David', 'Mendoza', 'david.mendoza98@gmail.com', '123456', '3332724590', 'Avenida 105 #80-20 Pereira'),
('10000000099', 'Alejandro', 'Buitrago', 'alejandro.buitrago99@gmail.com', '123456', '3261415846', 'Carrera 86 #53-86 Pereira'),
('10000000100', 'Fernanda', 'Buitrago', 'fernanda.buitrago100@gmail.com', '123456', '3161649691', 'Diagonal 57 #26-59 Neiva'),
('10000000101', 'Beatriz', 'Buitrago', 'beatriz.buitrago101@gmail.com', '123456', '3331397023', 'Carrera 103 #43-36 Cali'),
('10000000102', 'Lucía', 'Vargas', 'lucia.vargas102@gmail.com', '123456', '3869996207', 'Avenida 8 #15-34 Cúcuta'),
('10000000103', 'Bibiana', 'Duarte', 'bibiana.duarte103@gmail.com', '123456', '3966799667', 'Avenida 112 #78-66 Barranquilla'),
('10000000104', 'Dolores', 'Tovar', 'dolores.tovar104@gmail.com', '123456', '3341744682', 'Diagonal 1 #67-69 Bucaramanga'),
('10000000105', 'Natalia', 'Cifuentes', 'natalia.cifuentes105@gmail.com', '123456', '3596266630', 'Calle 77 #65-40 Armenia'),
('10000000106', 'Mónica', 'Yepes', 'monica.yepes106@gmail.com', '123456', '3483135534', 'Carrera 108 #86-49 Cúcuta'),
('10000000107', 'Mónica', 'Salazar', 'monica.salazar107@gmail.com', '123456', '3045813613', 'Carrera 111 #75-78 Villavicencio'),
('10000000108', 'Olga', 'Pardo', 'olga.pardo108@gmail.com', '123456', '3388938746', 'Carrera 22 #37-66 Sincelejo'),
('10000000109', 'Carolina', 'Contreras', 'carolina.contreras109@gmail.com', '123456', '3344768844', 'Carrera 38 #4-6 Pereira'),
('10000000110', 'Tatiana', 'Delgado', 'tatiana.delgado110@gmail.com', '123456', '3177953166', 'Transversal 50 #92-90 Pasto');

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `detalle`
--

INSERT INTO `detalle` (`id_detalle`, `numero_factura`, `id_producto`, `cantidad`, `precio_unitario`, `subtotal_producto`) VALUES
(89, 1, 1, 1, 85000.00, 85000.00),
(90, 1, 3, 1, 25000.00, 25000.00),
(91, 2, 11, 1, 75000.00, 75000.00),
(92, 3, 7, 1, 120000.00, 120000.00),
(93, 3, 5, 1, 18000.00, 18000.00),
(94, 3, 6, 1, 22000.00, 22000.00),
(95, 4, 12, 1, 65000.00, 65000.00),
(96, 5, 21, 1, 120000.00, 120000.00),
(97, 5, 23, 1, 60000.00, 60000.00),
(98, 5, 25, 1, 50000.00, 50000.00),
(99, 6, 13, 2, 30000.00, 60000.00),
(100, 6, 15, 1, 50000.00, 50000.00),
(101, 7, 2, 1, 70000.00, 70000.00),
(102, 7, 10, 1, 20000.00, 20000.00),
(103, 7, 27, 1, 35000.00, 35000.00),
(104, 8, 16, 2, 12000.00, 24000.00),
(105, 8, 19, 1, 95000.00, 95000.00),
(106, 9, 8, 1, 70000.00, 70000.00),
(107, 9, 22, 1, 80000.00, 80000.00),
(108, 9, 26, 1, 15000.00, 15000.00),
(109, 10, 4, 1, 35000.00, 35000.00),
(110, 10, 14, 1, 45000.00, 45000.00),
(111, 21, 31, 3, 43000.00, 129000.00),
(112, 22, 32, 2, 43000.00, 86000.00),
(113, 23, 33, 3, 44000.00, 132000.00),
(114, 24, 34, 2, 209000.00, 418000.00),
(115, 25, 35, 2, 53000.00, 106000.00),
(116, 26, 36, 2, 35000.00, 70000.00),
(117, 27, 37, 3, 163000.00, 489000.00),
(118, 28, 38, 2, 104000.00, 208000.00),
(119, 29, 39, 1, 51000.00, 51000.00),
(120, 30, 40, 3, 110000.00, 330000.00),
(121, 31, 41, 2, 212000.00, 424000.00),
(122, 32, 42, 3, 204000.00, 612000.00),
(123, 33, 43, 1, 93000.00, 93000.00),
(124, 34, 44, 2, 99000.00, 198000.00),
(125, 35, 45, 1, 46000.00, 46000.00),
(126, 36, 46, 1, 149000.00, 149000.00),
(127, 37, 47, 1, 59000.00, 59000.00),
(128, 38, 48, 2, 143000.00, 286000.00),
(129, 39, 49, 2, 47000.00, 94000.00),
(130, 40, 50, 1, 162000.00, 162000.00),
(131, 41, 51, 3, 49000.00, 147000.00),
(132, 42, 52, 1, 91000.00, 91000.00),
(133, 43, 53, 2, 77000.00, 154000.00),
(134, 44, 54, 3, 163000.00, 489000.00),
(135, 45, 55, 3, 179000.00, 537000.00),
(136, 46, 56, 3, 192000.00, 576000.00),
(137, 47, 57, 1, 162000.00, 162000.00),
(138, 48, 58, 3, 175000.00, 525000.00),
(139, 49, 59, 2, 197000.00, 394000.00),
(140, 50, 60, 2, 27000.00, 54000.00),
(141, 51, 61, 2, 89000.00, 178000.00),
(142, 52, 62, 2, 215000.00, 430000.00),
(143, 53, 63, 2, 106000.00, 212000.00),
(144, 54, 64, 2, 21000.00, 42000.00),
(145, 55, 65, 2, 56000.00, 112000.00),
(146, 56, 66, 2, 188000.00, 376000.00),
(147, 57, 67, 3, 37000.00, 111000.00),
(148, 58, 68, 3, 209000.00, 627000.00),
(149, 59, 69, 1, 27000.00, 27000.00),
(150, 60, 70, 1, 211000.00, 211000.00),
(151, 61, 71, 2, 75000.00, 150000.00),
(152, 62, 72, 2, 127000.00, 254000.00),
(153, 63, 73, 1, 107000.00, 107000.00),
(154, 64, 74, 2, 114000.00, 228000.00),
(155, 65, 75, 1, 204000.00, 204000.00),
(156, 66, 76, 1, 218000.00, 218000.00),
(157, 67, 77, 3, 172000.00, 516000.00),
(158, 68, 78, 3, 33000.00, 99000.00),
(159, 69, 79, 1, 60000.00, 60000.00),
(160, 70, 80, 2, 178000.00, 356000.00),
(161, 71, 75, 2, 25000.00, 50000.00),
(162, 71, 70, 2, 25000.00, 50000.00),
(164, 72, 38, 1, 120000.00, 120000.00),
(166, 73, 35, 2, 60000.00, 120000.00),
(167, 73, 18, 2, 60000.00, 120000.00),
(168, 73, 71, 3, 120000.00, 360000.00),
(169, 74, 1, 3, 25000.00, 75000.00),
(170, 74, 73, 2, 25000.00, 50000.00),
(172, 75, 39, 2, 25000.00, 50000.00),
(176, 77, 62, 2, 25000.00, 50000.00),
(178, 77, 60, 2, 85000.00, 170000.00),
(182, 79, 10, 3, 85000.00, 255000.00),
(183, 79, 33, 3, 60000.00, 180000.00),
(184, 80, 26, 1, 60000.00, 60000.00),
(186, 81, 4, 2, 120000.00, 240000.00),
(187, 81, 37, 3, 85000.00, 255000.00),
(188, 82, 20, 2, 25000.00, 50000.00),
(192, 84, 82, 3, 210000.00, 630000.00),
(193, 85, 10, 1, 85000.00, 85000.00),
(194, 85, 18, 3, 60000.00, 180000.00),
(195, 86, 74, 2, 45000.00, 90000.00),
(196, 86, 59, 1, 150000.00, 150000.00),
(197, 86, 24, 3, 150000.00, 450000.00),
(198, 87, 26, 3, 60000.00, 180000.00),
(200, 87, 43, 1, 85000.00, 85000.00),
(201, 88, 84, 1, 95000.00, 95000.00),
(205, 91, 47, 1, 60000.00, 60000.00),
(206, 91, 44, 3, 25000.00, 75000.00),
(207, 91, 45, 2, 45000.00, 90000.00),
(208, 92, 62, 1, 25000.00, 25000.00),
(210, 92, 37, 3, 85000.00, 255000.00),
(212, 93, 66, 1, 150000.00, 150000.00),
(213, 94, 74, 1, 45000.00, 45000.00),
(214, 94, 41, 2, 120000.00, 240000.00),
(215, 95, 77, 3, 25000.00, 75000.00),
(217, 96, 78, 2, 150000.00, 300000.00),
(218, 96, 51, 2, 85000.00, 170000.00),
(219, 97, 61, 2, 25000.00, 50000.00),
(221, 98, 76, 2, 85000.00, 170000.00),
(222, 98, 6, 2, 85000.00, 170000.00),
(223, 99, 13, 3, 25000.00, 75000.00),
(225, 100, 74, 2, 45000.00, 90000.00),
(226, 100, 59, 1, 150000.00, 150000.00),
(227, 101, 49, 3, 85000.00, 255000.00),
(228, 101, 65, 1, 45000.00, 45000.00),
(229, 101, 36, 3, 25000.00, 75000.00),
(230, 102, 11, 1, 150000.00, 150000.00),
(231, 102, 80, 3, 85000.00, 255000.00),
(233, 103, 34, 2, 60000.00, 120000.00),
(234, 103, 24, 3, 150000.00, 450000.00),
(235, 103, 76, 2, 85000.00, 170000.00),
(236, 104, 52, 1, 25000.00, 25000.00),
(239, 105, 70, 2, 25000.00, 50000.00),
(241, 106, 30, 1, 25000.00, 25000.00),
(242, 107, 58, 3, 85000.00, 255000.00),
(245, 108, 24, 2, 150000.00, 300000.00),
(246, 109, 32, 3, 25000.00, 75000.00),
(252, 112, 84, 3, 95000.00, 285000.00),
(253, 112, 57, 2, 60000.00, 120000.00),
(254, 112, 17, 3, 60000.00, 180000.00),
(256, 113, 30, 1, 25000.00, 25000.00),
(257, 114, 78, 2, 150000.00, 300000.00),
(258, 115, 25, 1, 85000.00, 85000.00),
(259, 116, 35, 2, 60000.00, 120000.00),
(263, 117, 40, 1, 150000.00, 150000.00),
(266, 118, 72, 2, 85000.00, 170000.00),
(267, 118, 9, 1, 120000.00, 120000.00),
(269, 119, 61, 1, 25000.00, 25000.00),
(272, 120, 16, 1, 85000.00, 85000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleado`
--

CREATE TABLE `empleado` (
  `id_empleado` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `empleado`
--

INSERT INTO `empleado` (`id_empleado`, `nombre`, `apellido`, `correo`, `contrasena`, `telefono`) VALUES
(1, 'Carlos', 'Ramírez', 'carlos.ramirez@bandp.com', '123456', '3101111111'),
(2, 'Ana', 'Martínez', 'ana.martinez@bandp.com', '123456', '3112222222'),
(3, 'Luis', 'Gómez', 'luis.gomez@bandp.com', '123456', '3123333333'),
(4, 'Liliana', 'Díaz', 'liliana.diaz4@bandp.com', '123456', '3188938746'),
(5, 'Hugo', 'Peña', 'hugo.pena5@bandp.com', '123456', '3122422633'),
(6, 'Liliana', 'Correa', 'liliana.correa6@bandp.com', '123456', '3196623525'),
(7, 'Olga', 'Cruz', 'olga.cruz7@bandp.com', '123456', '3144768844'),
(8, 'Álvaro', 'Rodríguez', 'alvaro.rodriguez8@bandp.com', '123456', '3105107776'),
(9, 'Vicente', 'Duarte', 'vicente.duarte9@bandp.com', '123456', '3118640615'),
(10, 'Karen', 'Delgado', 'karen.delgado10@bandp.com', '123456', '3137442089'),
(11, 'Diana', 'Torres', 'diana.torres11@bandp.com', '123456', '3102788238'),
(12, 'Esteban', 'Rivera', 'esteban.rivera12@bandp.com', '123456', '3188793853'),
(13, 'Diana', 'Sánchez', 'diana.sanchez13@bandp.com', '123456', '3173237058'),
(14, 'Danilo', 'Vásquez', 'danilo.vasquez14@bandp.com', '123456', '3186323376'),
(15, 'Leonardo', 'Aguilar', 'leonardo.aguilar15@bandp.com', '123456', '3199468772'),
(16, 'Ximena', 'Silva', 'ximena.silva16@bandp.com', '123456', '3173670226'),
(17, 'Óscar', 'Aguilar', 'oscar.aguilar17@bandp.com', '123456', '3145147994'),
(18, 'Iván', 'Duarte', 'ivan.duarte18@bandp.com', '123456', '3189130188'),
(19, 'Iván', 'Aguilar', 'ivan.aguilar19@bandp.com', '123456', '3115793722'),
(20, 'Isabel', 'Ramos', 'isabel.ramos20@bandp.com', '123456', '3182351868'),
(21, 'Diana', 'Álvarez', 'diana.alvarez21@bandp.com', '123456', '3124589533'),
(22, 'Beatriz', 'Vargas', 'beatriz.vargas22@bandp.com', '123456', '3188816912'),
(23, 'Patricia', 'Alvarado', 'patricia.alvarado23@bandp.com', '123456', '3161327691'),
(24, 'Gonzalo', 'Delgado', 'gonzalo.delgado24@bandp.com', '123456', '3169002392'),
(25, 'Silvia', 'Chávez', 'silvia.chavez25@bandp.com', '123456', '3168030010'),
(26, 'Fabián', 'Cárdenas', 'fabian.cardenas26@bandp.com', '123456', '3194700025'),
(27, 'Verónica', 'Medina', 'veronica.medina27@bandp.com', '123456', '3171486955'),
(28, 'Liliana', 'Cifuentes', 'liliana.cifuentes28@bandp.com', '123456', '3163768991'),
(29, 'Mario', 'Ramírez', 'mario.ramirez29@bandp.com', '123456', '3199961107'),
(30, 'Gloria', 'Castro', 'gloria.castro30@bandp.com', '123456', '3191454696'),
(31, 'Beatriz', 'Ramírez', 'beatriz.ramirez31@bandp.com', '123456', '3174048907'),
(32, 'Gloria', 'Ramos', 'gloria.ramos32@bandp.com', '123456', '3138628588'),
(33, 'Olga', 'Álvarez', 'olga.alvarez33@bandp.com', '123456', '3148072684'),
(34, 'Daniela', 'Rojas', 'daniela.rojas34@bandp.com', '123456', '3101873851'),
(35, 'Felipe', 'Reyes', 'felipe.reyes35@bandp.com', '123456', '3111675419'),
(36, 'Esteban', 'Gómez', 'esteban.gomez36@bandp.com', '123456', '3103556551'),
(37, 'Elena', 'Bermúdez', 'elena.bermudez37@bandp.com', '123456', '3114656838'),
(38, 'Verónica', 'Duarte', 'veronica.duarte38@bandp.com', '123456', '3153815034'),
(39, 'Fabián', 'Escobar', 'fabian.escobar39@bandp.com', '123456', '3113747534'),
(40, 'Ricardo', 'Castro', 'ricardo.castro40@bandp.com', '123456', '3106233774'),
(41, 'Mario', 'Álvarez', 'mario.alvarez41@bandp.com', '123456', '3164327421'),
(42, 'Mónica', 'Correa', 'monica.correa42@bandp.com', '123456', '3132709620'),
(43, 'Néstor', 'Cifuentes', 'nestor.cifuentes43@bandp.com', '123456', '3193030966'),
(44, 'Tomás', 'Martínez', 'tomas.martinez44@bandp.com', '123456', '3159937982'),
(45, 'Silvia', 'Hernández', 'silvia.hernandez45@bandp.com', '123456', '3186724909'),
(46, 'Beatriz', 'Guerrero', 'beatriz.guerrero46@bandp.com', '123456', '3118273315'),
(47, 'Cristian', 'Salazar', 'cristian.salazar47@bandp.com', '123456', '3128306261'),
(48, 'Fabiola', 'Restrepo', 'fabiola.restrepo48@bandp.com', '123456', '3149111742'),
(49, 'Rosa', 'Rincón', 'rosa.rincon49@bandp.com', '123456', '3195502929'),
(50, 'Diana', 'González', 'diana.gonzalez50@bandp.com', '123456', '3148563202'),
(51, 'Claudia', 'Delgado', 'claudia.delgado51@bandp.com', '123456', '3197358385'),
(52, 'Elena', 'Ramos', 'elena.ramos52@bandp.com', '123456', '3129179730'),
(53, 'Piedad', 'Morales', 'piedad.morales53@bandp.com', '123456', '3155691890'),
(54, 'Mónica', 'Herrera', 'monica.herrera54@bandp.com', '123456', '3258453521'),
(55, 'David', 'Álvarez', 'david.alvarez55@bandp.com', '123456', '3926830795'),
(56, 'Zacarías', 'Ospina', 'zacarias.ospina56@bandp.com', '123456', '3334978881'),
(57, 'Alejandro', 'Yepes', 'alejandro.yepes57@bandp.com', '123456', '3656152900'),
(58, 'Bibiana', 'Salazar', 'bibiana.salazar58@bandp.com', '123456', '3367574609'),
(59, 'Pablo', 'Escobar', 'pablo.escobar59@bandp.com', '123456', '3960514523'),
(60, 'Valeria', 'Restrepo', 'valeria.restrepo60@bandp.com', '123456', '3700141462'),
(61, 'Zoraida', 'España', 'zoraida.españa61@bandp.com', '123456', '3575209597'),
(62, 'Beatriz', 'Figueroa', 'beatriz.figueroa62@bandp.com', '123456', '3688273030'),
(63, 'Dolores', 'Franco', 'dolores.franco63@bandp.com', '123456', '3898493949'),
(64, 'Olga', 'Ibarra', 'olga.ibarra64@bandp.com', '123456', '3907214179'),
(65, 'Bruno', 'Vargas', 'bruno.vargas65@bandp.com', '123456', '3397760792'),
(66, 'Úrsula', 'Herrera', 'ursula.herrera66@bandp.com', '123456', '3394846763'),
(67, 'Carolina', 'Yepes', 'carolina.yepes67@bandp.com', '123456', '3406798268'),
(68, 'Jorge', 'Lozano', 'jorge.lozano68@bandp.com', '123456', '3443285529'),
(69, 'Felipe', 'Escobar', 'felipe.escobar69@bandp.com', '123456', '3348315126'),
(70, 'Ximena', 'Escobar', 'ximena.escobar70@bandp.com', '123456', '3858511779'),
(71, 'Diego', 'Ospina', 'diego.ospina71@bandp.com', '123456', '3537656494'),
(72, 'Renata', 'Pardo', 'renata.pardo72@bandp.com', '123456', '3546434187'),
(73, 'Hernán', 'Contreras', 'hernan.contreras73@bandp.com', '123456', '3551125671'),
(74, 'Dolores', 'Álvarez', 'dolores.alvarez74@bandp.com', '123456', '3727150493'),
(75, 'Cristian', 'España', 'cristian.españa75@bandp.com', '123456', '3922050912'),
(76, 'Paola', 'Acosta', 'paola.acosta76@bandp.com', '123456', '3477698143'),
(77, 'Zoraida', 'Naranjo', 'zoraida.naranjo77@bandp.com', '123456', '3997356828'),
(78, 'Renata', 'Zapata', 'renata.zapata78@bandp.com', '123456', '3888807316'),
(79, 'Quintín', 'Herrera', 'quintin.herrera79@bandp.com', '123456', '3393062061'),
(80, 'Paola', 'Acosta', 'paola.acosta80@bandp.com', '123456', '3517532243'),
(81, 'Valeria', 'Wilches', 'valeria.wilches81@bandp.com', '123456', '3956998797'),
(82, 'Yolanda', 'Franco', 'yolanda.franco82@bandp.com', '123456', '3601856351'),
(83, 'Ubaldo', 'Salazar', 'ubaldo.salazar83@bandp.com', '123456', '3128955006'),
(84, 'Sara', 'Tovar', 'sara.tovar84@bandp.com', '123456', '3811890569'),
(85, 'Diego', 'Vargas', 'diego.vargas85@bandp.com', '123456', '3560219456'),
(86, 'Cristian', 'Pardo', 'cristian.pardo86@bandp.com', '123456', '3295130056'),
(87, 'Jorge', 'Naranjo', 'jorge.naranjo87@bandp.com', '123456', '3451492250'),
(88, 'Pablo', 'Lozano', 'pablo.lozano88@bandp.com', '123456', '3462388455'),
(89, 'Isabela', 'Álvarez', 'isabela.alvarez89@bandp.com', '123456', '3993271900'),
(90, 'Isabela', 'Contreras', 'isabela.contreras90@bandp.com', '123456', '3187946147'),
(91, 'Alejandra', 'Zapata', 'alejandra.zapata91@bandp.com', '123456', '3679196799'),
(92, 'Marco', 'Herrera', 'marco.herrera92@bandp.com', '123456', '3798086909'),
(93, 'Zacarías', 'Vargas', 'zacarias.vargas93@bandp.com', '123456', '3143226844'),
(94, 'Iván', 'Gómez', 'ivan.gomez94@bandp.com', '123456', '3121882877'),
(95, 'Iván', 'Escobar', 'ivan.escobar95@bandp.com', '123456', '3608482316'),
(96, 'Tomás', 'Gómez', 'tomas.gomez96@bandp.com', '123456', '3599326438'),
(97, 'Zoraida', 'Mendoza', 'zoraida.mendoza97@bandp.com', '123456', '3280162221'),
(98, 'Zacarías', 'Contreras', 'zacarias.contreras98@bandp.com', '123456', '3275842194'),
(99, 'Daniela', 'Tovar', 'daniela.tovar99@bandp.com', '123456', '3127571992'),
(100, 'Sara', 'Wilches', 'sara.wilches100@bandp.com', '123456', '3502982778'),
(101, 'Ximena', 'Gómez', 'ximena.gomez101@bandp.com', '123456', '3181600593'),
(102, 'Esteban', 'Yepes', 'esteban.yepes102@bandp.com', '123456', '3929445037'),
(103, 'Carmen', 'Wilches', 'carmen.wilches103@bandp.com', '123456', '3744687060');

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `envio`
--

INSERT INTO `envio` (`id_envio`, `numero_factura`, `id_transportadora`, `numero_guia`, `fecha_envio`, `fecha_entrega_estimada`, `fecha_entrega_real`, `estado`) VALUES
(1, 1, 1, 'SE123456789', '2026-01-06', '2026-01-09', '2026-01-09', 'Entregado'),
(2, 2, 2, 'CO987654321', '2026-01-09', '2026-01-12', '2026-01-12', 'Entregado'),
(3, 3, 3, 'IR456789123', '2026-01-13', '2026-01-16', '2026-01-16', 'Entregado'),
(4, 4, 4, 'DH789456123', '2026-01-16', '2026-01-20', '2026-01-20', 'Entregado'),
(5, 5, 5, 'EN321654987', '2026-01-21', '2026-01-25', '2026-01-25', 'Entregado'),
(6, 6, 6, 'FE654987321', '2026-01-23', '2026-01-27', '2026-01-27', 'Entregado'),
(7, 7, 7, 'TC987321654', '2026-01-26', '2026-01-30', '2026-01-30', 'Entregado'),
(8, 8, 8, 'DP159753486', '2026-01-29', '2026-02-02', '2026-02-02', 'Entregado'),
(9, 9, 9, 'UP753951486', '2026-02-03', '2026-02-07', '2026-02-07', 'Entregado'),
(10, 10, 10, 'MU852963741', '2026-02-06', '2026-02-10', '2026-02-10', 'Entregado'),
(11, 21, 1, 'GU257243284', '2026-02-07', '2026-02-11', '2026-02-11', 'Entregado'),
(12, 22, 2, 'GU286293158', '2026-02-09', '2026-02-13', '2026-02-13', 'Entregado'),
(13, 23, 3, 'GU916274954', '2026-02-11', '2026-02-15', '2026-02-15', 'Entregado'),
(14, 24, 4, 'GU180909963', '2026-02-13', '2026-02-17', NULL, 'En camino'),
(15, 25, 5, 'GU929839316', '2026-02-15', '2026-02-19', '2026-02-19', 'Entregado'),
(16, 26, 6, 'GU598165815', '2026-02-17', '2026-02-21', '2026-02-21', 'Entregado'),
(17, 27, 7, 'GU915911873', '2026-02-19', '2026-02-23', NULL, 'En camino'),
(18, 28, 8, 'GU831361497', '2026-02-21', '2026-02-25', '2026-02-25', 'Entregado'),
(19, 29, 9, 'GU706118438', '2026-02-23', '2026-02-27', NULL, 'Pendiente'),
(20, 30, 10, 'GU770575153', '2026-02-25', '2026-03-01', '2026-03-01', 'Entregado'),
(21, 31, 11, 'GU773469560', '2026-02-27', '2026-03-03', '2026-03-03', 'Entregado'),
(22, 32, 12, 'GU572191734', '2026-03-01', '2026-03-05', '2026-03-05', 'Entregado'),
(23, 33, 13, 'GU574817290', '2026-03-03', '2026-03-07', '2026-03-07', 'Entregado'),
(24, 34, 14, 'GU955052486', '2026-03-05', '2026-03-09', '2026-03-09', 'Entregado'),
(25, 35, 15, 'GU160314355', '2026-03-07', '2026-03-11', '2026-03-11', 'Entregado'),
(26, 36, 16, 'GU179661615', '2026-03-09', '2026-03-13', '2026-03-13', 'Entregado'),
(27, 37, 17, 'GU585238820', '2026-03-11', '2026-03-15', '2026-03-15', 'Entregado'),
(28, 38, 18, 'GU495928981', '2026-03-13', '2026-03-17', '2026-03-17', 'Entregado'),
(29, 39, 19, 'GU182389284', '2026-03-15', '2026-03-19', NULL, 'En camino'),
(30, 40, 20, 'GU196955134', '2026-03-17', '2026-03-21', '2026-03-21', 'Entregado'),
(31, 41, 21, 'GU644459924', '2026-03-19', '2026-03-23', '2026-03-23', 'Entregado'),
(32, 42, 22, 'GU723123952', '2026-03-21', '2026-03-25', '2026-03-25', 'Entregado'),
(33, 43, 23, 'GU950207886', '2026-03-23', '2026-03-27', '2026-03-27', 'Entregado'),
(34, 44, 24, 'GU144047803', '2026-03-25', '2026-03-29', NULL, 'En camino'),
(35, 45, 25, 'GU969533218', '2026-03-27', '2026-03-31', '2026-03-31', 'Entregado'),
(36, 46, 26, 'GU302120588', '2026-03-29', '2026-04-02', '2026-04-02', 'Entregado'),
(37, 47, 27, 'GU610702777', '2026-03-31', '2026-04-04', '2026-04-04', 'Entregado'),
(38, 48, 28, 'GU166436383', '2026-04-02', '2026-04-06', '2026-04-06', 'Entregado'),
(39, 49, 29, 'GU970768982', '2026-04-04', '2026-04-08', '2026-04-08', 'Entregado'),
(40, 50, 30, 'GU468763500', '2026-04-06', '2026-04-10', NULL, 'En camino'),
(41, 51, 31, 'GU190547712', '2026-04-08', '2026-04-12', NULL, 'Pendiente'),
(42, 52, 32, 'GU285283722', '2026-04-10', '2026-04-14', '2026-04-14', 'Entregado'),
(43, 53, 33, 'GU859803019', '2026-04-12', '2026-04-16', '2026-04-16', 'Entregado'),
(44, 54, 34, 'GU571825556', '2026-04-14', '2026-04-18', '2026-04-18', 'Entregado'),
(45, 55, 35, 'GU754773573', '2026-04-16', '2026-04-20', '2026-04-20', 'Entregado'),
(46, 56, 36, 'GU500346767', '2026-04-18', '2026-04-22', '2026-04-22', 'Entregado'),
(47, 57, 37, 'GU515985367', '2026-04-20', '2026-04-24', NULL, 'Pendiente'),
(48, 58, 38, 'GU463318956', '2026-04-22', '2026-04-26', '2026-04-26', 'Entregado'),
(49, 59, 39, 'GU156227043', '2026-04-24', '2026-04-28', '2026-04-28', 'Entregado'),
(50, 60, 40, 'GU795038832', '2026-04-26', '2026-04-30', NULL, 'En camino'),
(51, 61, 41, 'GU454002758', '2026-04-28', '2026-05-02', '2026-05-02', 'Entregado'),
(52, 62, 42, 'GU828404274', '2026-04-30', '2026-05-04', '2026-05-04', 'Entregado'),
(53, 63, 43, 'GU370578414', '2026-05-02', '2026-05-06', '2026-05-06', 'Entregado'),
(54, 64, 44, 'GU804980312', '2026-05-04', '2026-05-08', NULL, 'En camino'),
(55, 65, 45, 'GU747145068', '2026-05-06', '2026-05-10', NULL, 'Pendiente'),
(56, 66, 46, 'GU457944766', '2026-05-08', '2026-05-12', NULL, 'En camino'),
(57, 67, 47, 'GU812548074', '2026-05-10', '2026-05-14', '2026-05-14', 'Entregado'),
(58, 68, 48, 'GU475617211', '2026-05-12', '2026-05-16', '2026-05-16', 'Entregado'),
(59, 69, 49, 'GU804433388', '2026-05-14', '2026-05-18', '2026-05-18', 'Entregado'),
(60, 70, 50, 'GU520861681', '2026-05-16', '2026-05-20', '2026-05-20', 'Entregado'),
(61, 71, 7, 'GU585337126', '2026-05-18', '2026-05-22', '2026-05-22', 'Entregado'),
(62, 72, 15, 'GU760465943', '2026-05-20', '2026-05-24', NULL, 'Pendiente'),
(63, 73, 47, 'GU940983577', '2026-05-22', '2026-05-26', '2026-05-26', 'Entregado'),
(64, 74, 34, 'GU423873102', '2026-05-24', '2026-05-28', NULL, 'En camino'),
(65, 75, 42, 'GU133447745', '2026-05-26', '2026-05-30', NULL, 'Pendiente'),
(66, 76, 31, 'GU531233244', '2026-05-28', '2026-06-01', NULL, 'En camino'),
(67, 77, 44, 'GU215923129', '2026-05-30', '2026-06-03', NULL, 'En camino'),
(68, 78, 46, 'GU576271425', '2026-06-01', '2026-06-05', NULL, 'Pendiente'),
(69, 79, 6, 'GU445864933', '2026-06-03', '2026-06-07', '2026-06-07', 'Entregado'),
(70, 80, 10, 'GU170525764', '2026-06-05', '2026-06-09', NULL, 'Pendiente'),
(71, 81, 18, 'GU770355806', '2026-06-07', '2026-06-11', '2026-06-11', 'Entregado'),
(72, 82, 38, 'GU688793237', '2026-06-09', '2026-06-13', '2026-06-13', 'Entregado'),
(73, 83, 21, 'GU508992977', '2026-06-11', '2026-06-15', '2026-06-15', 'Entregado'),
(74, 84, 34, 'GU416644047', '2026-06-13', '2026-06-17', NULL, 'En camino'),
(75, 85, 33, 'GU750072069', '2026-06-15', '2026-06-19', NULL, 'En camino'),
(76, 86, 7, 'GU951580447', '2026-06-17', '2026-06-21', '2026-06-21', 'Entregado'),
(77, 87, 8, 'GU802992685', '2026-06-19', '2026-06-23', '2026-06-23', 'Entregado'),
(78, 88, 50, 'GU691991695', '2026-06-21', '2026-06-25', '2026-06-25', 'Entregado'),
(79, 89, 14, 'GU561784080', '2026-06-23', '2026-06-27', NULL, 'En camino'),
(80, 90, 15, 'GU544328940', '2026-06-25', '2026-06-29', NULL, 'En camino'),
(81, 91, 30, 'GU528133274', '2026-06-27', '2026-07-01', NULL, 'En camino'),
(82, 92, 47, 'GU202097643', '2026-06-29', '2026-07-03', NULL, 'En camino'),
(83, 93, 28, 'GU435569630', '2026-07-01', '2026-07-05', '2026-07-05', 'Entregado'),
(84, 94, 17, 'GU501902658', '2026-07-03', '2026-07-07', NULL, 'Pendiente'),
(85, 95, 44, 'GU609241268', '2026-07-05', '2026-07-09', NULL, 'Pendiente'),
(86, 96, 6, 'GU993108266', '2026-07-07', '2026-07-11', NULL, 'Pendiente'),
(87, 97, 6, 'GU563723880', '2026-07-09', '2026-07-13', NULL, 'Pendiente'),
(88, 98, 48, 'GU893276164', '2026-07-11', '2026-07-15', NULL, 'En camino'),
(89, 99, 9, 'GU697398528', '2026-07-13', '2026-07-17', NULL, 'Pendiente'),
(90, 100, 38, 'GU702998820', '2026-07-15', '2026-07-19', '2026-07-19', 'Entregado'),
(91, 101, 22, 'GU819421270', '2026-07-17', '2026-07-21', NULL, 'Pendiente'),
(92, 102, 27, 'GU479673044', '2026-07-19', '2026-07-23', '2026-07-23', 'Entregado'),
(93, 103, 49, 'GU554124989', '2026-07-21', '2026-07-25', '2026-07-25', 'Entregado'),
(94, 104, 4, 'GU408839723', '2026-07-23', '2026-07-27', '2026-07-27', 'Entregado'),
(95, 105, 20, 'GU477577220', '2026-07-25', '2026-07-29', NULL, 'Pendiente'),
(96, 106, 37, 'GU644830077', '2026-07-27', '2026-07-31', NULL, 'Pendiente'),
(97, 107, 10, 'GU805165232', '2026-07-29', '2026-08-02', NULL, 'En camino'),
(98, 108, 15, 'GU216198604', '2026-07-31', '2026-08-04', NULL, 'En camino'),
(99, 109, 36, 'GU494665673', '2026-08-02', '2026-08-06', NULL, 'Pendiente'),
(100, 110, 49, 'GU399110343', '2026-08-04', '2026-08-08', '2026-08-08', 'Entregado'),
(101, 111, 15, 'GU966747347', '2026-08-06', '2026-08-10', NULL, 'En camino'),
(102, 112, 36, 'GU924024405', '2026-08-08', '2026-08-12', '2026-08-12', 'Entregado'),
(103, 113, 40, 'GU824750726', '2026-08-10', '2026-08-14', '2026-08-14', 'Entregado'),
(104, 114, 36, 'GU128189836', '2026-08-12', '2026-08-16', '2026-08-16', 'Entregado'),
(105, 115, 43, 'GU990626742', '2026-08-14', '2026-08-18', '2026-08-18', 'Entregado'),
(106, 116, 18, 'GU131088245', '2026-08-16', '2026-08-20', NULL, 'Pendiente'),
(107, 117, 18, 'GU854517058', '2026-08-18', '2026-08-22', NULL, 'En camino'),
(108, 118, 22, 'GU476908532', '2026-08-20', '2026-08-24', NULL, 'Pendiente'),
(109, 119, 12, 'GU253815116', '2026-08-22', '2026-08-26', '2026-08-26', 'Entregado'),
(110, 120, 43, 'GU530338918', '2026-08-24', '2026-08-28', NULL, 'Pendiente');

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `factura`
--

INSERT INTO `factura` (`numero_factura`, `fecha`, `subtotal`, `iva`, `costo_envio`, `total`, `id_usuario`, `id_empleado`, `metodo_pago`) VALUES
(1, '2026-01-05', 103000.00, 19570.00, 8000.00, 130570.00, '10000000001', 1, 'Tarjeta'),
(2, '2026-01-08', 75000.00, 14250.00, 7000.00, 96250.00, '10000000002', 1, 'Tarjeta'),
(3, '2026-01-12', 150000.00, 28500.00, 9000.00, 187500.00, '10000000003', 2, 'Tarjeta'),
(4, '2026-01-15', 48000.00, 9120.00, 6000.00, 63120.00, '10000000004', 2, 'Tarjeta'),
(5, '2026-01-20', 220000.00, 41800.00, 10000.00, 271800.00, '10000000005', 3, 'Tarjeta'),
(6, '2026-01-22', 90000.00, 17100.00, 7000.00, 114100.00, '10000000006', 1, 'Tarjeta'),
(7, '2026-01-25', 135000.00, 25650.00, 8000.00, 168650.00, '10000000007', 3, 'Tarjeta'),
(8, '2026-01-28', 60000.00, 11400.00, 6000.00, 77400.00, '10000000008', 2, 'Tarjeta'),
(9, '2026-02-02', 175000.00, 33250.00, 9000.00, 217250.00, '10000000009', 1, 'Tarjeta'),
(10, '2026-02-05', 85000.00, 16150.00, 7000.00, 108150.00, '10000000010', 3, 'Tarjeta'),
(11, '2026-01-05', 103000.00, 19570.00, 8000.00, 130570.00, '10000000001', 1, 'Tarjeta'),
(12, '2026-01-08', 75000.00, 14250.00, 7000.00, 96250.00, '10000000002', 1, 'Tarjeta'),
(13, '2026-01-12', 150000.00, 28500.00, 9000.00, 187500.00, '10000000003', 2, 'Tarjeta'),
(14, '2026-01-15', 48000.00, 9120.00, 6000.00, 63120.00, '10000000004', 2, 'Tarjeta'),
(15, '2026-01-20', 220000.00, 41800.00, 10000.00, 271800.00, '10000000005', 3, 'Tarjeta'),
(16, '2026-01-22', 90000.00, 17100.00, 7000.00, 114100.00, '10000000006', 1, 'Tarjeta'),
(17, '2026-01-25', 135000.00, 25650.00, 8000.00, 168650.00, '10000000007', 3, 'Tarjeta'),
(18, '2026-01-28', 60000.00, 11400.00, 6000.00, 77400.00, '10000000008', 2, 'Tarjeta'),
(19, '2026-02-02', 175000.00, 33250.00, 9000.00, 217250.00, '10000000009', 1, 'Tarjeta'),
(20, '2026-02-05', 85000.00, 16150.00, 7000.00, 108150.00, '10000000010', 3, 'Tarjeta'),
(21, '2026-02-06', 129000.00, 24510.00, 6000.00, 159510.00, '10000000001', 1, 'PSE'),
(22, '2026-02-08', 86000.00, 16340.00, 9000.00, 111340.00, '10000000002', 2, 'PSE'),
(23, '2026-02-10', 132000.00, 25080.00, 9000.00, 166080.00, '10000000003', 3, 'PSE'),
(24, '2026-02-12', 418000.00, 79420.00, 10000.00, 507420.00, '10000000004', 4, 'PSE'),
(25, '2026-02-14', 106000.00, 20140.00, 9000.00, 135140.00, '10000000005', 5, 'PSE'),
(26, '2026-02-16', 70000.00, 13300.00, 7000.00, 90300.00, '10000000006', 6, 'PSE'),
(27, '2026-02-18', 489000.00, 92910.00, 6000.00, 587910.00, '10000000007', 7, 'PSE'),
(28, '2026-02-20', 208000.00, 39520.00, 9000.00, 256520.00, '10000000008', 8, 'PSE'),
(29, '2026-02-22', 51000.00, 9690.00, 8000.00, 68690.00, '10000000009', 9, 'PSE'),
(30, '2026-02-24', 330000.00, 62700.00, 10000.00, 402700.00, '10000000010', 10, 'PSE'),
(31, '2026-02-26', 424000.00, 80560.00, 10000.00, 514560.00, '10000000011', 11, 'PSE'),
(32, '2026-02-28', 612000.00, 116280.00, 8000.00, 736280.00, '10000000012', 12, 'PSE'),
(33, '2026-03-02', 93000.00, 17670.00, 7000.00, 117670.00, '10000000013', 13, 'PSE'),
(34, '2026-03-04', 198000.00, 37620.00, 10000.00, 245620.00, '10000000014', 14, 'PSE'),
(35, '2026-03-06', 46000.00, 8740.00, 6000.00, 60740.00, '10000000015', 15, 'PSE'),
(36, '2026-03-08', 149000.00, 28310.00, 8000.00, 185310.00, '10000000016', 16, 'PSE'),
(37, '2026-03-10', 59000.00, 11210.00, 7000.00, 77210.00, '10000000017', 17, 'PSE'),
(38, '2026-03-12', 286000.00, 54340.00, 8000.00, 348340.00, '10000000018', 18, 'PSE'),
(39, '2026-03-14', 94000.00, 17860.00, 6000.00, 117860.00, '10000000019', 19, 'PSE'),
(40, '2026-03-16', 162000.00, 30780.00, 9000.00, 201780.00, '10000000020', 20, 'PSE'),
(41, '2026-03-18', 147000.00, 27930.00, 9000.00, 183930.00, '10000000021', 21, 'Transferencia'),
(42, '2026-03-20', 91000.00, 17290.00, 7000.00, 115290.00, '10000000022', 22, 'Transferencia'),
(43, '2026-03-22', 154000.00, 29260.00, 10000.00, 193260.00, '10000000023', 23, 'Transferencia'),
(44, '2026-03-24', 489000.00, 92910.00, 7000.00, 588910.00, '10000000024', 24, 'Transferencia'),
(45, '2026-03-26', 537000.00, 102030.00, 10000.00, 649030.00, '10000000025', 25, 'Transferencia'),
(46, '2026-03-28', 576000.00, 109440.00, 8000.00, 693440.00, '10000000026', 26, 'Transferencia'),
(47, '2026-03-30', 162000.00, 30780.00, 9000.00, 201780.00, '10000000027', 27, 'Transferencia'),
(48, '2026-04-01', 525000.00, 99750.00, 6000.00, 630750.00, '10000000028', 28, 'Transferencia'),
(49, '2026-04-03', 394000.00, 74860.00, 6000.00, 474860.00, '10000000029', 29, 'Transferencia'),
(50, '2026-04-05', 54000.00, 10260.00, 6000.00, 70260.00, '10000000030', 30, 'Transferencia'),
(51, '2026-04-07', 178000.00, 33820.00, 10000.00, 221820.00, '10000000031', 31, 'Transferencia'),
(52, '2026-04-09', 430000.00, 81700.00, 10000.00, 521700.00, '10000000032', 32, 'Transferencia'),
(53, '2026-04-11', 212000.00, 40280.00, 9000.00, 261280.00, '10000000033', 33, 'Transferencia'),
(54, '2026-04-13', 42000.00, 7980.00, 6000.00, 55980.00, '10000000034', 34, 'Transferencia'),
(55, '2026-04-15', 112000.00, 21280.00, 6000.00, 139280.00, '10000000035', 35, 'Transferencia'),
(56, '2026-04-17', 376000.00, 71440.00, 7000.00, 454440.00, '10000000036', 36, 'Transferencia'),
(57, '2026-04-19', 111000.00, 21090.00, 9000.00, 141090.00, '10000000037', 37, 'Transferencia'),
(58, '2026-04-21', 627000.00, 119130.00, 8000.00, 754130.00, '10000000038', 38, 'Transferencia'),
(59, '2026-04-23', 27000.00, 5130.00, 9000.00, 41130.00, '10000000039', 39, 'Transferencia'),
(60, '2026-04-25', 211000.00, 40090.00, 7000.00, 258090.00, '10000000040', 40, 'Transferencia'),
(61, '2026-04-27', 150000.00, 28500.00, 10000.00, 188500.00, '10000000041', 41, 'Transferencia'),
(62, '2026-04-29', 254000.00, 48260.00, 10000.00, 312260.00, '10000000042', 42, 'Transferencia'),
(63, '2026-05-01', 107000.00, 20330.00, 9000.00, 136330.00, '10000000043', 43, 'Transferencia'),
(64, '2026-05-03', 228000.00, 43320.00, 8000.00, 279320.00, '10000000044', 44, 'Transferencia'),
(65, '2026-05-05', 204000.00, 38760.00, 8000.00, 250760.00, '10000000045', 45, 'Transferencia'),
(66, '2026-05-07', 218000.00, 41420.00, 6000.00, 265420.00, '10000000046', 46, 'Transferencia'),
(67, '2026-05-09', 516000.00, 98040.00, 6000.00, 620040.00, '10000000047', 47, 'Transferencia'),
(68, '2026-05-11', 99000.00, 18810.00, 10000.00, 127810.00, '10000000048', 48, 'Transferencia'),
(69, '2026-05-13', 60000.00, 11400.00, 8000.00, 79400.00, '10000000049', 49, 'Transferencia'),
(70, '2026-05-15', 356000.00, 67640.00, 7000.00, 430640.00, '10000000050', 50, 'Transferencia'),
(71, '2026-05-17', 167000.00, 31730.00, 6000.00, 204730.00, '10000000038', 30, 'PSE'),
(72, '2026-05-19', 183000.00, 34770.00, 9000.00, 226770.00, '10000000023', 39, 'Tarjeta'),
(73, '2026-05-21', 600000.00, 114000.00, 6000.00, 720000.00, '10000000091', 69, 'Tarjeta'),
(74, '2026-05-23', 125000.00, 23750.00, 7000.00, 155750.00, '10000000036', 6, 'Tarjeta'),
(75, '2026-05-25', 238000.00, 45220.00, 10000.00, 293220.00, '10000000071', 38, 'Transferencia'),
(76, '2026-05-27', 134000.00, 25460.00, 6000.00, 165460.00, '10000000017', 82, 'PSE'),
(77, '2026-05-29', 241000.00, 45790.00, 6000.00, 292790.00, '10000000014', 2, 'Transferencia'),
(78, '2026-05-31', 618000.00, 117420.00, 8000.00, 743420.00, '10000000037', 61, 'PSE'),
(79, '2026-06-02', 435000.00, 82650.00, 7000.00, 524650.00, '10000000057', 44, 'Tarjeta'),
(80, '2026-06-04', 114000.00, 21660.00, 7000.00, 142660.00, '10000000007', 33, 'PSE'),
(81, '2026-06-06', 495000.00, 94050.00, 10000.00, 599050.00, '10000000015', 9, 'PSE'),
(82, '2026-06-08', 50000.00, 9500.00, 7000.00, 66500.00, '10000000063', 10, 'Transferencia'),
(83, '2026-06-10', 340000.00, 64600.00, 6000.00, 410600.00, '10000000081', 88, 'Tarjeta'),
(84, '2026-06-12', 702000.00, 133380.00, 10000.00, 845380.00, '10000000020', 20, 'Transferencia'),
(85, '2026-06-14', 265000.00, 50350.00, 7000.00, 322350.00, '10000000039', 11, 'Tarjeta'),
(86, '2026-06-16', 690000.00, 131100.00, 10000.00, 831100.00, '10000000016', 72, 'PSE'),
(87, '2026-06-18', 295000.00, 56050.00, 7000.00, 358050.00, '10000000078', 77, 'Transferencia'),
(88, '2026-06-20', 95000.00, 18050.00, 7000.00, 120050.00, '10000000029', 100, 'Transferencia'),
(89, '2026-06-22', 105000.00, 19950.00, 8000.00, 132950.00, '10000000049', 58, 'PSE'),
(90, '2026-06-24', 156000.00, 29640.00, 7000.00, 192640.00, '10000000039', 76, 'PSE'),
(91, '2026-06-26', 225000.00, 42750.00, 10000.00, 277750.00, '10000000040', 73, 'Transferencia'),
(92, '2026-06-28', 328000.00, 62320.00, 6000.00, 396320.00, '10000000008', 79, 'Transferencia'),
(93, '2026-06-30', 366000.00, 69540.00, 8000.00, 443540.00, '10000000013', 98, 'Tarjeta'),
(94, '2026-07-02', 285000.00, 54150.00, 7000.00, 346150.00, '10000000081', 28, 'PSE'),
(95, '2026-07-04', 163000.00, 30970.00, 7000.00, 200970.00, '10000000085', 11, 'Tarjeta'),
(96, '2026-07-06', 470000.00, 89300.00, 10000.00, 569300.00, '10000000031', 23, 'Transferencia'),
(97, '2026-07-08', 50000.00, 9500.00, 8000.00, 67500.00, '10000000010', 21, 'Tarjeta'),
(98, '2026-07-10', 454000.00, 86260.00, 7000.00, 547260.00, '10000000053', 58, 'Transferencia'),
(99, '2026-07-12', 75000.00, 14250.00, 6000.00, 95250.00, '10000000077', 61, 'PSE'),
(100, '2026-07-14', 312000.00, 59280.00, 6000.00, 377280.00, '10000000005', 30, 'PSE'),
(101, '2026-07-16', 375000.00, 71250.00, 7000.00, 453250.00, '10000000091', 37, 'Transferencia'),
(102, '2026-07-18', 441000.00, 83790.00, 6000.00, 530790.00, '10000000059', 10, 'Transferencia'),
(103, '2026-07-20', 740000.00, 140600.00, 8000.00, 888600.00, '10000000030', 34, 'Transferencia'),
(104, '2026-07-22', 25000.00, 4750.00, 7000.00, 36750.00, '10000000076', 85, 'Tarjeta'),
(105, '2026-07-24', 126000.00, 23940.00, 10000.00, 159940.00, '10000000055', 15, 'Transferencia'),
(106, '2026-07-26', 155000.00, 29450.00, 8000.00, 192450.00, '10000000029', 83, 'Tarjeta'),
(107, '2026-07-28', 255000.00, 48450.00, 6000.00, 309450.00, '10000000035', 19, 'Tarjeta'),
(108, '2026-07-30', 626000.00, 118940.00, 7000.00, 751940.00, '10000000008', 22, 'PSE'),
(109, '2026-08-01', 234000.00, 44460.00, 8000.00, 286460.00, '10000000077', 96, 'Transferencia'),
(110, '2026-08-03', 111000.00, 21090.00, 6000.00, 138090.00, '10000000037', 57, 'Tarjeta'),
(111, '2026-08-05', 53000.00, 10070.00, 7000.00, 70070.00, '10000000060', 89, 'PSE'),
(112, '2026-08-07', 585000.00, 111150.00, 9000.00, 705150.00, '10000000090', 52, 'PSE'),
(113, '2026-08-09', 114000.00, 21660.00, 10000.00, 145660.00, '10000000065', 70, 'PSE'),
(114, '2026-08-11', 300000.00, 57000.00, 6000.00, 363000.00, '10000000057', 11, 'Transferencia'),
(115, '2026-08-13', 85000.00, 16150.00, 6000.00, 107150.00, '10000000006', 56, 'Transferencia'),
(116, '2026-08-15', 333000.00, 63270.00, 9000.00, 405270.00, '10000000042', 78, 'PSE'),
(117, '2026-08-17', 458000.00, 87020.00, 9000.00, 554020.00, '10000000004', 12, 'Tarjeta'),
(118, '2026-08-19', 557000.00, 105830.00, 8000.00, 670830.00, '10000000087', 74, 'Transferencia'),
(119, '2026-08-21', 55000.00, 10450.00, 10000.00, 75450.00, '10000000003', 98, 'Transferencia'),
(120, '2026-08-23', 191000.00, 36290.00, 10000.00, 237290.00, '10000000106', 35, 'Transferencia');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodo_pago`
--

CREATE TABLE `metodo_pago` (
  `id_metodo` int(11) NOT NULL,
  `nombre_metodo` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `metodo_pago`
--

INSERT INTO `metodo_pago` (`id_metodo`, `nombre_metodo`) VALUES
(1, 'PSE'),
(2, 'TARJETA'),
(3, 'TRANSFERENCIA');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto`
--

CREATE TABLE `producto` (
  `id_producto` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `id_categoria` int(11) NOT NULL,
  `id_proveedor` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `producto`
--

INSERT INTO `producto` (`id_producto`, `nombre`, `descripcion`, `precio`, `stock`, `id_categoria`, `id_proveedor`) VALUES
(1, 'Purina Pro Plan Adult Complete', 'Alimento premium para perros adultos', 98000.00, 50, 1, 1),
(2, 'Dog Chow Cachorros', 'Alimento completo para cachorros', 72000.00, 45, 1, 2),
(3, 'Royal Canin Mini Adult', 'Alimento para perros adultos de razas pequeñas', 125000.00, 35, 1, 4),
(4, 'Chunky Adultos Pollo', 'Concentrado para perros adultos sabor pollo', 69000.00, 40, 1, 6),
(5, 'Pedigree Adulto Carne y Vegetales', 'Alimento balanceado para perros adultos', 62000.00, 60, 1, 8),
(6, 'Hill''s Science Diet Adult', 'Nutrición premium para perros adultos', 145000.00, 20, 1, 5),
(7, 'Agility Gold Grandes Adultos', 'Alimento para perros de razas grandes', 118000.00, 25, 1, 7),
(8, 'Monello Perros Adultos', 'Concentrado premium para perros adultos', 76000.00, 30, 1, 10),
(9, 'Taste of the Wild High Prairie', 'Alimento libre de granos para perros', 185000.00, 18, 1, 11),
(10, 'Diamond Naturals Adult Lamb & Rice', 'Alimento premium con cordero y arroz', 162000.00, 15, 1, 12),
(11, 'Purina Pro Plan Adult Cat', 'Alimento premium para gatos adultos', 89000.00, 40, 2, 1),
(12, 'Cat Chow Adultos', 'Alimento balanceado para gatos adultos', 58000.00, 45, 2, 3),
(13, 'Royal Canin Indoor 27', 'Alimento para gatos de interior', 129000.00, 25, 2, 4),
(14, 'Whiskas Adulto Carne', 'Alimento seco para gatos adultos', 46000.00, 60, 2, 9),
(15, 'Hill''s Science Diet Adult Cat', 'Nutrición premium para gatos adultos', 148000.00, 20, 2, 5),
(16, 'Agility Gold Gatos Adultos', 'Concentrado premium para gatos', 79000.00, 35, 2, 7),
(17, 'Monello Cat Adult', 'Alimento completo para gatos adultos', 68000.00, 30, 2, 10),
(18, 'Equilibrio Adult Cat', 'Alimento premium para gatos', 99000.00, 20, 2, 13),
(19, 'Diamond Naturals Indoor Cat', 'Alimento para gatos de interior', 158000.00, 18, 2, 12),
(20, 'Taste of the Wild Rocky Mountain', 'Alimento libre de granos para gatos', 172000.00, 15, 2, 11),
(21, 'Collar Tuff para Perro', 'Collar ajustable de nylon', 28000.00, 50, 3, 14),
(22, 'Correa Retráctil Flexi', 'Correa retráctil de 5 metros', 85000.00, 25, 3, 15),
(23, 'Comedero Doble Ferplast', 'Comedero doble para perro y gato', 45000.00, 30, 3, 16),
(24, 'Bebedero Automático Petmate', 'Dispensador automático de agua', 135000.00, 20, 3, 17),
(25, 'Guacal Petmate Vari Kennel', 'Transportadora para mascotas', 210000.00, 12, 3, 17),
(26, 'Juguete Kong Classic', 'Juguete de caucho resistente para perros', 62000.00, 40, 3, 18),
(27, 'Rascador Trixie', 'Rascador para gatos con poste de sisal', 95000.00, 18, 3, 19),
(28, 'Arena Sanitaria Cats Best', 'Arena aglomerante para gatos', 58000.00, 35, 3, 20),
(29, 'Shampoo Furminator Deshedding', 'Shampoo para perros y gatos', 48000.00, 25, 3, 21),
(30, 'Cepillo Furminator', 'Cepillo removedor de pelo para mascotas', 110000.00, 20, 3, 21),
(31, 'Royal Canin Puppy Medium', 'Alimento para cachorros de raza mediana', 43000.00, 15, 1, 4),
(32, 'Hill''s Science Diet Sensitive Stomach', 'Alimento para perros con estómago sensible', 43000.00, 37, 1, 5),
(33, 'Pedigree Dentastix Grande', 'Snack dental para perros grandes', 44000.00, 57, 3, 8),
(34, 'Whiskas Temptations Pollo', 'Snack cremoso para gatos sabor pollo', 209000.00, 33, 3, 9),
(35, 'Purina ONE SmartBlend Adulto', 'Alimento balanceado para perros adultos', 53000.00, 45, 1, 1),
(36, 'Fancy Feast Gourmet Salmón', 'Alimento húmedo para gatos sabor salmón', 35000.00, 47, 2, 22),
(37, 'Nutrican Perros Adultos', 'Concentrado para perros adultos', 163000.00, 45, 1, 22),
(38, 'Team Cachorros Raza Pequeña', 'Alimento para cachorros pequeños', 104000.00, 52, 1, 23),
(39, 'Ganador Premium Adulto', 'Alimento balanceado premium para perros', 51000.00, 36, 1, 24),
(40, 'Friskies Seafood Sensations', 'Alimento seco para gatos con mariscos', 110000.00, 52, 2, 25),
(41, 'Excellent Perros Raza Grande', 'Concentrado para perros de raza grande', 212000.00, 37, 1, 26),
(42, 'Baw Waw Cachorros', 'Alimento para cachorros en crecimiento', 204000.00, 13, 1, 27),
(43, 'Master Dog Adulto', 'Concentrado económico para perros adultos', 93000.00, 48, 1, 28),
(44, 'Master Cat Adulto', 'Concentrado económico para gatos adultos', 99000.00, 32, 2, 29),
(45, 'Nupec Gold Adulto', 'Alimento premium para perros adultos', 46000.00, 46, 1, 30),
(46, 'Eukanuba Adult Large Breed', 'Alimento para perros grandes adultos', 149000.00, 23, 1, 31),
(47, 'Iams ProActive Health', 'Alimento premium para perros adultos', 59000.00, 52, 1, 32),
(48, 'Farmina N&D Ancestral Grain', 'Alimento con bajo contenido de granos', 143000.00, 24, 1, 33),
(49, 'Acana Wild Prairie', 'Alimento libre de granos para perros', 47000.00, 32, 1, 34),
(50, 'Orijen Original', 'Alimento biológicamente apropiado para perros', 162000.00, 33, 1, 35),
(51, 'Blue Buffalo Life Protection', 'Alimento natural para perros adultos', 49000.00, 58, 1, 36),
(52, 'Nutrapet Cachorros', 'Alimento para cachorros', 91000.00, 46, 1, 37),
(53, 'Contegral Balanceado Canino', 'Concentrado balanceado para perros', 77000.00, 37, 1, 38),
(54, 'Italcol Nutrimascota', 'Alimento balanceado para perros', 163000.00, 59, 1, 39),
(55, 'Vitalcan Holistic Adulto', 'Alimento natural para perros adultos', 179000.00, 49, 1, 40),
(56, 'Purina ONE Gatos Adulto', 'Alimento balanceado para gatos adultos', 192000.00, 51, 2, 41),
(57, 'Fancy Feast Classic Atún', 'Alimento húmedo para gatos sabor atún', 162000.00, 11, 2, 42),
(58, 'Nutrissimo Senior', 'Alimento para perros senior', 175000.00, 52, 1, 43),
(59, 'Solla Nutrican Cachorros', 'Concentrado para cachorros', 197000.00, 27, 1, 44),
(60, 'Catsan Arena Higiénica', 'Arena sanitaria para gatos', 27000.00, 21, 3, 45),
(61, 'PetSafe Comedero Automático', 'Comedero automático programable', 89000.00, 54, 3, 46),
(62, 'Chuckit! Lanzador de Pelotas', 'Lanzador de pelotas para perros', 215000.00, 29, 3, 47),
(63, 'Nina Ottosson Juguete Interactivo', 'Juguete interactivo estimulante para mascotas', 106000.00, 32, 3, 48),
(64, 'Zolux Correa Ajustable', 'Correa ajustable para perros', 21000.00, 21, 3, 49),
(65, 'Imac Jaula para Mascotas', 'Jaula de transporte para mascotas pequeñas', 56000.00, 46, 3, 50),
(66, 'Savic Transportadora Mediana', 'Transportadora rígida para mascotas', 188000.00, 35, 3, 51),
(67, 'Kiwoko Cama Ortopédica', 'Cama ortopédica para perros', 37000.00, 19, 3, 52),
(68, 'Menforsan Shampoo Antipulgas', 'Shampoo antipulgas para perros y gatos', 209000.00, 50, 3, 53),
(69, 'Beaphar Pipeta Antipulgas', 'Pipeta antipulgas y garrapatas', 27000.00, 15, 3, 54),
(70, 'Virbac Shampoo Dermatológico', 'Shampoo dermatológico veterinario', 211000.00, 43, 3, 55),
(71, 'Bayer Seresto Collar Antipulgas', 'Collar antipulgas y garrapatas de larga duración', 75000.00, 34, 3, 56),
(72, 'Bravecto Tableta Antipulgas', 'Tableta masticable antipulgas para perros', 127000.00, 39, 3, 57),
(73, 'NexGard Tableta Masticable', 'Antiparasitario masticable para perros', 107000.00, 20, 3, 58),
(74, 'Drontal Desparasitante', 'Tableta desparasitante para perros y gatos', 114000.00, 29, 3, 59),
(75, 'Frontline Plus Pipeta', 'Pipeta antipulgas y garrapatas', 204000.00, 30, 3, 60),
(76, 'Hill''s Prescription Diet id', 'Alimento terapéutico digestivo para perros', 218000.00, 46, 1, 61),
(77, 'Royal Canin Veterinary Renal', 'Alimento terapéutico renal para perros', 172000.00, 15, 1, 62),
(78, 'Purina Pro Plan Veterinary EN', 'Alimento terapéutico gastrointestinal', 33000.00, 19, 1, 63),
(79, 'Kong Puppy Juguete', 'Juguete de caucho para cachorros', 60000.00, 58, 3, 65),
(80, 'Trixie Junior Rascador', 'Rascador para gatitos', 178000.00, 13, 3, 66),
(81, 'Alimento Premium Aves Exóticas', 'Mezcla de semillas para aves', 32000.00, 17, 1, 6),
(82, 'Pecera Kit Completo 20L', 'Kit de pecera con filtro y luz', 210000.00, 32, 2, 55),
(83, 'Alimento Peces Tropicales', 'Escamas para peces de acuario', 18000.00, 52, 2, 48),
(84, 'Jaula para Hámster Deluxe', 'Jaula con accesorios para roedores', 95000.00, 14, 3, 65),
(85, 'Alimento Conejos y Cuyes', 'Pellets balanceados para roedores', 27000.00, 51, 3, 44);

--
-- Productos nuevos agregados en las categorias restantes (Perros, Gatos, Otros)
--

INSERT INTO `producto` (`id_producto`, `nombre`, `descripcion`, `precio`, `stock`, `id_categoria`, `id_proveedor`) VALUES
(86, 'Correa Retráctil 5m', 'Correa retráctil resistente para paseo', 55000.00, 30, 1, 2),
(87, 'Cama Antiestrés Perro', 'Cama redonda con efecto calmante', 130000.00, 15, 1, 4),
(88, 'Snack Masticable de Cuero', 'Premio natural para masticar', 20000.00, 40, 1, 6),
(89, 'Juguete Kong Resistente', 'Juguete de caucho para morder', 35000.00, 25, 1, 7),
(90, 'Alimento Perro Adulto 15kg', 'Alimento balanceado para razas medianas', 175000.00, 20, 1, 1),
(91, 'Rascador Torre para Gato', 'Torre rascadora con niveles', 165000.00, 10, 2, 3),
(92, 'Arenero Cerrado con Filtro', 'Arenero con tapa y filtro de olores', 98000.00, 18, 2, 3),
(93, 'Juguete Ratón de Peluche', 'Juguete relleno con catnip', 12000.00, 45, 2, 3),
(94, 'Alimento Gato Adulto 10kg', 'Alimento balanceado para gatos adultos', 145000.00, 22, 2, 3),
(95, 'Transportadora para Gato', 'Transportadora ventilada tamaño mediano', 110000.00, 12, 2, 5),
(96, 'Kit de Primeros Auxilios Mascota', 'Botiquín básico para emergencias', 60000.00, 15, 3, 8),
(97, 'Placa de Identificación Grabada', 'Placa metálica personalizable', 15000.00, 50, 3, 8),
(98, 'Cepillo Multipropósito Mascotas', 'Cepillo apto para perro y gato', 25000.00, 35, 3, 8),
(99, 'Bolsas Biodegradables Recolectoras', 'Paquete de 60 bolsas', 10000.00, 60, 3, 8),
(100, 'Set de Comederos Viaje', 'Comedero y bebedero plegables', 30000.00, 28, 3, 8),
(101, 'Chaleco Salvavidas para Perro', 'Chaleco flotador para nadar seguro', 68000.00, 20, 1, 7),
(102, 'Hueso de Nylon Sabor Carne', 'Juguete masticable de larga duración', 24000.00, 35, 1, 7),
(103, 'Cepillo Deslanador Doble Cara', 'Cepillo para pelo corto y largo', 45000.00, 25, 1, 8),
(104, 'Impermeable para Perro Talla M', 'Chaqueta impermeable con capucha', 58000.00, 18, 1, 8),
(105, 'Snack Freeze-Dried Pollo', 'Premio liofilizado 100% carne', 32000.00, 30, 1, 6),
(106, 'Fuente de Agua para Gato', 'Fuente con filtro de carbón activado', 89000.00, 15, 2, 5),
(107, 'Casa Iglú para Gato', 'Casita acolchada tipo cueva', 95000.00, 12, 2, 5),
(108, 'Snack Crujiente Pollo y Queso', 'Snack horneado para gatos', 14500.00, 40, 2, 3),
(109, 'Collar Ajustable con Cascabel', 'Collar de seguridad con cierre de escape', 18000.00, 45, 2, 5),
(110, 'Rascador de Cartón Ondulado', 'Rascador plano reversible', 27000.00, 30, 2, 3);

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `proveedor`
--

INSERT INTO `proveedor` (`id_proveedor`, `nombre`, `direccion`, `telefono`, `correo`, `asesor`) VALUES
(1, 'Purina Pro Plan', 'Calle 93 #11-27, Bogotá', '6013456701', 'contacto@purina.com.co', 'Juliana Restrepo'),
(2, 'Dog Chow', 'Carrera 68 #24-30, Bogotá', '6013456702', 'ventas@dogchow.com.co', 'Mauricio Salazar'),
(3, 'Cat Chow', 'Carrera 68 #24-32, Bogotá', '6013456703', 'ventas@catchow.com.co', 'Camila Duarte'),
(4, 'Royal Canin', 'Avenida El Poblado #10-45, Medellín', '6043456704', 'contacto@royalcanin.com.co', 'Felipe Ocampo'),
(5, 'Hill''s Science Diet', 'Calle 127 #7-14, Bogotá', '6013456705', 'contacto@hillspet.com.co', 'Natalia Vargas'),
(6, 'Chunky', 'Autopista Sur #48-12, Cali', '6023456706', 'ventas@chunky.com.co', 'Andrés Cifuentes'),
(7, 'Agility Gold', 'Carrera 50 #15-60, Barranquilla', '6053456707', 'contacto@agilitygold.com.co', 'Diana Marcela Ríos'),
(8, 'Pedigree', 'Zona Industrial Montevideo, Bogotá', '6013456708', 'contacto@pedigree.com.co', 'Jorge Iván Bermúdez'),
(9, 'Whiskas', 'Zona Industrial Montevideo, Bogotá', '6013456709', 'contacto@whiskas.com.co', 'Paula Andrea Suárez'),
(10, 'Monello', 'Carrera 43A #14-109, Medellín', '6043456710', 'contacto@monello.com.co', 'Ricardo Peña'),
(11, 'Taste of the Wild', 'Carrera 15 #93-47, Bogotá', '6013456711', 'contacto@tasteofthewild.com.co', 'Lorena Castañeda'),
(12, 'Diamond Naturals', 'Calle 80 #69-40, Bogotá', '6013456712', 'ventas@diamondnaturals.com.co', 'Santiago Molina'),
(13, 'Equilibrio', 'Carrera 65 #11-83, Medellín', '6043456713', 'contacto@equilibrio.com.co', 'Alejandra Nieto'),
(14, 'Tuff', 'Avenida 30 de Agosto #45-12, Cali', '6023456714', 'ventas@tuff.com.co', 'Óscar Mendoza'),
(15, 'Flexi', 'Carrera 43A #5-15, Medellín', '6043456715', 'contacto@flexi.com.co', 'Tatiana Rincón'),
(16, 'Ferplast', 'Calle 116 #15-32, Bogotá', '6013456716', 'contacto@ferplast.com.co', 'Julián Escobar'),
(17, 'Petmate', 'Autopista Norte #108-27, Bogotá', '6013456717', 'ventas@petmate.com.co', 'Carolina Prieto'),
(18, 'Kong', 'Carrera 7 #71-21, Bogotá', '6013456718', 'contacto@kong.com.co', 'Daniel Ospina'),
(19, 'Trixie', 'Calle 10 #43-50, Medellín', '6043456719', 'contacto@trixie.com.co', 'Marcela Villamil'),
(20, 'Cats Best', 'Carrera 50 #80-15, Barranquilla', '6053456720', 'ventas@catsbest.com.co', 'Iván Camacho'),
(21, 'Furminator', 'Calle 127 #45-20, Bogotá', '6013456721', 'contacto@furminator.com.co', 'Yesenia Rojas'),
(22, 'Nutrican', 'Transversal 16 #79-95, Cali', '6014486102', 'contacto@nutrican.com.co', 'Iván Bermúdez'),
(23, 'Team', 'Carrera 62 #23-71, Bogotá', '6013626181', 'contacto@team.com.co', 'Claudia Nieto'),
(24, 'Ganador', 'Avenida 9 #30-37, Barranquilla', '6038617381', 'contacto@ganador.com.co', 'Diana Morales'),
(25, 'Friskies', 'Diagonal 30 #70-29, Medellín', '6025456573', 'contacto@friskies.com.co', 'Fernando López'),
(26, 'Excellent', 'Avenida 74 #57-16, Medellín', '6046101803', 'contacto@excellent.com.co', 'Iván Mendoza'),
(27, 'Baw Waw', 'Diagonal 21 #77-6, Barranquilla', '6046407658', 'contacto@bawwaw.com.co', 'Miguel González'),
(28, 'Master Dog', 'Transversal 6 #98-87, Medellín', '6031674975', 'contacto@masterdog.com.co', 'Julián Rojas'),
(29, 'Master Cat', 'Avenida 47 #75-56, Barranquilla', '6042530793', 'contacto@mastercat.com.co', 'Beatriz Vargas'),
(30, 'Nupec', 'Calle 42 #43-53, Cali', '6045835492', 'contacto@nupec.com.co', 'Gustavo Suárez'),
(31, 'Eukanuba', 'Diagonal 23 #41-33, Bogotá', '6032944841', 'contacto@eukanuba.com.co', 'Gustavo Mendoza'),
(32, 'Iams', 'Transversal 119 #53-7, Bogotá', '6029697969', 'contacto@iams.com.co', 'Olga Guerrero'),
(33, 'Farmina N&D', 'Calle 53 #35-71, Barranquilla', '6025832327', 'contacto@farminand.com.co', 'Mónica Guerrero'),
(34, 'Acana', 'Calle 62 #91-21, Bogotá', '6031229419', 'contacto@acana.com.co', 'Fernando Reyes'),
(35, 'Orijen', 'Diagonal 31 #83-20, Bogotá', '6045896624', 'contacto@orijen.com.co', 'Iván Alvarado'),
(36, 'Blue Buffalo', 'Diagonal 63 #59-71, Barranquilla', '6027435505', 'contacto@bluebuffalo.com.co', 'Johanna Mendoza'),
(37, 'Nutrapet', 'Calle 71 #99-54, Medellín', '6039518424', 'contacto@nutrapet.com.co', 'Ana Gutiérrez'),
(38, 'Contegral', 'Transversal 126 #20-58, Cali', '6059125900', 'contacto@contegral.com.co', 'Gladys Suárez'),
(39, 'Italcol', 'Diagonal 83 #25-90, Barranquilla', '6027425184', 'contacto@italcol.com.co', 'Olga Alvarado'),
(40, 'Vitalcan Holistic', 'Avenida 122 #91-49, Bogotá', '6043551903', 'contacto@vitalcanholistic.com.co', 'Paula Ramírez'),
(41, 'Purina ONE', 'Calle 113 #13-68, Cali', '6041257489', 'contacto@purinaone.com.co', 'Hernán Restrepo'),
(42, 'Fancy Feast', 'Calle 121 #34-44, Medellín', '6057668663', 'contacto@fancyfeast.com.co', 'Joaquín Vargas'),
(43, 'Nutrissimo', 'Avenida 125 #70-5, Barranquilla', '6052147909', 'contacto@nutrissimo.com.co', 'Liliana Gutiérrez'),
(44, 'Solla', 'Calle 112 #13-98, Medellín', '6018443690', 'contacto@solla.com.co', 'Adriana Rodríguez'),
(45, 'Catsan', 'Avenida 15 #38-46, Bogotá', '6038225725', 'contacto@catsan.com.co', 'Fabiola Alvarado'),
(46, 'PetSafe', 'Carrera 45 #11-79, Medellín', '6045040453', 'contacto@petsafe.com.co', 'Ingrid Torres'),
(47, 'Chuckit!', 'Diagonal 66 #59-33, Medellín', '6018805654', 'contacto@chuckit.com.co', 'Danilo Cárdenas'),
(48, 'Nina Ottosson', 'Calle 114 #45-76, Medellín', '6038118722', 'contacto@ninaottosson.com.co', 'Manuel Chávez'),
(49, 'Zolux', 'Diagonal 124 #14-31, Medellín', '6047022335', 'contacto@zolux.com.co', 'Emilio Gutiérrez'),
(50, 'Imac', 'Diagonal 71 #2-73, Bogotá', '6019333700', 'contacto@imac.com.co', 'Leonardo Gutiérrez'),
(51, 'Savic', 'Transversal 91 #29-82, Medellín', '6025204819', 'contacto@savic.com.co', 'Fabián Duarte'),
(52, 'Kiwoko', 'Calle 11 #40-57, Medellín', '6017121355', 'contacto@kiwoko.com.co', 'Fernando Gutiérrez'),
(53, 'Menforsan', 'Diagonal 45 #26-17, Cali', '6057138070', 'contacto@menforsan.com.co', 'Mario Ortiz'),
(54, 'Beaphar', 'Avenida 124 #38-96, Medellín', '6032932227', 'contacto@beaphar.com.co', 'Daniela Torres'),
(55, 'Virbac', 'Diagonal 94 #12-51, Medellín', '6015436878', 'contacto@virbac.com.co', 'Manuel Jiménez'),
(56, 'Bayer Seresto', 'Transversal 98 #82-48, Cali', '6014922880', 'contacto@bayerseresto.com.co', 'Johanna Silva'),
(57, 'Bravecto', 'Transversal 57 #83-9, Cali', '6046069909', 'contacto@bravecto.com.co', 'Ricardo Ramírez'),
(58, 'NexGard', 'Calle 78 #64-15, Bogotá', '6014939290', 'contacto@nexgard.com.co', 'Álvaro Álvarez'),
(59, 'Drontal', 'Avenida 108 #76-96, Barranquilla', '6027960607', 'contacto@drontal.com.co', 'Ismael Guerrero'),
(60, 'Frontline', 'Avenida 9 #89-48, Barranquilla', '6028438733', 'contacto@frontline.com.co', 'Diana Jiménez'),
(61, 'Advantix', 'Avenida 92 #8-51, Bogotá', '6034184459', 'contacto@advantix.com.co', 'Joaquín Salazar'),
(62, 'Hill''s Prescription Diet', 'Carrera 6 #7-43, Bogotá', '6023112652', 'contacto@hillsprescriptiondiet.com.co', 'David Hernández'),
(63, 'Royal Canin Veterinary', 'Transversal 56 #30-43, Medellín', '6021047572', 'contacto@royalcaninveterinary.com.co', 'Carolina Ramírez'),
(64, 'Purina Pro Plan Veterinary Diets', 'Carrera 29 #85-4, Cali', '6021249314', 'contacto@purinaproplanveterinarydiets.com.co', 'Piedad Cruz'),
(65, 'Pedigree Dentastix', 'Calle 45 #34-7, Cali', '6028062546', 'contacto@pedigreedentastix.com.co', 'Fabián Hernández'),
(66, 'Whiskas Temptations', 'Diagonal 93 #66-76, Barranquilla', '6018583392', 'contacto@whiskastemptations.com.co', 'Vicente Martínez'),
(67, 'Kong Puppy', 'Diagonal 8 #8-62, Cali', '6048151684', 'contacto@kongpuppy.com.co', 'Óscar Escobar'),
(68, 'Trixie Junior', 'Calle 21 #42-78, Barranquilla', '6022101965', 'contacto@trixiejunior.com.co', 'Johanna Correa'),
(69, 'Ferplast Atlas', 'Diagonal 76 #59-65, Cali', '6058217547', 'contacto@ferplastatlas.com.co', 'Mónica Sánchez'),
(70, 'Petmate Sky Kennel', 'Diagonal 116 #30-53, Medellín', '6038608449', 'contacto@petmateskykennel.com.co', 'Nubia Pérez'),
(71, 'Flexi New Comfort', 'Diagonal 81 #86-33, Cali', '6033560856', 'contacto@flexinewcomfort.com.co', 'Óscar Hernández');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pse`
--

CREATE TABLE `pse` (
  `id_pse` int(11) NOT NULL,
  `numero_factura` int(11) NOT NULL,
  `banco` varchar(100) NOT NULL,
  `monto` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `pse`
--

INSERT INTO `pse` (`id_pse`, `numero_factura`, `banco`, `monto`) VALUES
(1, 2, 'Bancolombia', 96250.00),
(2, 5, 'Davivienda', 271800.00),
(3, 8, 'Banco de Bogotá', 77400.00),
(4, 21, 'Banco de Bogotá', 63804.00),
(5, 22, 'Davivienda', 44536.00),
(6, 23, 'Banco Caja Social', 66432.00),
(7, 24, 'Banco AV Villas', 202968.00),
(8, 25, 'Scotiabank Colpatria', 54056.00),
(9, 26, 'BBVA Colombia', 36120.00),
(10, 27, 'BBVA Colombia', 235164.00),
(11, 28, 'Bancolombia', 102608.00),
(12, 29, 'Davivienda', 27476.00),
(13, 30, 'BBVA Colombia', 161080.00),
(14, 31, 'Davivienda', 205824.00),
(15, 32, 'Banco de Bogotá', 294512.00),
(16, 33, 'Bancolombia', 47068.00),
(17, 34, 'Banco Popular', 98248.00),
(18, 35, 'Davivienda', 24296.00),
(19, 36, 'Banco Popular', 74124.00),
(20, 37, 'Banco Caja Social', 30884.00),
(21, 38, 'Banco Agrario', 139336.00),
(22, 39, 'Davivienda', 47144.00),
(23, 40, 'Banco Agrario', 80712.00),
(24, 41, 'Bancolombia', 73572.00),
(25, 42, 'BBVA Colombia', 46116.00),
(26, 43, 'Scotiabank Colpatria', 77304.00),
(27, 44, 'Banco AV Villas', 235564.00),
(28, 45, 'Davivienda', 259612.00),
(29, 46, 'Banco Caja Social', 277376.00),
(30, 47, 'Scotiabank Colpatria', 80712.00),
(31, 48, 'Davivienda', 252300.00),
(32, 49, 'Banco Caja Social', 189944.00),
(33, 50, 'BBVA Colombia', 28104.00),
(34, 51, 'Banco Popular', 88728.00),
(35, 52, 'Davivienda', 208680.00),
(36, 53, 'Davivienda', 104512.00),
(37, 54, 'Banco AV Villas', 22392.00),
(38, 55, 'Itaú Colombia', 55712.00),
(39, 56, 'Banco Caja Social', 181776.00),
(40, 57, 'Itaú Colombia', 56436.00),
(41, 58, 'Banco de Bogotá', 301652.00),
(42, 59, 'Banco Popular', 16452.00),
(43, 60, 'Itaú Colombia', 103236.00),
(44, 61, 'Bancolombia', 75400.00),
(45, 62, 'Banco Popular', 124904.00),
(46, 63, 'Davivienda', 54532.00),
(47, 64, 'Itaú Colombia', 111728.00),
(48, 65, 'Banco AV Villas', 100304.00),
(49, 66, 'Davivienda', 106168.00),
(50, 67, 'Banco Caja Social', 248016.00),
(51, 68, 'Bancolombia', 51124.00),
(52, 69, 'Bancolombia', 31760.00),
(53, 70, 'Banco de Bogotá', 172256.00);

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `tarjeta`
--

INSERT INTO `tarjeta` (`id_tarjeta`, `numero_factura`, `numero_tarjeta`, `cvv`, `fecha_vencimiento`, `franquicia`, `monto`) VALUES
(1, 1, '4532123412341234', '123', '2028-05-01', 'Visa', 130570.00),
(2, 4, '5267894567894567', '456', '2029-08-01', 'MasterCard', 63120.00),
(3, 7, '4111222233334444', '789', '2027-12-01', 'Visa', 168650.00),
(4, 10, '5555666677778888', '321', '2030-03-01', 'MasterCard', 108150.00),
(5, 21, '5218238860727171', '758', '2027-01-01', 'MasterCard', 47853.00),
(6, 22, '5323793793316928', '118', '2028-02-01', 'MasterCard', 33402.00),
(7, 23, '5940896741454711', '240', '2029-03-01', 'Visa', 49824.00),
(8, 24, '5578984396261618', '777', '2030-04-01', 'MasterCard', 152226.00),
(9, 25, '4315365839623712', '838', '2027-05-01', 'MasterCard', 40542.00),
(10, 26, '5985827756688355', '339', '2028-06-01', 'American Express', 27090.00),
(11, 27, '4753821885645616', '896', '2029-07-01', 'MasterCard', 176373.00),
(12, 28, '5313887370812680', '828', '2030-08-01', 'American Express', 76956.00),
(13, 29, '5562362654698361', '625', '2027-09-01', 'Visa', 20607.00),
(14, 30, '5672839167271436', '524', '2028-10-01', 'Visa', 120810.00),
(15, 31, '4767467814616221', '201', '2029-11-01', 'American Express', 154368.00),
(16, 32, '4078570087403273', '877', '2030-12-01', 'American Express', 220884.00),
(17, 33, '5855229813115193', '320', '2027-01-01', 'Visa', 35301.00),
(18, 34, '4486593429961782', '344', '2028-02-01', 'MasterCard', 73686.00),
(19, 35, '5713918997821269', '747', '2029-03-01', 'American Express', 18222.00),
(20, 36, '4879102567804941', '684', '2030-04-01', 'MasterCard', 55593.00),
(21, 37, '4138961899149312', '905', '2027-05-01', 'American Express', 23163.00),
(22, 38, '4089733871165155', '865', '2028-06-01', 'Visa', 104502.00),
(23, 39, '5580644731851726', '460', '2029-07-01', 'American Express', 35358.00),
(24, 40, '5293398632092033', '833', '2030-08-01', 'MasterCard', 60534.00),
(25, 41, '5620426816866170', '417', '2027-09-01', 'American Express', 55179.00),
(26, 42, '4585684817836438', '379', '2028-10-01', 'Visa', 34587.00),
(27, 43, '5522820473346554', '291', '2029-11-01', 'MasterCard', 57978.00),
(28, 44, '4546235379552293', '540', '2030-12-01', 'American Express', 176673.00),
(29, 45, '4671584360218305', '717', '2027-01-01', 'American Express', 194709.00),
(30, 46, '4915169367768126', '381', '2028-02-01', 'American Express', 208032.00),
(31, 47, '4744940636211510', '246', '2029-03-01', 'American Express', 60534.00),
(32, 48, '4483700169337272', '680', '2030-04-01', 'Visa', 189225.00),
(33, 49, '4761827322593255', '642', '2027-05-01', 'MasterCard', 142458.00),
(34, 50, '5967285814244048', '611', '2028-06-01', 'American Express', 21078.00),
(35, 51, '5441831145155678', '810', '2029-07-01', 'MasterCard', 66546.00),
(36, 52, '4925382882922438', '929', '2030-08-01', 'American Express', 156510.00),
(37, 53, '5126988257575914', '971', '2027-09-01', 'Visa', 78384.00),
(38, 54, '4459298842923275', '342', '2028-10-01', 'MasterCard', 16794.00),
(39, 55, '4755865731262412', '167', '2029-11-01', 'MasterCard', 41784.00),
(40, 56, '5315221583728632', '796', '2030-12-01', 'American Express', 136332.00),
(41, 57, '4372311480889238', '989', '2027-01-01', 'Visa', 42327.00),
(42, 58, '4622369736536286', '826', '2028-02-01', 'Visa', 226239.00),
(43, 59, '4402549630505961', '729', '2029-03-01', 'American Express', 12339.00),
(44, 60, '5928352638046531', '962', '2030-04-01', 'American Express', 77427.00),
(45, 61, '5942533644537825', '732', '2027-05-01', 'American Express', 56550.00),
(46, 62, '5314594989125012', '924', '2028-06-01', 'American Express', 93678.00),
(47, 63, '5410198135898202', '525', '2029-07-01', 'MasterCard', 40899.00),
(48, 64, '4294612162316658', '508', '2030-08-01', 'Visa', 83796.00),
(49, 65, '4217622849608642', '225', '2027-09-01', 'MasterCard', 75228.00),
(50, 66, '4103575472937850', '354', '2028-10-01', 'Visa', 79626.00),
(51, 67, '4388361091639433', '578', '2029-11-01', 'MasterCard', 186012.00),
(52, 68, '4184744292818491', '346', '2030-12-01', 'Visa', 38343.00),
(53, 69, '4576910887105681', '649', '2027-01-01', 'Visa', 23820.00),
(54, 70, '5807533369927606', '474', '2028-02-01', 'Visa', 129192.00);

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `transferencia_bancaria`
--

INSERT INTO `transferencia_bancaria` (`id_transferencia`, `numero_factura`, `banco`, `numero_cuenta`, `titular`, `monto`) VALUES
(1, 3, 'Bancolombia', '1234567890', 'Carlos Rodriguez', 187500.00),
(2, 6, 'Banco de Bogotá', '9876543210', 'Laura Martinez', 114100.00),
(3, 9, 'Davivienda', '4567891230', 'Sebastián Castro', 217250.00),
(4, 21, 'Banco AV Villas', '4492602049', 'Juan Pérez', 47853.00),
(5, 22, 'BBVA Colombia', '2326569692', 'María Gómez', 33402.00),
(6, 23, 'Davivienda', '5626388820', 'Carlos Rodríguez', 49824.00),
(7, 24, 'Itaú Colombia', '3654424954', 'Laura Martínez', 152226.00),
(8, 25, 'Banco Caja Social', '5482624860', 'Andrés López', 40542.00),
(9, 26, 'Banco Agrario', '6322188162', 'Sofía Hernández', 27090.00),
(10, 27, 'Banco Popular', '3597009738', 'Diego Torres', 176373.00),
(11, 28, 'Banco Popular', '4655730355', 'Valentina Ramírez', 76956.00),
(12, 29, 'Davivienda', '8864285771', 'Sebastián Castro', 20607.00),
(13, 30, 'Scotiabank Colpatria', '2606152369', 'Camila Moreno', 120810.00),
(14, 31, 'Banco de Bogotá', '8086527181', 'Miguel Peña', 154368.00),
(15, 32, 'Itaú Colombia', '7309779967', 'Beatriz Martínez', 220884.00),
(16, 33, 'Davivienda', '7561728644', 'Karen Nieto', 35301.00),
(17, 34, 'Davivienda', '7969918312', 'Rodrigo Ortiz', 73686.00),
(18, 35, 'Banco de Bogotá', '3469810046', 'Vicente Morales', 18222.00),
(19, 36, 'Banco AV Villas', '3869961166', 'Karen Muñoz', 55593.00),
(20, 37, 'Scotiabank Colpatria', '3380064537', 'Joaquín Reyes', 23163.00),
(21, 38, 'BBVA Colombia', '5585133383', 'Liliana Ortiz', 104502.00),
(22, 39, 'Banco Agrario', '3760786161', 'Ximena Correa', 35358.00),
(23, 40, 'BBVA Colombia', '5453811475', 'Hugo Ramos', 60534.00),
(24, 41, 'Bancolombia', '7328203808', 'Elena Romero', 55179.00),
(25, 42, 'Scotiabank Colpatria', '8728116828', 'Fabián Castro', 34587.00),
(26, 43, 'Banco Caja Social', '8267378816', 'Paula Sánchez', 57978.00),
(27, 44, 'Davivienda', '6556684476', 'Pablo Morales', 176673.00),
(28, 45, 'Banco Agrario', '2830154607', 'Beatriz Flores', 194709.00),
(29, 46, 'Davivienda', '5071218314', 'Néstor Correa', 208032.00),
(30, 47, 'Banco de Bogotá', '2881937953', 'Mario Vásquez', 60534.00),
(31, 48, 'Banco Agrario', '3598862507', 'Diana Delgado', 189225.00),
(32, 49, 'Banco Popular', '7004510516', 'Elena Silva', 142458.00),
(33, 50, 'Banco Popular', '3412365931', 'Gustavo Bermúdez', 21078.00),
(34, 51, 'Banco de Bogotá', '1859759428', 'Ana Castro', 66546.00),
(35, 52, 'Banco Caja Social', '9532273208', 'Tatiana Martínez', 156510.00),
(36, 53, 'Banco Caja Social', '3738900744', 'Fabián Delgado', 78384.00),
(37, 54, 'Banco AV Villas', '5407856339', 'Beatriz Castillo', 16794.00),
(38, 55, 'Banco de Bogotá', '3469178881', 'Nubia Vargas', 41784.00),
(39, 56, 'Banco AV Villas', '2479679716', 'Claudia Cruz', 136332.00),
(40, 57, 'Banco AV Villas', '4570796341', 'Joaquín Cruz', 42327.00),
(41, 58, 'Davivienda', '9138644862', 'Gloria Morales', 226239.00),
(42, 59, 'Banco de Bogotá', '9991206531', 'Patricia López', 12339.00),
(43, 60, 'Davivienda', '4709911999', 'Joaquín Vásquez', 77427.00),
(44, 61, 'Banco AV Villas', '5425044246', 'Sandra Cruz', 56550.00),
(45, 62, 'Banco Agrario', '7039121410', 'Ingrid Delgado', 93678.00),
(46, 63, 'Banco Caja Social', '2994763896', 'Carolina Bermúdez', 40899.00),
(47, 64, 'Banco AV Villas', '8561998560', 'Ingrid Pérez', 83796.00),
(48, 65, 'Banco de Bogotá', '2931000173', 'Felipe Gutiérrez', 75228.00),
(49, 66, 'Itaú Colombia', '8788828039', 'Raúl Chávez', 79626.00),
(50, 67, 'Banco Agrario', '9070568519', 'Adriana Ospina', 186012.00),
(51, 68, 'Bancolombia', '7800411181', 'Beatriz Ortiz', 38343.00),
(52, 69, 'Scotiabank Colpatria', '4638577630', 'Hernán Silva', 23820.00),
(53, 70, 'Itaú Colombia', '2720484983', 'Hernán Ramírez', 129192.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `transportadora`
--

CREATE TABLE `transportadora` (
  `id_transportadora` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `transportadora`
--

INSERT INTO `transportadora` (`id_transportadora`, `nombre`, `telefono`) VALUES
(1, 'Servientrega', '6015551234'),
(2, 'Coordinadora', '6044445678'),
(3, 'Inter Rapidisimo', '6017778899'),
(4, 'DHL Express', '6018889900'),
(5, 'Envía', '6016667788'),
(6, 'FedEx Colombia', '6019991122'),
(7, 'TCC', '6043334455'),
(8, 'Deprisa', '6012223344'),
(9, 'UPS Colombia', '6015557788'),
(10, 'Mensajeros Urbanos', '6014445566'),
(11, '472 Envíos', '6055635017'),
(12, 'Redex', '6051170307'),
(13, 'Camión Bus Marfil', '6054205394'),
(14, 'Copetran', '6015049282'),
(15, 'Expreso Brasilia', '6049196976'),
(16, 'Berlinas del Fonce', '6055031966'),
(17, 'Bolivariano', '6049234615'),
(18, 'Flota La Macarena', '6041289293'),
(19, 'Rápido Ochoa', '6015936453'),
(20, 'Expreso Palmira', '6027784725'),
(21, 'Sotrans', '6026137284'),
(22, 'Transportes Ninense', '6057191135'),
(23, 'Envigo', '6049907391'),
(24, 'Domicilios.com', '6038138769'),
(25, 'Rappi Envíos', '6056549757'),
(26, 'Picap Delivery', '6038612582'),
(27, 'Mercado Libre Flex', '6036144280'),
(28, 'Coltrans', '6034867786'),
(29, 'Colvanes', '6014231028'),
(30, 'Transprensa', '6033005795'),
(31, 'AXO Logística', '6054106298'),
(32, 'Nexa Envíos', '6024630331'),
(33, 'Logysem', '6045638893'),
(34, 'Zubut', '6059801946'),
(35, 'Servientrega Mercantil', '6055747930'),
(36, 'Global Cargo', '6014256752'),
(37, 'Rimasa Logística', '6034816534'),
(38, 'Cargo Express', '6034010529'),
(39, 'Transegurcol', '6031237370'),
(40, 'Vía Fácil', '6053123709'),
(41, 'TransCarga Colombia', '6031763626'),
(42, 'Ipsen Logistics', '6015901239'),
(43, 'Andicargo', '6029235577'),
(44, 'Multitransportes', '6011205779'),
(45, 'Colcarga', '6055770422'),
(46, 'Panalpina Colombia', '6049031491'),
(47, 'Kuehne + Nagel Colombia', '6046716097'),
(48, 'Grupo Redes', '6021861958'),
(49, 'Falabella Delivery', '6039014965'),
(50, 'Éxito Envíos', '6012096280'),
(51, 'Coordinadora Carga Aérea', '6049250138'),
(52, 'TCC Carga Pesada', '6011899411'),
(53, 'DHL Same Day', '6023503120'),
(54, 'FedEx Colombia Cargo', '6056097514'),
(55, 'Envía Nacional', '6015163953'),
(56, 'Deprisa Express', '6017982241'),
(57, 'UPS Colombia Cargo', '6054786401'),
(58, 'Inter Rapidísimo Nacional', '6057381684'),
(59, 'Mensajeros Urbanos Express', '6048427625'),
(60, 'Domesa', '6038194570');

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
-- Indices de la tabla `detalle`
--
ALTER TABLE `detalle`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `numero_factura` (`numero_factura`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `empleado`
--
ALTER TABLE `empleado`
  ADD PRIMARY KEY (`id_empleado`),
  ADD UNIQUE KEY `correo` (`correo`);

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
  ADD KEY `id_categoria` (`id_categoria`),
  ADD KEY `id_proveedor` (`id_proveedor`);

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
-- AUTO_INCREMENT de la tabla `metodo_pago`
--
ALTER TABLE `metodo_pago`
  MODIFY `id_metodo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `producto`
--
ALTER TABLE `producto`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=111;

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
-- Filtros para la tabla `detalle`
--
ALTER TABLE `detalle`
  ADD CONSTRAINT `detalle_ibfk_1` FOREIGN KEY (`numero_factura`) REFERENCES `factura` (`numero_factura`),
  ADD CONSTRAINT `detalle_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`);

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