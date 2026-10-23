# Objetos programables de la base de datos `bandp`

Todo lo que se describe aquí vive en un único archivo: **`database/objetos.sql`**,
que `database/init_db.py` ejecuta al final (después de `schema.sql` y `seed.sql`).

El archivo es **idempotente**: cada objeto se elimina antes de recrearse, así que
puede correrse las veces que haga falta sin duplicar nada.

```bash
python database/init_db.py
```

Al terminar imprime cuántas vistas, funciones, procedimientos y triggers quedaron
creados, como verificación rápida.

---

## Por qué el orden importa

`objetos.sql` va **al final**, nunca antes del seed.

Los triggers de `detalle` descuentan stock. Si existieran mientras se carga
`seed.sql`, las ~270 líneas de facturas históricas del `bandp.sql` original
volverían a descontar inventario que ya venía descontado en los datos, y todos
los productos quedarían con stock incorrecto (varios en negativo).

---

## 1. Tabla de apoyo: `auditoria_producto`

Es la **única tabla nueva**, y es puramente aditiva: no cambia ninguna columna,
tipo ni relación de las tablas del `bandp.sql` original. Solo guarda el rastro
que dejan los triggers de `producto`.

| Columna | Para qué |
|---|---|
| `accion` | `ALTA`, `PRECIO`, `STOCK` o `BAJA` |
| `valor_anterior` / `valor_nuevo` | qué había antes y qué quedó |
| `usuario_bd` | `CURRENT_USER()`, quién lo hizo |
| `fecha` | cuándo |

Consulta típica — historial de un producto:

```sql
SELECT * FROM auditoria_producto WHERE id_producto = 5 ORDER BY fecha DESC;
```

### Política de retención

Es la única tabla del esquema que **crece sola y sin límite**: recibe una fila
por cada movimiento de stock, y cada venta mueve stock. Sin nadie que la
recorte, con el tiempo pesa más que las tablas del negocio.

`sp_purgar_auditoria(dias)` es la política: conserva lo reciente y descarta lo
antiguo. Antes de borrar cuenta cuántas filas se van, y al terminar informa
qué quedó, para poder ejecutarlo con confianza.

```sql
CALL sp_purgar_auditoria(180);   -- conserva los últimos 6 meses
```

| Devuelve | Qué dice |
|---|---|
| `purgado_antes_de` | La fecha de corte que se usó |
| `filas_eliminadas` | Cuántas se borraron |
| `filas_conservadas` | Cuántas quedan en la tabla |

Aborta con `SIGNAL` si se le pide conservar menos de un día, para que un `0`
escrito por descuido no vacíe la auditoría entera.

---

## 2. Vistas

| Vista | Qué resuelve |
|---|---|
| `vista_catalogo_productos` | Código + producto + categoría + proveedor + etiqueta de stock. Evita repetir el mismo JOIN triple en toda la tienda. |
| `vista_stock_critico` | Qué hay que reabastecer, con el teléfono y el asesor del proveedor a la mano. |
| `vista_carrito_detalle` | Contenido del carrito de cada cliente, con el subtotal de cada línea ya calculado. |
| `vista_ventas_detalle` | Una fila por producto vendido. Es la vista base de todos los reportes. |
| `vista_resumen_facturas` | Una fila por factura: cliente, método de pago, unidades, estado del envío. Alimenta el listado del panel admin. |
| `vista_ventas_por_categoria` | Cuánto vendió cada categoría (unidades, ingresos, precio promedio). |
| `vista_top_productos` | Ranking de los productos más vendidos. |
| `vista_historial_cliente` | Cuánto ha comprado cada cliente, primera y última compra. |
| `vista_envios_pendientes` | Envíos aún no entregados, con días en tránsito y si van atrasados. |
| `vista_equipo` | El personal con su rol ya resuelto y cuántas ventas ha atendido cada uno. Responde "quién es administrador y quién es vendedor" sin repetir el JOIN `empleado → rol`. |

Ejemplos:

```sql
SELECT * FROM vista_stock_critico;
SELECT * FROM vista_top_productos LIMIT 10;
SELECT * FROM vista_envios_pendientes WHERE cumplimiento = 'Atrasado';
SELECT * FROM vista_equipo WHERE rol = 'Administrador';
```

