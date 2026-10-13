
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 02_chefs_alto_impacto.cypher
//
// CONSULTA 2: CHEFS DE ALTO IMPACTO
//
// Condiciones:
// 1. El chef trabaja en al menos un restaurante
//    con calificacion promedio > 4 estrellas.
// 2. Prepara al menos un platillo ofrecido
//    en 3 o mas restaurantes diferentes.
//
// Los promedios consideran todas las calificaciones.
// Se utiliza COUNT(DISTINCT) para evitar
// contar un mismo restaurante varias veces.
//

// ================================================
// 1. RESTAURANTES DONDE TRABAJA CADA CHEF
// ================================================

MATCH (chef:Chef)-[:TRABAJA_EN]->(rest:Restaurante)

// Obtener todas las calificaciones recibidas.
MATCH (:Usuario)-[cal:`CALIFICÓ`]->(rest)

// Calcular el promedio por restaurante.
WITH chef, rest,
     avg(cal.puntuacion) AS promedio_restaurante

// Solo restaurantes con promedio superior a 4.
WHERE promedio_restaurante > 4

// Agrupar restaurantes destacados de cada chef.
WITH chef,
     collect({
         id: rest.id,
         nombre: rest.nombre,
         promedio: round(promedio_restaurante, 2)
     }) AS restaurantes_destacados

// ================================================
// 2. PLATILLOS PREPARADOS POR LOS CHEFS
// ================================================

MATCH (chef)-[:PREPARA]->(platillo:Platillo)

// Buscar restaurantes que ofrecen cada platillo.
MATCH (ofertante:Restaurante)-[:OFRECE]->(platillo)

// Contar restaurantes distintos por platillo.
WITH chef,
     restaurantes_destacados,
     platillo,
     count(DISTINCT ofertante) AS cantidad_restaurantes

// El platillo debe aparecer en al menos 3.
WHERE cantidad_restaurantes >= 3

// ================================================
// 3. AGRUPAR LOS RESULTADOS
// ================================================

WITH chef,
     restaurantes_destacados,
     collect({
         id: platillo.id,
         nombre: platillo.nombre,
         restaurantes_que_lo_ofrecen: cantidad_restaurantes
     }) AS platillos_destacados

// ================================================
// 4. MOSTRAR CHEFS DE ALTO IMPACTO
// ================================================

RETURN
    chef.id AS id_chef,
    chef.nombre AS chef,
    size(restaurantes_destacados)
        AS restaurantes_bien_calificados,
    size(platillos_destacados)
        AS platillos_en_tres_o_mas_restaurantes,
    restaurantes_destacados,
    platillos_destacados

ORDER BY
    restaurantes_bien_calificados DESC,
    platillos_en_tres_o_mas_restaurantes DESC,
    chef ASC

LIMIT 20;
