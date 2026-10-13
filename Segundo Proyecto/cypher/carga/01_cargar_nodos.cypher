
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Sistema de Recomendacion de Restaurantes
//
// Archivo: 01_cargar_nodos.cypher
// Objetivo: Cargar los 865 nodos desde archivos CSV.
// Motor: Neo4j 5.26
//
// Ejecutar cada bloque LOAD CSV por separado.
// Los archivos deben estar en el directorio import
// de la instancia Neo4j.
//

// ================================================
// 1. CARGAR USUARIOS (500)
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///usuarios.csv' AS row
MERGE (u:Usuario {id: toInteger(row.id)})
SET u.nombre = row.nombre,
    u.email = row.email,
    u.edad = toInteger(row.edad),
    u.pais = row.pais;


// ================================================
// 2. CARGAR RESTAURANTES (200)
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///restaurantes.csv' AS row
MERGE (r:Restaurante {id: toInteger(row.id)})
SET r.nombre = row.nombre,
    r.anio_apertura = toInteger(row.anio_apertura),
    r.rango_precios = row.rango_precios,
    r.descripcion = row.descripcion;


// ================================================
// 3. CARGAR TIPOS DE COCINA (15)
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///tipos_cocina.csv' AS row
MERGE (t:TipoCocina {id: toInteger(row.id)})
SET t.nombre = row.nombre,
    t.descripcion = row.descripcion;


// ================================================
// 4. CARGAR CHEFS (100)
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///chefs.csv' AS row
MERGE (c:Chef {id: toInteger(row.id)})
SET c.nombre = row.nombre,
    c.fecha_nacimiento = date(row.fecha_nacimiento),
    c.nacionalidad = row.nacionalidad;


// ================================================
// 5. CARGAR PLATILLOS (50)
// ================================================

LOAD CSV WITH HEADERS
FROM 'file:///platillos.csv' AS row
MERGE (p:Platillo {id: toInteger(row.id)})
SET p.nombre = row.nombre,
    p.precio = toFloat(row.precio),
    p.descripcion = row.descripcion;