---

## 3. Funciones

| Función | Devuelve |
|---|---|
| `fn_stock_disponible(id_producto)` | Stock actual, o `0` si el producto no existe. |
| `fn_estado_stock(id_producto)` | `'Agotado'`, `'Stock bajo'` o `'Disponible'`. |
| `fn_total_carrito(id_usuario)` | Subtotal del carrito activo (sin IVA ni envío). |
| `fn_total_comprado_cliente(id_usuario)` | Total histórico gastado por el cliente. |

```sql
SELECT nombre, fn_estado_stock(id_producto) AS estado FROM producto;
SELECT fn_total_carrito('1001');
```

---

## 4. Procedimientos almacenados

| Procedimiento | Qué hace |
|---|---|
| `sp_agregar_al_carrito(id_usuario, id_producto, cantidad)` | Crea el carrito si el cliente aún no tiene, valida stock y suma la cantidad. |
| `sp_vaciar_carrito(id_usuario)` | Borra todas las líneas del carrito. |
| `sp_registrar_venta(id_usuario, id_empleado, iva, envio, metodo, OUT numero_factura)` | Caso de uso completo, en una transacción: valida stock, calcula totales, crea factura y detalle, vacía el carrito. |
| `sp_registrar_pago(numero_factura, metodo, ...)` | Guarda el pago en `pse`, `tarjeta` o `transferencia_bancaria` según el método. De la tarjeta solo conserva los últimos 4 dígitos. |
| `sp_registrar_envio(numero_factura, transportadora, dias, OUT guia)` | Genera la guía (`BP-000042-007`) y programa la entrega estimada. |
| `sp_actualizar_estado_envio(id_envio, estado)` | Cambia el estado; al marcar `Entregado` el trigger sella la fecha real. |
| `sp_cambiar_precio(id_producto, nuevo_precio)` | Cambio de precio controlado, que queda auditado. |
| `sp_reponer_stock_masivo(minimo, objetivo)` | Recorre con un **CURSOR** los productos bajo el mínimo y los sube al objetivo. Devuelve el listado de lo que repuso. |
| `sp_reporte_ventas(fecha_inicio, fecha_fin)` | Ventas por día en un rango: facturas, unidades, subtotal, IVA, total y ticket promedio. |
| `sp_purgar_auditoria(dias)` | Política de retención de `auditoria_producto`: borra el rastro más viejo que `dias` días. Informa cuántas filas quitó y cuántas conservó. |

Todos los procedimientos validan sus entradas y abortan con
`SIGNAL SQLSTATE '45000'` y un mensaje en español cuando algo no cuadra
(carrito vacío, stock insuficiente, factura inexistente, método de pago
desconocido, rango de fechas invertido…).

### Venta completa desde SQL

```sql
CALL sp_agregar_al_carrito('1001', 5, 2);
CALL sp_agregar_al_carrito('1001', 7, 1);

CALL sp_registrar_venta('1001', 999, 0.19, 12000, 'Tarjeta', @factura);
SELECT @factura;

CALL sp_registrar_pago(@factura, 'Tarjeta', NULL, NULL, NULL,
                       '4111111111111111', 'Visa', '2030-01-01');

CALL sp_registrar_envio(@factura, 1, 5, @guia);
SELECT @guia;
```

### Reportes

```sql
CALL sp_reporte_ventas('2025-01-01', '2025-12-31');
CALL sp_reponer_stock_masivo(10, 50);
```

---

## 5. Triggers

### `producto` — validación y auditoría

| Trigger | Qué hace |
|---|---|
| `trg_producto_bi` | BEFORE INSERT: rechaza precio ≤ 0, stock negativo y código vacío; recorta espacios del nombre y **normaliza el código a mayúsculas sin espacios**. |
| `trg_producto_ai` | AFTER INSERT: registra el `ALTA` en `auditoria_producto`. |
| `trg_producto_bu` | BEFORE UPDATE: mismas validaciones y misma normalización al editar. |
| `trg_producto_au` | AFTER UPDATE: registra cada cambio de precio y cada movimiento de stock. |
| `trg_producto_ad` | AFTER DELETE: registra la `BAJA` con los datos que tenía el producto. |

