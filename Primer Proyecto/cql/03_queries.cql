-- ============================================================
-- Proyecto 1 - Sistemas de Bases de Datos 2
-- Consultas Query-Driven
-- ============================================================

USE aerolinea;


-- ============================================================
-- Q1
-- Disponibilidad de asientos por clase para un vuelo
--
-- Tabla:
-- disponibilidad_asientos_por_vuelo_clase
--
-- Partition Key:
-- vuelo_id
--
-- No utiliza JOIN.
-- No utiliza ALLOW FILTERING.
-- No realiza COUNT en tiempo de consulta.
-- Los valores disponibles y ocupados son contadores
-- mantenidos durante las operaciones de reserva/cancelacion.
-- ============================================================

SELECT
    clase,
    disponibles,
    ocupados
FROM disponibilidad_asientos_por_vuelo_clase
WHERE vuelo_id = 7738e6e4-6f78-5a6a-9adc-1f33c41fe130;


-- ============================================================
-- Q2
-- Historial cronologico de reservas de un pasajero
-- dentro de un rango de fechas
--
-- Tabla:
-- historial_reservas_por_pasajero
--
-- Partition Key:
-- pasajero_id
--
-- Clustering Columns:
-- fecha_salida DESC
-- reserva_id ASC
--
-- La informacion de vuelo, asiento, reserva y pago se
-- encuentra desnormalizada en la misma tabla.
--
-- No utiliza JOIN.
-- No utiliza ALLOW FILTERING.
-- ============================================================

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
WHERE pasajero_id = af65cd22-ae00-5a4a-8268-45d22029b352
  AND fecha_salida >= '2026-01-10T00:00:00Z'
  AND fecha_salida <= '2026-01-26T23:59:59Z';


-- ============================================================
-- Q3
-- Manifiesto de un vuelo ordenado por numero de asiento
--
-- Tabla:
-- manifiesto_por_vuelo
--
-- Partition Key:
-- vuelo_id
--
-- Clustering Columns:
-- fila_asiento ASC
-- letra_asiento ASC
--
-- La separacion entre fila y letra permite mantener un
-- orden numerico real de los asientos:
-- 1A, 1B, ..., 2A, 2B, ..., 10A, ...
--
-- La informacion del pasajero, clase, reserva y pago
-- se encuentra desnormalizada en la misma tabla.
--
-- No utiliza JOIN.
-- No utiliza ALLOW FILTERING.
-- ============================================================

SELECT
    numero_asiento,
    clase,
    nombre_pasajero,
    documento_identificacion,
    estado_reserva,
    estado_pago
FROM manifiesto_por_vuelo
WHERE vuelo_id = 7738e6e4-6f78-5a6a-9adc-1f33c41fe130;

-- ============================================================
-- Q4
-- Porcentaje de ocupacion por ruta y rango de fechas
--
-- Tabla:
-- ocupacion_por_ruta_mes
--
-- Partition Key:
-- origen + destino + anio_mes
--
-- Clustering Columns:
-- fecha_salida ASC
-- vuelo_id ASC
--
-- Se utilizan agregados previamente mantenidos:
-- reservas_confirmadas y capacidad_total.
--
-- El bucket mensual evita recorrer toda la tabla.
--
-- No utiliza JOIN.
-- No utiliza ALLOW FILTERING.
-- ============================================================

SELECT
    SUM(reservas_confirmadas) AS reservas_confirmadas,
    SUM(capacidad_total) AS capacidad_total,
    (CAST(SUM(reservas_confirmadas) AS decimal) * 100)
        / SUM(capacidad_total) AS porcentaje_ocupacion
FROM ocupacion_por_ruta_mes
WHERE origen = 'GUA'
  AND destino = 'MEX'
  AND anio_mes = '2026-01'
  AND fecha_salida >= '2026-01-01T00:00:00Z'
  AND fecha_salida <= '2026-01-31T23:59:59Z';


-- ============================================================
-- Q5
-- Top N vuelos por ingresos de pagos confirmados
-- dentro de un periodo materializado
--
-- Tabla:
-- ranking_ingresos_por_periodo
--
-- Partition Key:
-- fecha_inicio + fecha_fin
--
-- Clustering Columns:
-- ingreso_total DESC
-- vuelo_id ASC
--
-- Los ingresos se encuentran precalculados por vuelo.
-- Cassandra devuelve directamente los primeros N registros
-- debido al orden de clustering.
--
-- No utiliza JOIN.
-- No utiliza ALLOW FILTERING.
-- No requiere ordenar los resultados en la aplicacion.
-- ============================================================

SELECT
    codigo_vuelo,
    fecha_salida,
    origen,
    destino,
    ingreso_total
FROM ranking_ingresos_por_periodo
WHERE fecha_inicio = '2026-01-01'
  AND fecha_fin = '2026-01-31'
ORDER BY ingreso_total DESC
LIMIT 10;

-- ============================================================
-- TTL
-- Reserva temporal con expiracion automatica
--
-- Cassandra elimina automaticamente la informacion
-- almacenada una vez transcurrido el TTL indicado.
--
-- Ejemplo academico:
-- TTL de 30 segundos para demostrar su funcionamiento.
-- En un escenario real, el TTL se calcularia segun
-- el tiempo permitido para mantener una reserva pendiente.
-- ============================================================

INSERT INTO reservas_por_id (
    reserva_id,
    pasajero_id,
    vuelo_id,
    numero_asiento,
    fecha_reserva,
    estado
)
VALUES (
    99999999-9999-4999-8999-999999999999,
    af65cd22-ae00-5a4a-8268-45d22029b352,
    7738e6e4-6f78-5a6a-9adc-1f33c41fe130,
    'TTL-TEST',
    toTimestamp(now()),
    'EXPIRABLE'
)
USING TTL 30;


-- Consultar el tiempo de vida restante.

SELECT
    reserva_id,
    numero_asiento,
    estado,
    TTL(estado) AS ttl_restante
FROM reservas_por_id
WHERE reserva_id =
    99999999-9999-4999-8999-999999999999;


-- Transcurridos los 30 segundos, esta consulta
-- debe retornar 0 filas.

SELECT *
FROM reservas_por_id
WHERE reserva_id =
    99999999-9999-4999-8999-999999999999;