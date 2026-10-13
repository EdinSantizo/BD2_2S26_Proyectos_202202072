
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 01_ruta_mas_corta.cypher
//
// ANALISIS 1: RUTA MAS CORTA ENTRE USUARIOS
//
// Objetivo:
// Encontrar el camino mas corto de amistad
// entre dos usuarios de la plataforma.
//
// Se utiliza shortestPath() y la relacion
// ES_AMIGO_DE en ambas direcciones.
//
// Compatible con Neo4j 5.26.19
//

// ================================================
// 1. IDENTIFICAR LOS USUARIOS
// ================================================

// Usuario origen: Juan Perez (ID 1)
// Usuario destino: Valeria Torres (ID 4)

MATCH (origen:Usuario {id: 1})
MATCH (destino:Usuario {id: 4})

// ================================================
// 2. ENCONTRAR EL CAMINO MAS CORTO
// ================================================

// La amistad se recorre en ambas direcciones.
// shortestPath selecciona un camino con
// la menor cantidad de relaciones.

MATCH camino = shortestPath(
    (origen)-[:ES_AMIGO_DE*]-(destino)
)

// ================================================
// 3. PRESENTAR RESULTADOS
// ================================================

RETURN
    origen.id AS id_origen,
    origen.nombre AS usuario_origen,

    destino.id AS id_destino,
    destino.nombre AS usuario_destino,

    length(camino) AS grados_separacion,

    [persona IN nodes(camino) |
        {
            id: persona.id,
            nombre: persona.nombre
        }
    ] AS usuarios_en_camino,

    camino AS ruta_grafo;
