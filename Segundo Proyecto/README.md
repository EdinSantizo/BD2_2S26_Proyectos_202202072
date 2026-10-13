
# Proyecto 2 — Sistema de Recomendación de Restaurantes

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería**  
**Escuela de Ingeniería en Ciencias y Sistemas**  
**Curso:** Sistemas de Bases de Datos 2  
**Carné:** 202202072

## Descripción

Sistema de recomendación y análisis de restaurantes desarrollado mediante Neo4j, utilizando una base de datos orientada a grafos.

El proyecto representa las relaciones entre usuarios, restaurantes, chefs, platillos y tipos de cocina, permitiendo analizar recomendaciones sociales, preferencias gastronómicas, calificaciones, visitas y conexiones entre entidades.

## Tecnologías utilizadas

- Neo4j Database 5.26.19
- Neo4j Desktop 2.2.1
- Lenguaje Cypher
- Python 3.12
- Git y GitHub
- Arrows.app

## Modelo de datos

El sistema utiliza cinco tipos de nodos:

| Nodo | Cantidad |
|---|---:|
| Usuario | 500 |
| Restaurante | 200 |
| Chef | 100 |
| Platillo | 50 |
| TipoCocina | 15 |
| **Total** | **865** |

Se implementaron ocho tipos de relaciones:

| Relación | Cantidad |
|---|---:|
| CALIFICÓ | 5607 |
| VISITÓ | 5616 |
| ES_AMIGO_DE | 663 |
| PERTENECE_A | 227 |
| OFRECE | 679 |
| PREPARA | 301 |
| TRABAJA_EN | 213 |
| LE_GUSTA | 997 |
| **Total** | **14303** |

## Modelo conceptual

El modelo fue elaborado mediante Arrows.app.

![Modelo conceptual](diagramas/modelo_conceptual.png)

El archivo editable se encuentra en `diagramas/modelo_conceptual.json`.

## Estructura del proyecto

```text
Segundo Proyecto/
├── cypher/
│   ├── modelo/
│   ├── carga/
│   ├── consultas/
│   └── analisis/
├── data/
│   ├── nodos/
│   └── relaciones/
├── scripts/
├── diagramas/
├── docs/
├── evidencias/
└── README.md
```

### Organización

- `cypher/modelo/`: restricciones, índices y datos de prueba.
- `cypher/carga/`: scripts de importación masiva.
- `cypher/consultas/`: cinco consultas obligatorias.
- `cypher/analisis/`: dos análisis de redes.
- `data/nodos/`: archivos CSV de nodos.
- `data/relaciones/`: archivos CSV de relaciones.
- `scripts/`: generación y validación de datos.
- `diagramas/`: representación conceptual del grafo.
- `docs/`: documentación técnica y manual de usuario.
- `evidencias/`: material visual y resultados del proyecto.

## Requisitos previos

Para ejecutar el proyecto se necesita:

1. Neo4j Desktop con una instancia local de Neo4j 5.26.19.
2. Python 3.12 o una versión compatible.
3. Los archivos contenidos en este repositorio.
4. Acceso al editor de consultas de Neo4j.

No se requieren librerías externas de Python para generar los archivos CSV.

## Instalación y ejecución

### 1. Preparar la instancia

Crear una instancia local en Neo4j Desktop.

Nombre sugerido:

`BD2_Proyecto2_Restaurantes`

Seleccionar la versión `5.26.19`, configurar una contraseña y poner en ejecución la instancia.

Abrir Neo4j Query y conectarse a la base de datos `neo4j`.

### 2. Generar los datos

Desde una terminal ubicada en `Segundo Proyecto`, ejecutar:

```powershell
python scripts/generar_nodos.py
python scripts/generar_relaciones.py
python scripts/validar_datos.py
```

Los scripts generan los CSV correspondientes a 865 nodos y 14,303 relaciones.

La generación es reproducible mediante semillas fijas.

### 3. Preparar la importación

Abrir la carpeta de la instancia local desde Neo4j Desktop.

Localizar el directorio `import` de la instancia.

Copiar dentro de ese directorio los 13 archivos CSV disponibles en:

- `data/nodos/`
- `data/relaciones/`

Los archivos deben quedar directamente dentro de `import`, sin subcarpetas adicionales.

