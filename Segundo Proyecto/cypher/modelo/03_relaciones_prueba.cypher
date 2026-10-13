
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 03_relaciones_prueba.cypher
// Objetivo: Crear las 8 relaciones del modelo conceptual.
// Compatible con Neo4j 5.26.
//

// ========================================
// 1. JUAN CALIFICO A LA PARRILLA
// ========================================

MATCH (u:Usuario {id: 1})
MATCH (r:Restaurante {id: 1})
MERGE (u)-[cal:`CALIFICÓ`]->(r)
SET cal.puntuacion = 5,
    cal.fecha = date('2026-09-10'),
    cal.comentario = 'excelente comida';

// ========================================
// 2. JUAN VISITO LA PARRILLA
// ========================================

MATCH (u:Usuario {id: 1})
MATCH (r:Restaurante {id: 1})
MERGE (u)-[v:`VISITÓ` {
    fecha_visita: date('2026-09-09')
}]->(r)
SET v.id_visita = 1,
    v.consumo = 85.0,
    v.con_reserva = true;

// ========================================
// 3. JUAN ES AMIGO DE MARIA
// ========================================

MATCH (juan:Usuario {id: 1})
MATCH (maria:Usuario {id: 2})
MERGE (juan)-[a:ES_AMIGO_DE]->(maria)
SET a.fecha_amistad = date('2024-01-15');

// ========================================
// 4. LA PARRILLA PERTENECE A ITALIANA
// ========================================

MATCH (r:Restaurante {id: 1})
MATCH (t:TipoCocina {id: 1})
MERGE (r)-[:PERTENECE_A]->(t);

// ========================================
// 5. LA PARRILLA OFRECE PIZZA MARGARITA
// ========================================

MATCH (r:Restaurante {id: 1})
MATCH (p:Platillo {id: 1})
MERGE (r)-[o:OFRECE]->(p)
SET o.precio = 65.0,
    o.disponible = true;

// ========================================
// 6. CARLOS PREPARA PIZZA MARGARITA
// ========================================

MATCH (c:Chef {id: 1})
MATCH (p:Platillo {id: 1})
MERGE (c)-[pr:PREPARA]->(p)
SET pr.estilo = 'tradicional',
    pr.especialidad = 'cocina italiana';

// ========================================
// 7. CARLOS TRABAJA EN LA PARRILLA
// ========================================

MATCH (c:Chef {id: 1})
MATCH (r:Restaurante {id: 1})
MERGE (c)-[tr:TRABAJA_EN]->(r)
SET tr.fecha_inicio = date('2020-02-01'),
    tr.puesto = 'Chef principal';

// ========================================
// 8. A JUAN LE GUSTA LA COCINA ITALIANA
// ========================================

MATCH (u:Usuario {id: 1})
MATCH (t:TipoCocina {id: 1})
MERGE (u)-[g:LE_GUSTA]->(t)
SET g.nivel_interes = 5;
