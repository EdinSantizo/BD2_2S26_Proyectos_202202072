-- ============================================================
-- Proyecto 1 - Sistemas de Bases de Datos 2
-- Sistema de Gestión de Reservas y Boletos Aéreos
-- Keyspace Apache Cassandra
-- ============================================================

CREATE KEYSPACE IF NOT EXISTS aerolinea
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
}
AND durable_writes = true;