### 4. Crear restricciones e índices

Desde Neo4j Query ejecutar los bloques contenidos en:

`cypher/modelo/01_constraints_indices.cypher`

Se crean seis restricciones de unicidad y dos índices adicionales.

### 5. Cargar los nodos

Ejecutar los cinco bloques del archivo:

`cypher/carga/01_cargar_nodos.cypher`

Los datos se insertan mediante `LOAD CSV WITH HEADERS` y `MERGE`.

### 6. Cargar las relaciones

Ejecutar los ocho bloques del archivo:

`cypher/carga/02_cargar_relaciones.cypher`

Las consultas utilizan importaciones por lotes de 500 registros.

La carga debe realizarse después de crear todos los nodos.

Los archivos `02_nodos_prueba.cypher` y `03_relaciones_prueba.cypher` son ejemplos opcionales del modelo y no son necesarios para la carga masiva desde cero.

### 7. Verificar la base de datos

Para verificar el total de nodos:

```cypher
MATCH (n)
RETURN count(n) AS total_nodos;
```

Resultado esperado: `865`.

Para verificar el total de relaciones:

```cypher
MATCH ()-[r]->()
RETURN count(r) AS total_relaciones;
```

Resultado esperado: `14303`.

Para comprobar los tipos de relaciones:

```cypher
MATCH ()-[r]->()
RETURN type(r) AS tipo,
       count(r) AS cantidad
ORDER BY tipo;
```

## Consultas Cypher

Se implementaron cinco consultas de negocio:

| Archivo | Funcionalidad |
|---|---|
| 01_recomendacion_social.cypher | Recomendaciones hasta tres grados de amistad |
| 02_chefs_alto_impacto.cypher | Identificación de chefs destacados |
| 03_restaurantes_infravalorados.cypher | Análisis de reservas y calificaciones |
| 04_precios_vs_consumo.cypher | Comparación del rango de precios con el consumo |
| 05_discrepancias_cocinas.cypher | Comparación de preferencias y visitas reales |

Todos los archivos se encuentran en `cypher/consultas/`.

Las consultas pueden ejecutarse de manera independiente después de realizar la carga masiva.

## Análisis de redes

Se implementaron dos análisis adicionales:

### Ruta más corta entre usuarios

Archivo: `cypher/analisis/01_ruta_mas_corta.cypher`

Utiliza `shortestPath()` para encontrar la distancia mínima entre dos usuarios conectados por relaciones de amistad.

### Restaurantes altamente conectados

Archivo: `cypher/analisis/02_restaurantes_conectados.cypher`

Identifica establecimientos con mayor número de chefs vinculados y platillos destacados.

## Datos de prueba

Se prepararon casos controlados para comprobar los resultados:

| ID | Entidad | Validación |
|---|---|---|
| 1 | Juan Perez | Recomendación social |
| 1 | Carlos Lopez | Chef de alto impacto |
| 50 | Mesa China 050 | Restaurante infravalorado |
| 75 | Mesa Arabe 075 | Diferencia entre precios y consumo |
| 10 | Diego Castillo | Discrepancias gastronómicas |
| 16 | Bistro Italiana 016 | Alta conectividad |

Los datos utilizados son sintéticos y tienen propósitos académicos.

## Documentación

El repositorio incluye los siguientes documentos:

- [Documentación técnica](docs/documentacion_tecnica.md)
- [Manual de usuario](docs/manual_usuario.md)

La documentación técnica presenta el diseño del grafo, sus propiedades, relaciones, implementación y análisis de resultados.

El manual de usuario contiene las instrucciones para configurar Neo4j, importar los archivos y ejecutar las consultas.

## Observaciones

- La base utiliza identificadores únicos para sus nodos.
- Las calificaciones y niveles de interés manejan valores entre 1 y 5.
- Las relaciones VISITÓ permiten registrar múltiples visitas entre un usuario y un restaurante.
- Las consultas pueden ejecutarse nuevamente sin modificar los datos.
- Los montos utilizados para las categorías de precios son valores de referencia sintéticos.
- Las imágenes ilustrativas del manual sirven como apoyo visual; los scripts del repositorio constituyen la referencia ejecutable.

## Repositorio

https://github.com/EdinSantizo/BD2_2S26_Proyectos_202202072
