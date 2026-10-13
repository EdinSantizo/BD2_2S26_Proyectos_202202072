
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 03_restaurantes_infravalorados.cypher
//
// CONSULTA 3: RESTAURANTES INFRAVALORADOS
//
// Condiciones:
// 1. Tasa de reservas mayor al promedio global.
// 2. Calificacion menor al promedio global.
//
// Se calculan las estadisticas por separado
// para evitar multiplicar visitas y calificaciones.
//

// ================================================
// 1. TASA GLOBAL DE RESERVAS
// ================================================

CALL () {
    MATCH (:Usuario)-[v:`VISITÓ`]->(:Restaurante)

    WITH count(v) AS total_visitas,
         sum(
             CASE
                 WHEN v.con_reserva = true THEN 1
                 ELSE 0
             END
         ) AS total_reservas

    RETURN toFloat(total_reservas) / total_visitas
           AS tasa_reserva_global
}

// ================================================
// 2. CALIFICACION GLOBAL
// ================================================

CALL () {
    MATCH (:Usuario)-[c:`CALIFICÓ`]->(:Restaurante)

    RETURN avg(c.puntuacion)
           AS calificacion_global
}

// ================================================
// 3. VISITAS DE CADA RESTAURANTE
// ================================================

MATCH (r:Restaurante)

CALL (r) {
    MATCH (:Usuario)-[v:`VISITÓ`]->(r)

    RETURN count(v) AS total_visitas,
           sum(
               CASE
                   WHEN v.con_reserva = true THEN 1
                   ELSE 0
               END
           ) AS visitas_con_reserva
}

// ================================================
// 4. CALIFICACIONES POR RESTAURANTE
// ================================================

CALL (r) {
    MATCH (:Usuario)-[c:`CALIFICÓ`]->(r)

    RETURN count(c) AS total_calificaciones,
           avg(c.puntuacion) AS calificacion_restaurante
}

// ================================================
// 5. CALCULAR Y COMPARAR INDICADORES
// ================================================

WITH r,
     total_visitas,
     visitas_con_reserva,
     total_calificaciones,
     calificacion_restaurante,
     tasa_reserva_global,
     calificacion_global

WHERE total_visitas > 0
  AND total_calificaciones > 0

WITH r,
     total_visitas,
     visitas_con_reserva,
     calificacion_restaurante,
     tasa_reserva_global,
     calificacion_global,
     toFloat(visitas_con_reserva) / total_visitas
         AS tasa_reserva_restaurante

WHERE tasa_reserva_restaurante > tasa_reserva_global
  AND calificacion_restaurante < calificacion_global

// ================================================
// 6. RESULTADO
// ================================================

RETURN
    r.id AS id_restaurante,
    r.nombre AS restaurante,
    total_visitas,
    visitas_con_reserva,

    round(tasa_reserva_restaurante * 100, 2)
        AS porcentaje_reservas,

    round(tasa_reserva_global * 100, 2)
        AS porcentaje_reservas_global,

    round(calificacion_restaurante, 2)
        AS calificacion_promedio,

    round(calificacion_global, 2)
        AS calificacion_global

ORDER BY
    (tasa_reserva_restaurante - tasa_reserva_global) DESC,
    calificacion_promedio ASC

LIMIT 20;
