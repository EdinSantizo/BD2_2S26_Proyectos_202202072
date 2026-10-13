
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 04_precios_vs_consumo.cypher
//
// CONSULTA 4: RANGO DE PRECIOS VS CONSUMO REAL
//
// Objetivo:
// Comparar el consumo promedio registrado en VISITÓ
// contra el consumo esperado del rango de precio.
//
// Valores de referencia de los datos sinteticos:
// bajo  = Q60
// medio = Q120
// alto  = Q240
//
// Se ordena por diferencia absoluta para encontrar
// tanto consumos superiores como inferiores.
//

// ================================================
// 1. OBTENER CONSUMO PROMEDIO REAL
// ================================================

MATCH (r:Restaurante)<-[v:`VISITÓ`]-(:Usuario)

WHERE r.rango_precios IN ['bajo', 'medio', 'alto']

WITH r,
     count(v) AS total_visitas,
     avg(v.consumo) AS consumo_promedio_real

// ================================================
// 2. DETERMINAR CONSUMO ESPERADO
// ================================================

WITH r,
     total_visitas,
     consumo_promedio_real,
     CASE r.rango_precios
         WHEN 'bajo' THEN 60.0
         WHEN 'medio' THEN 120.0
         WHEN 'alto' THEN 240.0
     END AS consumo_esperado

// ================================================
// 3. CALCULAR DIFERENCIAS
// ================================================

WITH r,
     total_visitas,
     consumo_promedio_real,
     consumo_esperado,
     consumo_promedio_real - consumo_esperado
         AS diferencia

// ================================================
// 4. MOSTRAR RESULTADOS
// ================================================

RETURN
    r.id AS id_restaurante,
    r.nombre AS restaurante,
    r.rango_precios AS rango_precios,
    total_visitas,

    consumo_esperado,

    round(consumo_promedio_real, 2)
        AS consumo_promedio_real,

    round(diferencia, 2)
        AS diferencia_quetzales,

    round(abs(diferencia), 2)
        AS diferencia_absoluta,

    round(
        100.0 * diferencia / consumo_esperado,
        2
    ) AS diferencia_porcentual,

    CASE
        WHEN diferencia > 0 THEN 'Mayor al esperado'
        WHEN diferencia < 0 THEN 'Menor al esperado'
        ELSE 'Igual al esperado'
    END AS interpretacion

ORDER BY
    diferencia_absoluta DESC,
    id_restaurante ASC

LIMIT 20;