### `carrito_producto` — nadie reserva más de lo que hay

| Trigger | Qué hace |
|---|---|
| `trg_carrito_producto_bi` | BEFORE INSERT: cantidad ≥ 1 y que haya stock suficiente. |
| `trg_carrito_producto_bu` | BEFORE UPDATE: lo mismo al cambiar la cantidad. |

### `factura` — totales coherentes

| Trigger | Qué hace |
|---|---|
| `trg_factura_bi` | BEFORE INSERT: rechaza importes negativos, pone la fecha de hoy si falta y **recalcula `total = subtotal + iva + costo_envio`**. Así ningún cliente (la app, phpMyAdmin, un script) puede guardar un total falseado. |

### `detalle` — control de stock

Estos son los importantes:

| Trigger | Qué hace |
|---|---|
| `trg_detalle_bi` | BEFORE INSERT: valida cantidad y stock (aborta con el nombre del producto en el mensaje) y recalcula `subtotal_producto = cantidad × precio_unitario`. |
| `trg_detalle_ai` | AFTER INSERT: **descuenta el stock vendido**. |
| `trg_detalle_au` | AFTER UPDATE: si se corrige una línea ya facturada, ajusta solo la diferencia (y si cambia el producto, devuelve al viejo y descuenta al nuevo). |
| `trg_detalle_ad` | AFTER DELETE: al anular una línea, el stock vuelve al inventario. |

### `envio` — fechas coherentes

| Trigger | Qué hace |
|---|---|
| `trg_envio_bi` | BEFORE INSERT: si falta la fecha de envío pone hoy, si falta la estimada pone hoy + 5 días, y rechaza una entrega estimada anterior al envío. |
| `trg_envio_bu` | BEFORE UPDATE: al pasar a `Entregado` sella `fecha_entrega_real` con la fecha de hoy; si el estado retrocede, la limpia. |

---

## 6. Cambio en el código Python que esto obligó

`app/services/factura_service.py` **descontaba el stock a mano**:

```python
item.producto.stock -= item.cantidad   # <- esta línea se eliminó
```

Con `trg_detalle_ai` en su lugar, esa línea habría descontado el stock **dos
veces** por cada venta. El descuento quedó con un solo responsable: el trigger.
La base de datos es ahora la única fuente de verdad del inventario, y da igual
si la venta entra por la aplicación Flask, por `sp_registrar_venta` o por un
`INSERT` a mano desde phpMyAdmin.

Por la misma razón, `app/services/producto_service.py` valida ahora precio y
stock (`ProductoService._validar`) con las mismas reglas del trigger: el
servicio comprueba primero para poder mostrar un mensaje al usuario, y el
trigger queda como última línea de defensa si el dato entra por fuera de la app.

---

## 7. Cómo comprobar que funcionan

```sql
-- El trigger descuenta el stock
SELECT stock FROM producto WHERE id_producto = 5;      -- p.ej. 40
INSERT INTO detalle (numero_factura, id_producto, cantidad, precio_unitario, subtotal_producto)
VALUES (1, 5, 3, 1000, 0);                             -- el subtotal se recalcula solo
SELECT stock FROM producto WHERE id_producto = 5;      -- 37

-- Y lo devuelve al anular
DELETE FROM detalle WHERE id_detalle = LAST_INSERT_ID();
SELECT stock FROM producto WHERE id_producto = 5;      -- 40 otra vez

-- El trigger bloquea lo imposible
UPDATE producto SET precio = 0 WHERE id_producto = 5;
-- ERROR 1644: El precio del producto debe ser mayor que cero.

-- Y la auditoría lo registró todo
SELECT * FROM auditoria_producto WHERE id_producto = 5 ORDER BY fecha DESC;
```

Listado de todo lo creado:

```sql
SHOW FULL TABLES IN bandp WHERE table_type = 'VIEW';
SHOW TRIGGERS FROM bandp;
SHOW PROCEDURE STATUS WHERE db = 'bandp';
SHOW FUNCTION STATUS WHERE db = 'bandp';
```
