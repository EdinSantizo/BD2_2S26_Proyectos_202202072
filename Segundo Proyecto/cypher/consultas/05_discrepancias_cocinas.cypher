
//
// PROYECTO 2 - SISTEMAS DE BASES DE DATOS 2
// Archivo: 05_discrepancias_cocinas.cypher
//
// CONSULTA 5: DISCREPANCIAS DE PREFERENCIAS
//
// Objetivo:
// Comparar la cocina favorita declarada por
// cada usuario con la cocina mas visitada.
//
// LE_GUSTA: preferencia declarada.
// VISITO -> PERTENECE_A: comportamiento real.
//
// Si existen empates, se consideran todas
// las cocinas empatadas en el valor maximo.
//
// Compatible con Neo4j 5.26.19
//

// ================================================
// 1. OBTENER USUARIOS
// ================================================

MATCH (u:Usuario)

// ================================================
// 2. COCINAS FAVORITAS DECLARADAS
// ================================================

CALL (u) {

    MATCH (u)-[g:LE_GUSTA]->(t:TipoCocina)

    WITH t, max(g.nivel_interes) AS interes
    ORDER BY t.id

    WITH
        collect({
            id: t.id,
            nombre: t.nombre,
            nivel: interes
        }) AS candidatas,
        max(interes) AS interes_maximo

    RETURN
        [c IN candidatas
         WHERE c.nivel = interes_maximo]
         AS favoritas,
        interes_maximo
}

// ================================================
// 3. COCINAS REALMENTE VISITADAS
// ================================================

CALL (u) {

    MATCH (u)-[:`VISITÓ`]->(r:Restaurante)
              -[:PERTENECE_A]->(t:TipoCocina)

    WITH t, count(*) AS visitas
    ORDER BY t.id

    WITH
        collect({
            id: t.id,
            nombre: t.nombre,
            visitas: visitas
        }) AS frecuencias,
        max(visitas) AS visitas_maximas

    RETURN
        [c IN frecuencias
         WHERE c.visitas = visitas_maximas]
         AS mas_visitadas,
        visitas_maximas
}

// ================================================
// 4. IDENTIFICAR DISCREPANCIAS
// ================================================

// Conservar las variables de las subconsultas
// antes de aplicar el filtro WHERE.

WITH u,
     favoritas,
     interes_maximo,
     mas_visitadas,
     visitas_maximas

// Existe discrepancia si ninguna de las
// cocinas mas visitadas coincide con alguna
// de las favoritas declaradas.

WHERE none(
    favorita IN favoritas
    WHERE any(
        real IN mas_visitadas
        WHERE real.id = favorita.id
    )
)

// ================================================
// 5. MOSTRAR RESULTADOS
// ================================================

RETURN
    u.id AS id_usuario,
    u.nombre AS usuario,

    [c IN favoritas | c.nombre]
        AS cocinas_favoritas_declaradas,

    interes_maximo AS nivel_interes,

    [c IN mas_visitadas | c.nombre]
        AS cocinas_mas_visitadas,

    visitas_maximas AS frecuencia_visitas,

    'Preferencia diferente al consumo'
        AS discrepancia

ORDER BY
    frecuencia_visitas DESC,
    id_usuario ASC

LIMIT 25;
