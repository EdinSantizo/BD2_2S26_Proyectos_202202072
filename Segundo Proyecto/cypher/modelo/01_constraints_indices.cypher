
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Sistema de Recomendacion de Restaurantes con Neo4j
//
// Archivo: 01_constraints_indices.cypher
// Objetivo: Crear restricciones e indices del modelo.
//
// Compatible con Neo4j 5.26
//

// ===============================================
// 1. CONSTRAINTS DE UNICIDAD POR ID
// ===============================================

// Usuario
CREATE CONSTRAINT usuario_id_unico IF NOT EXISTS
FOR (u:Usuario)
REQUIRE u.id IS UNIQUE;

// Restaurante
CREATE CONSTRAINT restaurante_id_unico IF NOT EXISTS
FOR (r:Restaurante)
REQUIRE r.id IS UNIQUE;

// TipoCocina
CREATE CONSTRAINT tipococina_id_unico IF NOT EXISTS
FOR (t:TipoCocina)
REQUIRE t.id IS UNIQUE;

// Chef
CREATE CONSTRAINT chef_id_unico IF NOT EXISTS
FOR (c:Chef)
REQUIRE c.id IS UNIQUE;

// Platillo
CREATE CONSTRAINT platillo_id_unico IF NOT EXISTS
FOR (p:Platillo)
REQUIRE p.id IS UNIQUE;


// ===============================================
// 2. CONSTRAINT ADICIONAL DE USUARIO
// ===============================================

// No permitir emails duplicados
CREATE CONSTRAINT usuario_email_unico IF NOT EXISTS
FOR (u:Usuario)
REQUIRE u.email IS UNIQUE;


// ===============================================
// 3. INDICES DE BUSQUEDA
// ===============================================

// Busqueda de restaurantes por nombre
CREATE INDEX idx_restaurante_nombre IF NOT EXISTS
FOR (r:Restaurante)
ON (r.nombre);

// Busqueda de tipos de cocina por nombre
CREATE INDEX idx_tipococina_nombre IF NOT EXISTS
FOR (t:TipoCocina)
ON (t.nombre);
