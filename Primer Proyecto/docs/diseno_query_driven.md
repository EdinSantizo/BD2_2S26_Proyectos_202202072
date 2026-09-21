# Diseño Query-Driven para Apache Cassandra

## Consulta 1 - Disponibilidad de asientos por clase

### Requerimiento

Para un vuelo específico, obtener la cantidad de asientos disponibles y ocupados, desglosados por clase: económica, ejecutiva y primera clase.

### Tabla especializada

`disponibilidad_asientos_por_vuelo_clase`

### Estructura

| Campo | Tipo | Función |
|---|---|---|
| vuelo_id | uuid | Partition Key |
| clase | text | Clustering Key |
| disponibles | counter | Contador de asientos disponibles |
| ocupados | counter | Contador de asientos ocupados |

### Primary Key

```sql
PRIMARY KEY ((vuelo_id), clase)
```

### Justificación de la Partition Key

`vuelo_id` se utiliza como Partition Key debido a que la consulta parte de un vuelo específico. Esto permite almacenar en una misma partición los contadores de todas las clases correspondientes al vuelo y acceder directamente a ellos sin realizar filtrado.

### Justificación de la Clustering Key

`clase` se utiliza como Clustering Key para mantener una fila independiente para cada clase de asiento dentro de la partición del vuelo.

Los valores utilizados serán:

- economica
- ejecutiva
- primera

### Estrategia de agregación

La consulta utiliza columnas de tipo `counter`.

Cuando se confirma una reserva:

```text
disponibles = disponibles - 1
ocupados = ocupados + 1
```

Cuando se cancela una reserva:

```text
disponibles = disponibles + 1
ocupados = ocupados - 1
```

De esta manera no es necesario contar las reservas en tiempo de consulta.

### CQL propuesto

```sql
CREATE TABLE disponibilidad_asientos_por_vuelo_clase (
    vuelo_id uuid,
    clase text,
    disponibles counter,
    ocupados counter,
    PRIMARY KEY ((vuelo_id), clase)
);
```

### Consulta soportada

```sql
SELECT clase, disponibles, ocupados
FROM disponibilidad_asientos_por_vuelo_clase
WHERE vuelo_id = ?;
```

Esta tabla permite responder la consulta directamente mediante la clave de partición, sin utilizar JOIN ni ALLOW FILTERING.


---

## Consulta 2 - Historial cronológico de un pasajero

### Requerimiento

Dado un pasajero y un rango de fechas, obtener sus vuelos y reservas ordenados cronológicamente, incluyendo el estado del pago correspondiente.

### Tabla especializada

`historial_reservas_por_pasajero`

### Estructura

| Campo | Tipo | Función |
|---|---|---|
| pasajero_id | uuid | Partition Key |
| fecha_salida | timestamp | Clustering Key |
| reserva_id | uuid | Clustering Key |
| codigo_vuelo | text | Código del vuelo |
| aeropuerto_origen | text | Aeropuerto de origen |
| aeropuerto_destino | text | Aeropuerto de destino |
| fecha_reserva | timestamp | Fecha de creación de la reserva |
| numero_asiento | text | Número de asiento |
| clase | text | Clase del asiento |
| estado_reserva | text | Estado de la reserva |
| estado_pago | text | Estado del pago |
| monto_pago | decimal | Monto asociado al pago |

### Primary Key

```sql
PRIMARY KEY ((pasajero_id), fecha_salida, reserva_id)
```

### Justificación de la Partition Key

`pasajero_id` se utiliza como Partition Key porque la consulta siempre parte de un pasajero específico. De esta manera, todo el historial correspondiente al pasajero se encuentra agrupado dentro de una misma partición.

### Justificación de las Clustering Keys

`fecha_salida` se utiliza como primera Clustering Key para permitir búsquedas mediante rangos de fechas y mantener las reservas ordenadas cronológicamente.

`reserva_id` se utiliza como segunda Clustering Key para garantizar unicidad cuando existen varias reservas con la misma fecha y hora de salida.

### Decisión sobre la fecha utilizada

El requerimiento menciona un rango de fechas sin indicar explícitamente si corresponde a la fecha de creación de la reserva o a la fecha del vuelo.

