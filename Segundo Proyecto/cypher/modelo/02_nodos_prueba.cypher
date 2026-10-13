
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Sistema de Recomendacion de Restaurantes con Neo4j
//
// Archivo: 02_nodos_prueba.cypher
// Objetivo: Crear los 6 nodos del modelo conceptual.
// Compatible con Neo4j 5.26
//

// ===============================================
// 1. USUARIO: JUAN PEREZ
// ===============================================

MERGE (u:Usuario {id: 1})
SET u.nombre = 'Juan Perez',
    u.email = 'juan@gmail.com',
    u.edad = 25,
    u.pais = 'Guatemala';

// ===============================================
// 2. USUARIO: MARIA LOPEZ
// ===============================================

MERGE (u:Usuario {id: 2})
SET u.nombre = 'Maria Lopez',
    u.email = 'maria@gmail.com',
    u.edad = 27,
    u.pais = 'Guatemala';

// ===============================================
// 3. RESTAURANTE: LA PARRILLA
// ===============================================

MERGE (r:Restaurante {id: 1})
SET r.nombre = 'La Parrilla',
    r.anio_apertura = 2015,
    r.rango_precios = 'medio',
    r.descripcion = 'Restaurante de carnes';

// ===============================================
// 4. TIPO DE COCINA: ITALIANA
// ===============================================

MERGE (t:TipoCocina {id: 1})
SET t.nombre = 'Italiana',
    t.descripcion = 'Cocina tradicional de Italia';

// ===============================================
// 5. CHEF: CARLOS LOPEZ
// ===============================================

MERGE (c:Chef {id: 1})
SET c.nombre = 'Carlos Lopez',
    c.fecha_nacimiento = date('1985-04-12'),
    c.nacionalidad = 'Guatemalteca';

// ===============================================
// 6. PLATILLO: PIZZA MARGARITA
// ===============================================

MERGE (p:Platillo {id: 1})
SET p.nombre = 'Pizza Margarita',
    p.precio = 65.00,
    p.descripcion = 'Pizza con tomate y mozzarella';
