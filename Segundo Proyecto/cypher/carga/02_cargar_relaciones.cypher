
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 02_cargar_relaciones.cypher
// Objetivo: Cargar las 14303 relaciones desde CSV.
// Compatible con Neo4j 5.26.
//
// REQUISITO PREVIO:
// Ejecutar la preparacion de la visita original
// y tener los 865 nodos correctamente cargados.
//
// Ejecutar cada bloque por separado.
// Las cargas utilizan transacciones de 500 filas.
//

// ================================================
// 1. AMISTADES - ES_AMIGO_DE
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///amistades.csv' AS row
CALL (row) {
    MATCH (u1:Usuario {id: toInteger(row.id_usuario1)})
    MATCH (u2:Usuario {id: toInteger(row.id_usuario2)})
    MERGE (u1)-[a:ES_AMIGO_DE]->(u2)
    SET a.fecha_amistad = date(row.fecha_amistad)
} IN TRANSACTIONS OF 500 ROWS;


// ================================================
// 2. RESTAURANTE - PERTENECE_A
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///pertenencias.csv' AS row
CALL (row) {
    MATCH (r:Restaurante {id: toInteger(row.id_restaurante)})
    MATCH (t:TipoCocina {id: toInteger(row.id_cocina)})
    MERGE (r)-[:PERTENECE_A]->(t)
} IN TRANSACTIONS OF 500 ROWS;


// ================================================
// 3. RESTAURANTE - OFRECE
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///ofertas.csv' AS row
CALL (row) {
    MATCH (r:Restaurante {id: toInteger(row.id_restaurante)})
    MATCH (p:Platillo {id: toInteger(row.id_platillo)})
    MERGE (r)-[o:OFRECE]->(p)
    SET o.precio = toFloat(row.precio),
        o.disponible = (row.disponible = 'true')
} IN TRANSACTIONS OF 500 ROWS;


// ================================================
// 4. CHEF - PREPARA
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///preparaciones.csv' AS row
CALL (row) {
    MATCH (c:Chef {id: toInteger(row.id_chef)})
    MATCH (p:Platillo {id: toInteger(row.id_platillo)})
    MERGE (c)-[pr:PREPARA]->(p)
    SET pr.estilo = row.estilo,
        pr.especialidad = row.especialidad
} IN TRANSACTIONS OF 500 ROWS;


// ================================================
// 5. CHEF - TRABAJA_EN
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///trabajos.csv' AS row
CALL (row) {
    MATCH (c:Chef {id: toInteger(row.id_chef)})
    MATCH (r:Restaurante {id: toInteger(row.id_restaurante)})
    MERGE (c)-[tr:TRABAJA_EN]->(r)
    SET tr.fecha_inicio = date(row.fecha_inicio),
        tr.puesto = row.puesto
} IN TRANSACTIONS OF 500 ROWS;


// ================================================
// 6. USUARIO - LE_GUSTA
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///gustos.csv' AS row
CALL (row) {
    MATCH (u:Usuario {id: toInteger(row.id_usuario)})
    MATCH (t:TipoCocina {id: toInteger(row.id_cocina)})
    MERGE (u)-[g:LE_GUSTA]->(t)
    SET g.nivel_interes = toInteger(row.nivel_interes)
} IN TRANSACTIONS OF 500 ROWS;


// ================================================
// 7. USUARIO - CALIFICO
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///calificaciones.csv' AS row
CALL (row) {
    MATCH (u:Usuario {id: toInteger(row.id_usuario)})
    MATCH (r:Restaurante {id: toInteger(row.id_restaurante)})
    MERGE (u)-[c:`CALIFICÓ`]->(r)
    SET c.puntuacion = toInteger(row.puntuacion),
        c.fecha = date(row.fecha),
        c.comentario = row.comentario
} IN TRANSACTIONS OF 500 ROWS;


// ================================================
// 8. USUARIO - VISITO
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///visitas.csv' AS row
CALL (row) {
    MATCH (u:Usuario {id: toInteger(row.id_usuario)})
    MATCH (r:Restaurante {id: toInteger(row.id_restaurante)})
    MERGE (u)-[v:`VISITÓ` {
        id_visita: toInteger(row.id_visita)
    }]->(r)
    SET v.fecha_visita = date(row.fecha_visita),
        v.consumo = toFloat(row.consumo),
        v.con_reserva = (row.con_reserva = 'true')
} IN TRANSACTIONS OF 500 ROWS;