Se utilizará `fecha_salida` debido a que la consulta representa el historial cronológico de vuelos del pasajero. La `fecha_reserva` también se almacenará como información adicional de la fila.

### Denormalización

La tabla almacena conjuntamente información proveniente conceptualmente de reservas, vuelos, asientos y pagos.

Esto permite consultar el historial completo mediante una sola tabla sin utilizar JOIN.

### CQL propuesto

```sql
CREATE TABLE historial_reservas_por_pasajero (
    pasajero_id uuid,
    fecha_salida timestamp,
    reserva_id uuid,
    codigo_vuelo text,
    aeropuerto_origen text,
    aeropuerto_destino text,
    fecha_reserva timestamp,
    numero_asiento text,
    clase text,
    estado_reserva text,
    estado_pago text,
    monto_pago decimal,
    PRIMARY KEY ((pasajero_id), fecha_salida, reserva_id)
) WITH CLUSTERING ORDER BY (fecha_salida DESC);
```

### Consulta soportada

```sql
SELECT
    fecha_salida,
    codigo_vuelo,
    aeropuerto_origen,
    aeropuerto_destino,
    numero_asiento,
    clase,
    estado_reserva,
    estado_pago,
    monto_pago
FROM historial_reservas_por_pasajero
WHERE pasajero_id = ?
  AND fecha_salida >= ?
  AND fecha_salida <= ?
ORDER BY fecha_salida DESC;
```

Esta consulta puede ejecutarse utilizando directamente la Partition Key y un rango sobre la Clustering Key, sin JOIN y sin ALLOW FILTERING.


---

## Consulta 3 - Manifiesto de vuelo ordenado y enriquecido

### Requerimiento

Para un vuelo específico, obtener el listado de pasajeros ordenado por número de asiento, incluyendo la clase del asiento, el estado de la reserva y el estado del pago en una sola consulta.

### Tabla especializada

`manifiesto_por_vuelo`

### Estructura

| Campo | Tipo | Función |
|---|---|---|
| vuelo_id | uuid | Partition Key |
| fila_asiento | int | Clustering Key |
| letra_asiento | text | Clustering Key |
| numero_asiento | text | Número completo del asiento |
| reserva_id | uuid | Identificador de la reserva |
| pasajero_id | uuid | Identificador del pasajero |
| nombre_pasajero | text | Nombre del pasajero |
| documento_identificacion | text | DPI o pasaporte del pasajero |
| clase | text | Clase del asiento |
| estado_reserva | text | Estado de la reserva |
| estado_pago | text | Estado del pago |

### Primary Key

```sql
PRIMARY KEY ((vuelo_id), fila_asiento, letra_asiento)
```

### Justificación de la Partition Key

`vuelo_id` se utiliza como Partition Key debido a que la consulta siempre solicita el manifiesto correspondiente a un vuelo específico.

Esto permite almacenar dentro de una misma partición todos los pasajeros y asientos correspondientes al vuelo.

### Justificación de las Clustering Keys

`fila_asiento` y `letra_asiento` permiten mantener los registros ordenados naturalmente por número de asiento.

Se evita utilizar únicamente `numero_asiento` de tipo `text` como Clustering Key porque un orden lexicográfico podría producir secuencias incorrectas como 1A, 10A, 11A, 2A.

Separando el número de fila y la letra se obtiene un orden natural:

```text
1A
1B
1C
2A
2B
2C
10A
10B
10C
```

### Denormalización

La tabla contiene información que conceptualmente pertenece a las entidades Asiento, Reserva, Pasajero y Pago.

Los datos se almacenan conjuntamente para permitir obtener el manifiesto enriquecido mediante una única consulta, sin necesidad de JOIN.

### CQL propuesto

```sql
CREATE TABLE manifiesto_por_vuelo (
    vuelo_id uuid,
    fila_asiento int,
    letra_asiento text,
    numero_asiento text,
    reserva_id uuid,
    pasajero_id uuid,
    nombre_pasajero text,
    documento_identificacion text,
    clase text,
    estado_reserva text,
    estado_pago text,
    PRIMARY KEY ((vuelo_id), fila_asiento, letra_asiento)
) WITH CLUSTERING ORDER BY (
    fila_asiento ASC,
    letra_asiento ASC
);
```

