
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 02_restaurantes_conectados.cypher
//
// ANALISIS 2: RESTAURANTES ALTAMENTE CONECTADOS
//
// Objetivo:
// Identificar restaurantes con mayor numero
// de chefs y platillos destacados.
//
// Definicion de platillo destacado:
// - Preparado por al menos un chef.
// - Ofrecido en 3 o mas restaurantes.
//
// Puntuacion de conectividad:
// total_chefs + total_platillos_destacados
//
// Compatible con Neo4j 5.26.19
//

// ================================================
// 1. OBTENER RESTAURANTES
// ================================================

MATCH (r:Restaurante)

// ================================================
// 2. CONTAR CHEFS VINCULADOS
// ================================================

CALL (r) {

    MATCH (c:Chef)-[:TRABAJA_EN]->(r)

    RETURN count(DISTINCT c) AS total_chefs
}

// ================================================
// 3. CONTAR PLATILLOS OFRECIDOS
// ================================================

CALL (r) {

    MATCH (r)-[:OFRECE]->(p:Platillo)

    RETURN count(DISTINCT p)
           AS total_platillos
}

// ================================================
// 4. CONTAR PLATILLOS DESTACADOS
// ================================================

CALL (r) {

    MATCH (r)-[:OFRECE]->(p:Platillo)

    // El platillo debe ser preparado
    // por al menos un chef.

    WHERE EXISTS {
        MATCH (:Chef)-[:PREPARA]->(p)
    }

    // Contar los restaurantes diferentes
    // que ofrecen el mismo platillo.

    MATCH (otro:Restaurante)-[:OFRECE]->(p)

    WITH p,
         count(DISTINCT otro)
         AS restaurantes_que_lo_ofrecen

    WHERE restaurantes_que_lo_ofrecen >= 3

    RETURN count(DISTINCT p)
           AS total_platillos_destacados
}

// ================================================
// 5. CALCULAR CONECTIVIDAD
// ================================================

WITH r,
     total_chefs,
     total_platillos,
     total_platillos_destacados,
     total_chefs + total_platillos_destacados
         AS puntaje_conectividad

// ================================================
// 6. MOSTRAR RANKING
// ================================================

RETURN
    r.id AS id_restaurante,
    r.nombre AS restaurante,

    total_chefs,

    total_platillos,

    total_platillos_destacados,

    puntaje_conectividad

ORDER BY
    puntaje_conectividad DESC,
    total_chefs DESC,
    total_platillos_destacados DESC,
    id_restaurante ASC

LIMIT 20;
