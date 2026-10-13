
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 01_recomendacion_social.cypher
//
// CONSULTA 1: RECOMENDACION SOCIAL
//
// Objetivo:
// Recomendar restaurantes calificados con 4 o 5
// estrellas por amigos de hasta 3 grados.
//
// Reglas:
// 1. Considerar amistades directas e indirectas.
// 2. No contar dos veces al mismo amigo.
// 3. Excluir restaurantes ya visitados.
// 4. Ordenar por cantidad de amigos coincidentes.
// 5. Desempatar por calificacion promedio.
//
// Usuario de prueba: Juan Perez (ID 1)
//

MATCH (u:Usuario {id: 1})

// Buscar amigos hasta 3 grados de separacion.
// La amistad se recorre en ambas direcciones.
MATCH camino = (u)-[:ES_AMIGO_DE*1..3]-(amigo:Usuario)

WHERE amigo <> u

// Cada amigo se considera una sola vez,
// aunque existan multiples caminos.
WITH u, amigo, min(length(camino)) AS grado

// Obtener restaurantes calificados por amigos.
MATCH (amigo)-[c:`CALIFICÓ`]->(r:Restaurante)

// Considerar solamente calificaciones altas.
// Excluir restaurantes visitados por el usuario.
WHERE c.puntuacion >= 4
  AND NOT EXISTS {
      MATCH (u)-[:`VISITÓ`]->(r)
  }

// Agrupar primero por amigo y restaurante.
// Evitar que varias calificaciones del mismo
// amigo distorsionen el ranking.
WITH r, amigo, grado,
     avg(c.puntuacion) AS promedio_amigo

// Calcular coincidencias y promedio general.
WITH r,
     count(amigo) AS amigos_coincidentes,
     avg(promedio_amigo) AS promedio_calificacion,
     collect({
         id: amigo.id,
         nombre: amigo.nombre,
         grado: grado
     }) AS amigos_que_recomiendan

// Mostrar las recomendaciones.
RETURN
    r.id AS id_restaurante,
    r.nombre AS restaurante,
    amigos_coincidentes,
    round(promedio_calificacion, 2) AS calificacion_promedio,
    amigos_que_recomiendan

ORDER BY
    amigos_coincidentes DESC,
    calificacion_promedio DESC,
    restaurante ASC

LIMIT 10;