### Consulta soportada

```sql
SELECT
    numero_asiento,
    nombre_pasajero,
    documento_identificacion,
    clase,
    estado_reserva,
    estado_pago
FROM manifiesto_por_vuelo
WHERE vuelo_id = ?;
```

La consulta accede directamente a la partición correspondiente al vuelo y retorna el manifiesto ordenado por asiento sin utilizar JOIN ni ALLOW FILTERING.


---

## Consulta 4 - Porcentaje de ocupación por ruta y rango de fechas

### Requerimiento

Para una ruta específica, definida por aeropuerto de origen y aeropuerto de destino, obtener la ocupación de cada vuelo dentro de un rango de fechas.

La ocupación se determina utilizando la cantidad de reservas confirmadas y la capacidad total de la aeronave asignada al vuelo.

### Tabla especializada

`ocupacion_por_ruta_mes`

### Estructura

| Campo | Tipo | Función |
|---|---|---|
| origen | text | Partition Key |
| destino | text | Partition Key |
| anio_mes | text | Partition Key y bucket temporal |
| fecha_salida | timestamp | Clustering Key |
| vuelo_id | uuid | Clustering Key |
| reservas_confirmadas | counter | Cantidad de reservas confirmadas |
| capacidad_total | counter | Capacidad total del vuelo |

### Primary Key

```sql
PRIMARY KEY (
    (origen, destino, anio_mes),
    fecha_salida,
    vuelo_id
)
```

### Justificación de la Partition Key

La Partition Key está formada por `origen`, `destino` y `anio_mes`.

`origen` y `destino` identifican la ruta que se desea consultar.

`anio_mes` funciona como bucket temporal y evita almacenar todos los vuelos históricos de una ruta dentro de una única partición de tamaño creciente.

Ejemplos de particiones:

```text
GUA | MIA | 2026-08
GUA | MIA | 2026-09
GUA | MIA | 2026-10
```

### Justificación de las Clustering Keys

`fecha_salida` permite ordenar los vuelos cronológicamente dentro del bucket y ejecutar consultas mediante rangos de fechas.

`vuelo_id` garantiza la unicidad de los vuelos en caso de que existan vuelos con la misma fecha y hora de salida.

### Estrategia de agregación

La tabla mantiene previamente los valores necesarios para determinar la ocupación del vuelo.

`reservas_confirmadas` se actualiza cuando una reserva cambia a estado confirmado o deja de estar confirmada.

`capacidad_total` representa la capacidad máxima de la aeronave asignada al vuelo.

Debido a las restricciones de las tablas de contadores de Cassandra, ambos valores se mantienen como columnas de tipo `counter`.

Cuando se crea el vuelo se inicializa su capacidad.

Cuando se confirma una reserva:

```text
reservas_confirmadas = reservas_confirmadas + 1
```

Cuando se cancela una reserva previamente confirmada:

```text
reservas_confirmadas = reservas_confirmadas - 1
```

El porcentaje de ocupación corresponde a:

```text
(reservas_confirmadas / capacidad_total) * 100
```

Los valores utilizados para el porcentaje ya se encuentran preagregados en Cassandra, por lo que no es necesario recorrer ni contar las reservas en el cliente.

### Bucketing temporal

La información se divide por mes mediante `anio_mes`.

Si el rango solicitado incluye varios meses, se consulta cada bucket mensual involucrado de forma independiente.

Esto evita particiones excesivamente grandes y mantiene las consultas dirigidas a particiones conocidas.

### CQL propuesto

```sql
CREATE TABLE ocupacion_por_ruta_mes (
    origen text,
    destino text,
    anio_mes text,
    fecha_salida timestamp,
    vuelo_id uuid,
    reservas_confirmadas counter,
    capacidad_total counter,
    PRIMARY KEY (
        (origen, destino, anio_mes),
        fecha_salida,
        vuelo_id
    )
) WITH CLUSTERING ORDER BY (
    fecha_salida ASC,
    vuelo_id ASC
);
```

