-- ============================================================
-- Proyecto 1 - Sistemas de Bases de Datos 2
-- Sistema de Gestión de Reservas y Boletos Aéreos
-- Esquema Cassandra
-- ============================================================

USE aerolinea;

-- ============================================================
-- TABLAS BASE OPERATIVAS
-- ============================================================

-- ------------------------------------------------------------
-- PASAJEROS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pasajeros_por_id (
    pasajero_id uuid PRIMARY KEY,
    nombre text,
    email text,
    documento_identificacion text,
    telefono text,
    nacionalidad text
);


-- ------------------------------------------------------------
-- AERONAVES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS aeronaves_por_id (
    aeronave_id uuid PRIMARY KEY,
    modelo text,
    aerolinea_operadora text,
    matricula text,
    capacidad_maxima int
);


-- ------------------------------------------------------------
-- VUELOS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS vuelos_por_id (
    vuelo_id uuid PRIMARY KEY,
    codigo_vuelo text,
    aeronave_id uuid,
    aeropuerto_origen text,
    aeropuerto_destino text,
    fecha_hora_salida timestamp,
    fecha_hora_llegada timestamp,
    estado text
);


-- ------------------------------------------------------------
-- ASIENTOS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS asientos_por_vuelo (
    vuelo_id uuid,
    numero_asiento text,
    asiento_id uuid,
    fila_asiento int,
    letra_asiento text,
    clase text,
    estado text,
    PRIMARY KEY ((vuelo_id), numero_asiento)
);


-- ------------------------------------------------------------
-- RESERVAS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS reservas_por_id (
    reserva_id uuid PRIMARY KEY,
    pasajero_id uuid,
    vuelo_id uuid,
    numero_asiento text,
    fecha_reserva timestamp,
    estado text
);


-- ------------------------------------------------------------
-- PAGOS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pagos_por_reserva (
    reserva_id uuid PRIMARY KEY,
    pago_id uuid,
    monto decimal,
    metodo_pago text,
    fecha_pago timestamp,
    estado text
);


-- ============================================================
-- TABLAS QUERY-DRIVEN
-- ============================================================


-- ============================================================
-- Q1
-- DISPONIBILIDAD DE ASIENTOS POR CLASE
-- ============================================================

CREATE TABLE IF NOT EXISTS disponibilidad_asientos_por_vuelo_clase (
    vuelo_id uuid,
    clase text,
    disponibles counter,
    ocupados counter,
    PRIMARY KEY ((vuelo_id), clase)
);


-- ============================================================
-- Q2
-- HISTORIAL CRONOLOGICO DE UN PASAJERO
-- ============================================================

CREATE TABLE IF NOT EXISTS historial_reservas_por_pasajero (
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
)
WITH CLUSTERING ORDER BY (
    fecha_salida DESC,
    reserva_id ASC
);


-- ============================================================
-- Q3
-- MANIFIESTO DE VUELO ORDENADO POR ASIENTO
-- ============================================================

CREATE TABLE IF NOT EXISTS manifiesto_por_vuelo (
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
)
WITH CLUSTERING ORDER BY (
    fila_asiento ASC,
    letra_asiento ASC
);


-- ============================================================
-- Q4
-- OCUPACION POR RUTA Y BUCKET MENSUAL
-- ============================================================

CREATE TABLE IF NOT EXISTS ocupacion_por_ruta_mes (
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
)
WITH CLUSTERING ORDER BY (
    fecha_salida ASC,
    vuelo_id ASC
);


-- ============================================================
-- Q5
-- TOP N DE VUELOS POR INGRESOS
-- ============================================================

CREATE TABLE IF NOT EXISTS ranking_ingresos_por_periodo (
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
)
WITH CLUSTERING ORDER BY (
    ingreso_total DESC,
    vuelo_id ASC
);