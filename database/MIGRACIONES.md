# Migraciones de la base de datos `bandp`

Cada cambio que se le hizo al esquema original vive en su propio archivo
`.sql` dentro de esta carpeta. Esta tabla dice qué hace cada uno y cuándo
hay que ejecutarlo, para no tener que abrirlos uno por uno ni adivinar si
ya se aplicó.

> **¿Base nueva?** No necesitas nada de esto. `python database/init_db.py`
> ejecuta `schema.sql` + `seed.sql` + `objetos.sql`, y esos tres archivos
> ya incluyen todos los cambios de la tabla de abajo. Las migraciones son
> solo para una base `bandp` **que ya existía** de un sprint anterior.

> **Ojo con `init_db.py`:** desde el Sprint 5 **borra la base y la vuelve a
> crear** (pregunta antes, salvo con `--forzar`). Esa es la diferencia con
> una migración: `init_db.py` deja la base como los tres archivos dicen y se
> lleva por delante los datos; una migración cambia el esquema y **conserva
> lo que haya**. Si tienes datos propios, migra; si solo tienes los de
> ejemplo, reconstruir es más simple y más seguro.

## Migraciones aplicadas

| # | Archivo | Sprint | Qué hace | Aplicada |
|---|---|---|---|---|
| 1 | `migracion_imagen_producto.sql` | Sprint 3 | Crea la tabla `imagen_producto` (varias fotos por producto) y retira la columna `producto.imagen_url`, que solo permitía una. | Sprint 3 |
| 2 | `migracion_empleado_activo.sql` | Sprint 3 | Agrega `empleado.activo` para quitarle el acceso al panel a alguien sin borrar su cuenta (sus facturas son histórico contable). | Sprint 3 |
| 3 | `migracion_utf8mb4.sql` | Sprint 4 | Convierte toda la base de `latin1` a `utf8mb4`. Corrige el desajuste con la conexión de la app, que ya pedía `utf8mb4`, y que dañaba las tildes y la «ñ». | 01/09/2026 |
| 4 | `migracion_producto_autoincrement.sql` | Sprint 4 | Devuelve el `AUTO_INCREMENT` a `producto.id_producto` y crea el índice `FULLTEXT` del buscador del catálogo. | 01/09/2026 |
| 5 | `migracion_codigo_recuperacion.sql` | Sprint 5 | Crea la tabla `codigo_recuperacion`: guarda el código de un solo uso que se envía por correo para restablecer una contraseña olvidada (solo el hash, con vencimiento e intentos). | 22/10/2026 |

### Resultado de aplicarlas (01/09/2026, MariaDB 10.4.32)

| Comprobación | Antes | Después |
|---|---|---|
| Tablas en `latin1` | 18 | 0 |
| `María` en bytes | `4D6172·ED·61` (latin1) | `4D6172·C3AD·61` (UTF-8) |
| `producto.id_producto` | sin `AUTO_INCREMENT` | `auto_increment`, contador en 111 |
| Índice del buscador | ninguno | `ft_producto_busqueda` (FULLTEXT) |
| `EXPLAIN` de una búsqueda | recorría la tabla | `type: fulltext` |
| Contraseñas en texto plano | 215 | 0 |

### Nota: las llaves foráneas de texto

La conversión a `utf8mb4` falla de entrada con:

```
ERROR 1832: Cannot change column 'id_usuario':
            used in a foreign key constraint 'carrito_ibfk_1'
```

Las dos puntas de una llave foránea deben compartir juego de caracteres, y
al convertir las tablas de a una dejan de coincidir. **`SET FOREIGN_KEY_CHECKS = 0`
no sirve**: MariaDB rechaza el cambio igual. Hay que quitar la restricción,
convertir y volver a ponerla — que es lo que hace el archivo.

Solo aplica a dos restricciones de todo el esquema (`carrito_ibfk_1` y
`factura_ibfk_1`, ambas sobre `id_usuario VARCHAR(11)`). Las demás son sobre
columnas `INT`, y un entero no tiene juego de caracteres. Esta consulta las
lista:

```sql
SELECT k.CONSTRAINT_NAME, k.TABLE_NAME, k.COLUMN_NAME
  FROM information_schema.KEY_COLUMN_USAGE k
  JOIN information_schema.COLUMNS c
    ON c.TABLE_SCHEMA = k.TABLE_SCHEMA
   AND c.TABLE_NAME   = k.TABLE_NAME
   AND c.COLUMN_NAME  = k.COLUMN_NAME
 WHERE k.TABLE_SCHEMA = 'bandp'
   AND k.REFERENCED_TABLE_NAME IS NOT NULL
   AND c.CHARACTER_SET_NAME IS NOT NULL;
```

## Cómo aplicar una migración

```bash
mysql -u root -p bandp < database/migracion_utf8mb4.sql
```

O desde phpMyAdmin: pestaña **SQL** → pegar el contenido del archivo →
**Continuar**.

> Antes de cualquier migración que toque datos, haz una copia:
> `mysqldump -u root -p bandp > respaldo_bandp.sql`

## Cómo saber si ya está aplicada

| Migración | Comprobación | Resultado esperado |
|---|---|---|
| `imagen_producto` | `SHOW TABLES LIKE 'imagen_producto';` | Devuelve una fila |
| `empleado_activo` | `SHOW COLUMNS FROM empleado LIKE 'activo';` | Devuelve una fila |
| `utf8mb4` | `SELECT table_name, table_collation FROM information_schema.tables WHERE table_schema='bandp' AND table_collation NOT LIKE 'utf8mb4%';` | **Ninguna fila** |
| `producto_autoincrement` | `SHOW CREATE TABLE producto;` | Se ve `AUTO_INCREMENT` en `id_producto` y `FULLTEXT KEY ft_producto_busqueda` |
| `codigo_recuperacion` | `SHOW TABLES LIKE 'codigo_recuperacion';` | Devuelve una fila |

## Nota sobre el orden

Las cinco son independientes entre sí y se pueden ejecutar en cualquier
orden. Todas son **idempotentes**: correrlas dos veces no rompe nada (la
segunda vez, o no encuentran nada que cambiar, o avisan con un error de
«ya existe» que se puede ignorar).

> La #5 es la única que `verificar.py` revisa por su cuenta: si falta la
> tabla `codigo_recuperacion`, avisa al arrancar y dice qué comando correr.
> Es un **aviso** y no un fallo: sin esa tabla la tienda funciona completa,
> lo único que no anda es «¿Olvidaste tu contraseña?».

## Contraseñas

`migrar_contrasenas.py` no es una migración de esquema —no cambia ninguna
tabla— pero se ejecuta una sola vez igual que las de arriba. Cifra las
contraseñas que los datos semilla dejaron en texto plano:

```bash
python database/migrar_contrasenas.py            # muestra qué haría
python database/migrar_contrasenas.py --aplicar  # lo hace
```

Nadie tiene que cambiar su contraseña: quien entraba con `123456` sigue
entrando con `123456`, pero la base ya no la guarda a la vista.