### Consulta soportada

```sql
SELECT
    fecha_salida,
    vuelo_id,
    reservas_confirmadas,
    capacidad_total
FROM ocupacion_por_ruta_mes
WHERE origen = ?
  AND destino = ?
  AND anio_mes = ?
  AND fecha_salida >= ?
  AND fecha_salida <= ?;
```

La consulta utiliza una Partition Key conocida y aplica el rango únicamente sobre la Clustering Key temporal, por lo que no requiere JOIN ni ALLOW FILTERING.


---

## Consulta 5 - Top N de vuelos por ingresos generados

### Requerimiento

Obtener los N vuelos con mayor ingreso generado dentro de un período de fechas, ordenados de mayor a menor ingreso.

El ranking debe resolverse utilizando una tabla de agregación y no mediante el cálculo y ordenamiento de todos los pagos en el cliente.

### Tabla especializada

`ranking_ingresos_por_periodo`

### Estructura

| Campo | Tipo | Función |
|---|---|---|
| fecha_inicio | date | Partition Key |
| fecha_fin | date | Partition Key |
| ingreso_total | decimal | Clustering Key DESC |
| vuelo_id | uuid | Clustering Key |
| codigo_vuelo | text | Código del vuelo |
| fecha_salida | timestamp | Fecha y hora del vuelo |
| origen | text | Aeropuerto de origen |
| destino | text | Aeropuerto de destino |

### Primary Key

```sql
PRIMARY KEY (
    (fecha_inicio, fecha_fin),
    ingreso_total,
    vuelo_id
)
```

### Justificación de la Partition Key

`fecha_inicio` y `fecha_fin` forman una Partition Key compuesta que identifica el período materializado para el cual se construye el ranking.

Todos los vuelos pertenecientes al ranking de dicho período se almacenan dentro de una misma partición.

Esto permite recuperar directamente los primeros N registros de la partición.

### Justificación de las Clustering Keys

`ingreso_total` es la primera Clustering Key y se define en orden descendente.

De esta forma, los vuelos con mayores ingresos se almacenan primero dentro de la partición.

`vuelo_id` se utiliza como segunda Clustering Key para garantizar la unicidad cuando dos o más vuelos poseen el mismo ingreso total.

### Estrategia de agregación

El ingreso total de cada vuelo se mantiene previamente agregado a partir de sus pagos confirmados.

La consulta Top N no recorre los pagos ni calcula el ingreso en tiempo de consulta.

La tabla representa una materialización del ranking correspondiente a un período de reporte.

Si el ingreso acumulado de un vuelo cambia, la posición anterior debe sustituirse por una nueva fila correspondiente al nuevo ingreso.

### Períodos materializados

Para permitir el ordenamiento eficiente por ingresos, el ranking se construye por períodos de reporte conocidos.

Por ejemplo:

```text
2026-09-01 → 2026-09-30
2026-10-01 → 2026-10-31
```

Durante la carga de datos se generarán los períodos utilizados en las pruebas del sistema.

### CQL propuesto

```sql
CREATE TABLE ranking_ingresos_por_periodo (
    fecha_inicio date,
    fecha_fin date,
    ingreso_total decimal,
    vuelo_id uuid,
    codigo_vuelo text,
    fecha_salida timestamp,
    origen text,
    destino text,
    PRIMARY KEY (
        (fecha_inicio, fecha_fin),
        ingreso_total,
        vuelo_id
    )
) WITH CLUSTERING ORDER BY (
    ingreso_total DESC,
    vuelo_id ASC
);
```

### Consulta soportada

```sql
SELECT
    codigo_vuelo,
    fecha_salida,
    origen,
    destino,
    ingreso_total
FROM ranking_ingresos_por_periodo
WHERE fecha_inicio = ?
  AND fecha_fin = ?
LIMIT ?;
```

La tabla almacena los vuelos ordenados por ingreso dentro del período, permitiendo resolver el Top N directamente mediante `LIMIT` sin JOIN, sin ALLOW FILTERING y sin ordenar los resultados en el cliente.

