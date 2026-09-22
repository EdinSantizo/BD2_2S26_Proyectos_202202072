\# DOCUMENTACIÓN TÉCNICA



\## Sistema de Gestión de Reservas y Boletos Aéreos con Apache Cassandra



\*\*Universidad de San Carlos de Guatemala\*\*  

\*\*Facultad de Ingeniería\*\*  

\*\*Ingeniería en Ciencias y Sistemas\*\*  

\*\*Curso:\*\* Sistemas de Bases de Datos 2  

\*\*Proyecto:\*\* Primer Proyecto  

\*\*Carné:\*\* 202202072  



\---



\# 1. Introducción



El presente proyecto implementa un sistema de gestión de reservas y boletos aéreos utilizando Apache Cassandra como sistema de base de datos distribuida.



La solución fue diseñada bajo un enfoque Query-Driven, en el cual el modelo físico de datos se construye a partir de las consultas que el sistema debe resolver, en lugar de aplicar un modelo relacional tradicional.



Debido a la naturaleza distribuida de Cassandra, se priorizaron aspectos como la desnormalización, el diseño correcto de partition keys y clustering columns, la replicación de datos y el uso de niveles de consistencia.



El sistema contempla información relacionada con pasajeros, aeronaves, vuelos, asientos, reservas y pagos. Además, incluye tablas especializadas para resolver eficientemente las cinco consultas principales solicitadas.



\---



\# 2. Objetivos



\## 2.1 Objetivo general



Diseñar e implementar una base de datos distribuida en Apache Cassandra para administrar reservas y boletos aéreos, aplicando técnicas de modelado Query-Driven, replicación, consistencia y tolerancia a fallos.



\## 2.2 Objetivos específicos



\- Implementar un clúster Apache Cassandra compuesto por tres nodos.

\- Utilizar una estrategia de replicación adecuada para un entorno distribuido.

\- Diseñar tablas Cassandra optimizadas para las consultas requeridas.

\- Evitar el uso de JOIN y ALLOW FILTERING en las consultas principales.

\- Cargar al menos 100,000 reservas mediante scripts desarrollados en Python.

\- Utilizar Batch Writes durante el proceso de carga.

\- Implementar contadores y tablas de agregación para consultas estadísticas.

\- Implementar TTL para reservas temporales.

\- Evaluar los niveles de consistencia ONE, QUORUM y ALL.

\- Simular la caída y recuperación de un nodo del clúster.



\---



\# 3. Tecnologías utilizadas



La solución fue desarrollada utilizando las siguientes tecnologías:



\- Apache Cassandra 4.1.12.

\- Docker.

\- Docker Compose.

\- Python 3.12.

\- cassandra-driver 3.30.1.

\- Faker 40.39.0.

\- PowerShell.

\- Git.

\- GitHub.



El clúster Cassandra se ejecuta mediante contenedores Docker, lo que permite reproducir fácilmente la infraestructura en otros equipos.



\---



\# 4. Arquitectura general



La solución utiliza un clúster formado por tres nodos Apache Cassandra.



Los nodos son:



\- cassandra1.

\- cassandra2.

\- cassandra3.



Todos pertenecen al mismo datacenter:



```text

datacenter1

```



y al clúster:



```text

AerolineaCluster

```



Los puertos publicados en el equipo anfitrión son:



```text

cassandra1 -> localhost:9042

cassandra2 -> localhost:9043

cassandra3 -> localhost:9044

```



La comunicación interna entre los nodos se realiza mediante la red Docker:



```text

primerproyecto\_cassandra\_net

```



Cada nodo posee un volumen independiente para mantener la persistencia de sus datos.



\---



\# 5. Modelo conceptual



El sistema contempla las siguientes entidades principales:



\- Pasajero.

\- Aeronave.

\- Vuelo.

\- Asiento.

\- Reserva.

\- Pago.



Las relaciones principales son:



\- Un pasajero puede realizar múltiples reservas.

\- Una aeronave puede operar múltiples vuelos.

\- Un vuelo contiene múltiples asientos.

\- Un vuelo recibe múltiples reservas.

\- Una reserva asigna un asiento.

\- Una reserva posee información asociada de pago.



El modelo conceptual completo se encuentra en:



```text

diagramas/modelo\_er\_conceptual.pdf

```



y su código fuente Mermaid en:



```text

diagramas/modelo\_er\_conceptual.mmd

```



Este modelo representa el dominio del sistema. Sin embargo, no se utiliza directamente como modelo físico en Cassandra, debido a que Cassandra requiere diseñar las tablas en función de los patrones de consulta.



\---



\# 6. Diseño Query-Driven



El diseño Cassandra fue construido partiendo de las consultas requeridas.



En lugar de normalizar los datos, cada consulta dispone de una tabla especializada que contiene los datos necesarios para responderla de manera directa.



Esto permite evitar:



```text

JOIN

ALLOW FILTERING

consultas completas sobre tablas

ordenamiento en el cliente

```



El documento detallado del análisis Query-Driven se encuentra en:



```text

docs/diseno\_query\_driven.md

```



El modelo lógico Cassandra se encuentra en:



```text

diagramas/modelo\_logico\_cassandra.pdf

```



\---



\# 7. Keyspace



El keyspace principal del proyecto es:



```text

aerolinea

```



Su definición es:



```sql

CREATE KEYSPACE IF NOT EXISTS aerolinea

WITH replication = {

&#x20;   'class': 'NetworkTopologyStrategy',

&#x20;   'datacenter1': 3

}

AND durable\_writes = true;

```



Se utilizó:



```text

NetworkTopologyStrategy

```



con un Replication Factor igual a:



```text

3

```



Esto significa que cada dato del keyspace posee una réplica en cada uno de los tres nodos disponibles dentro de `datacenter1`.



La configuración fue verificada utilizando:



```bash

nodetool status aerolinea

```



obteniéndose un ownership efectivo de 100% para los tres nodos.



\---



\# 8. Tablas del sistema



La implementación contiene 11 tablas.



\## 8.1 Tablas operativas



Las tablas base utilizadas para representar las principales entidades son:



```text

pasajeros\_por\_id

aeronaves\_por\_id

vuelos\_por\_id

asientos\_por\_vuelo

reservas\_por\_id

pagos\_por\_reserva

```



Estas tablas permiten mantener información operativa accesible mediante sus identificadores principales.



\## 8.2 Tablas Query-Driven



Las cinco consultas principales utilizan las siguientes tablas:



```text

Q1 -> disponibilidad\_asientos\_por\_vuelo\_clase

Q2 -> historial\_reservas\_por\_pasajero

Q3 -> manifiesto\_por\_vuelo

Q4 -> ocupacion\_por\_ruta\_mes

Q5 -> ranking\_ingresos\_por\_periodo

```



En Cassandra la duplicación de información es intencional y permite responder consultas sin realizar JOIN.



\---



\# 9. Diseño de claves



\## 9.1 Q1 - Disponibilidad de asientos



Tabla:



```text

disponibilidad\_asientos\_por\_vuelo\_clase

```



Clave primaria:



```text

PRIMARY KEY ((vuelo\_id), clase)

```



Donde:



```text

Partition Key = vuelo\_id

Clustering Column = clase

```



La consulta conoce el vuelo, por lo cual Cassandra accede directamente a su partición.



Los campos:



```text

disponibles

ocupados

```



son contadores Cassandra.



Esto evita realizar un COUNT sobre todos los asientos cada vez que se consulta la disponibilidad.



\---



\## 9.2 Q2 - Historial del pasajero



Tabla:



```text

historial\_reservas\_por\_pasajero

```



Clave primaria:



```text

PRIMARY KEY ((pasajero\_id), fecha\_salida, reserva\_id)

```



Orden:



```text

fecha\_salida DESC

reserva\_id ASC

```



La partition key es:



```text

pasajero\_id

```



Esto agrupa el historial de cada pasajero dentro de una sola partición.



La columna:



```text

fecha\_salida

```



permite realizar búsquedas por rango mediante:



```sql

fecha\_salida >= fecha\_inicial

fecha\_salida <= fecha\_final

```



La información de vuelo, asiento, reserva y pago se encuentra desnormalizada dentro de la misma tabla.



\---



\## 9.3 Q3 - Manifiesto del vuelo



Tabla:



```text

manifiesto\_por\_vuelo

```



Clave primaria:



```text

PRIMARY KEY ((vuelo\_id), fila\_asiento, letra\_asiento)

```



Orden:



```text

fila\_asiento ASC

letra\_asiento ASC

```



La partition key es:



```text

vuelo\_id

```



Los asientos fueron separados en:



```text

fila\_asiento

letra\_asiento

```



para evitar un orden lexicográfico incorrecto.



Por ejemplo, almacenar directamente el asiento como texto podría generar:



```text

1A

10A

11A

2A

```



Mientras que la separación permite mantener:



```text

1A

1B

...

2A

2B

...

10A

10B

```



\---



\## 9.4 Q4 - Ocupación por ruta



Tabla:



```text

ocupacion\_por\_ruta\_mes

```



Partition key compuesta:



```text

(origen, destino, anio\_mes)

```



Clustering columns:



```text

fecha\_salida

vuelo\_id

```



La columna:



```text

anio\_mes

```



funciona como bucket mensual.



Esto evita crear particiones excesivamente grandes y permite restringir la consulta a una ruta y un período determinado.



La tabla mantiene los contadores:



```text

reservas\_confirmadas

capacidad\_total

```



por vuelo.



Con estos valores puede calcularse el porcentaje de ocupación directamente en Cassandra.



\---



\## 9.5 Q5 - Ranking por ingresos



Tabla:



```text

ranking\_ingresos\_por\_periodo

```



Partition key:



```text

(fecha\_inicio, fecha\_fin)

```



Clustering columns:



```text

ingreso\_total DESC

vuelo\_id ASC

```



El ingreso total de cada vuelo se materializa previamente.



Gracias al orden descendente de `ingreso\_total`, Cassandra puede ejecutar:



```sql

LIMIT N

```



y obtener directamente los vuelos con mayores ingresos dentro del período.



No es necesario ordenar los resultados en Python.



\---



\# 10. Implementación del clúster



El clúster se define mediante:



```text

docker-compose.yml

```



Se desplegaron tres nodos utilizando:



```text

cassandra:4.1

```



La versión detectada durante las pruebas fue:



```text

Apache Cassandra 4.1.12

```



La configuración del clúster fue:



```text

Cluster Name: AerolineaCluster

Datacenter: datacenter1

Rack: rack1

Snitch: GossipingPropertyFileSnitch

Partitioner: Murmur3Partitioner

```



La validación mediante `nodetool describecluster` mostró:



```text

Live: 3

Joining: 0

Moving: 0

Leaving: 0

Unreachable: 0

```



Los tres nodos compartieron la misma versión del esquema, confirmando Schema Agreement.



\---



\# 11. Replicación



Se utilizó:



```text

NetworkTopologyStrategy

```



con:



```text

Replication Factor = 3

```



El comando:



```bash

nodetool status aerolinea

```



mostró los tres nodos en estado:



```text

UN

```



donde:



```text

U = Up

N = Normal

```



Cada nodo presentó:



```text

Owns (effective): 100.0%

```



para el keyspace `aerolinea`.



También se realizó una prueba escribiendo un registro mediante `cassandra1` y leyéndolo posteriormente desde `cassandra2` y `cassandra3`, comprobando el funcionamiento distribuido del clúster.



\---



\# 12. Carga masiva de datos



La carga se implementó mediante Python utilizando:



```text

cassandra-driver

Faker

```



El script principal es:



```text

scripts/03\_carga\_masiva.py

```



La ejecución utilizada fue:



```powershell

.\\.venv\\Scripts\\python.exe -u scripts\\03\_carga\_masiva.py --reservas 100000

```



La carga definitiva generó:



```text

Reservas:      100,000

Pagos:         100,000

Historial Q2:  100,000

Manifiesto Q3: 100,000

Pasajeros:       5,000

Aeronaves:          20

Vuelos:          1,000

Asientos:      120,000

Registros Q1:    3,000

Registros Q4:    1,000

Registros Q5:    1,000

```



La distribución de estados de las reservas fue:



```text

Confirmadas: 80,000

Pendientes:  10,000

Canceladas:  10,000

```



El tiempo medido para la carga definitiva fue:



```text

26.44 segundos

```



\---



\# 13. Batch Writes



La carga de reservas utilizó:



```python

BatchStatement(

&#x20;   batch\_type=BatchType.UNLOGGED,

&#x20;   consistency\_level=ConsistencyLevel.ONE

)

```



Cada Batch Write agrupó:



```text

5 reservas

```



Cada reserva genera cuatro escrituras:



```text

1\. reservas\_por\_id

2\. pagos\_por\_reserva

3\. historial\_reservas\_por\_pasajero

4\. manifiesto\_por\_vuelo

```



Por lo tanto:



```text

5 reservas x 4 statements = 20 statements por batch

```



Para las 100,000 reservas se ejecutaron:



```text

20,000 Batch Writes

```



Se utilizaron batches pequeños para evitar construir lotes excesivamente grandes.



\---



\# 14. Consulta Q1 - Disponibilidad por clase



La consulta utilizada fue:



```sql

SELECT

&#x20;   clase,

&#x20;   disponibles,

&#x20;   ocupados

FROM disponibilidad\_asientos\_por\_vuelo\_clase

WHERE vuelo\_id =

&#x20;   7738e6e4-6f78-5a6a-9adc-1f33c41fe130;

```



Resultado obtenido:



```text

BUSINESS -> 2 disponibles, 10 ocupados

PREMIUM  -> 1 disponible, 17 ocupados

ECONOMY  -> 27 disponibles, 63 ocupados

```



Total:



```text

Disponibles: 30

Ocupados:    90

Capacidad:  120

```



La consulta utiliza directamente la partition key `vuelo\_id` y no realiza conteos en tiempo de lectura.



\---



\# 15. Consulta Q2 - Historial de pasajero



Se consultó el pasajero:



```text

af65cd22-ae00-5a4a-8268-45d22029b352

```



dentro del rango:



```text

2026-01-10

a

2026-01-26

```



Consulta:



```sql

SELECT

&#x20;   fecha\_salida,

&#x20;   codigo\_vuelo,

&#x20;   aeropuerto\_origen,

&#x20;   aeropuerto\_destino,

&#x20;   numero\_asiento,

&#x20;   clase,

&#x20;   estado\_reserva,

&#x20;   estado\_pago,

&#x20;   monto\_pago

FROM historial\_reservas\_por\_pasajero

WHERE pasajero\_id =

&#x20;   af65cd22-ae00-5a4a-8268-45d22029b352

&#x20; AND fecha\_salida >= '2026-01-10T00:00:00Z'

&#x20; AND fecha\_salida <= '2026-01-26T23:59:59Z';

```



Resultado:



```text

13 registros

```



Los resultados se devolvieron ordenados cronológicamente de forma descendente.



No se utilizó JOIN ni ALLOW FILTERING.



\---



\# 16. Consulta Q3 - Manifiesto de vuelo



Consulta:



```sql

SELECT

&#x20;   numero\_asiento,

&#x20;   clase,

&#x20;   nombre\_pasajero,

&#x20;   documento\_identificacion,

&#x20;   estado\_reserva,

&#x20;   estado\_pago

FROM manifiesto\_por\_vuelo

WHERE vuelo\_id =

&#x20;   7738e6e4-6f78-5a6a-9adc-1f33c41fe130;

```



Resultado:



```text

100 pasajeros

```



Los resultados fueron devueltos directamente en orden de asiento:



```text

1A

1B

1C

...

10A

10B

...

17D

```



La información del pasajero, reserva y pago se encuentra desnormalizada dentro de la tabla.



\---



\# 17. Consulta Q4 - Porcentaje de ocupación



La prueba se realizó para:



```text

Ruta: GUA -> MEX

Bucket: 2026-01

Período: enero 2026

```



Consulta:



```sql

SELECT

&#x20;   SUM(reservas\_confirmadas) AS reservas\_confirmadas,

&#x20;   SUM(capacidad\_total) AS capacidad\_total,

&#x20;   (CAST(SUM(reservas\_confirmadas) AS decimal) \* 100)

&#x20;       / SUM(capacidad\_total) AS porcentaje\_ocupacion

FROM ocupacion\_por\_ruta\_mes

WHERE origen = 'GUA'

&#x20; AND destino = 'MEX'

&#x20; AND anio\_mes = '2026-01'

&#x20; AND fecha\_salida >= '2026-01-01T00:00:00Z'

&#x20; AND fecha\_salida <= '2026-01-31T23:59:59Z';

```



Resultado:



```text

Reservas confirmadas: 1,280

Capacidad total:      1,920

Porcentaje:           66.6666666667 %

```



Los contadores necesarios se encuentran previamente materializados en la tabla.



\---



\# 18. Consulta Q5 - Top N por ingresos



La prueba se realizó para enero de 2026.



Consulta:



```sql

SELECT

&#x20;   codigo\_vuelo,

&#x20;   fecha\_salida,

&#x20;   origen,

&#x20;   destino,

&#x20;   ingreso\_total

FROM ranking\_ingresos\_por\_periodo

WHERE fecha\_inicio = '2026-01-01'

&#x20; AND fecha\_fin = '2026-01-31'

ORDER BY ingreso\_total DESC

LIMIT 10;

```



La consulta devolvió:



```text

10 registros

```



con un ingreso materializado de:



```text

19,200.00

```



para los vuelos obtenidos.



Durante la generación de datos se utilizó una distribución uniforme de capacidad, clases y estados por vuelo, por lo cual existen empates entre múltiples vuelos.



Cuando dos vuelos poseen el mismo ingreso, Cassandra utiliza `vuelo\_id ASC` como segundo criterio de clustering.



El ranking no requiere realizar ordenamiento en la aplicación cliente.



\---



\# 19. TTL



Se implementó una prueba de Time To Live sobre una reserva temporal.



La inserción utilizada fue:



```sql

INSERT INTO reservas\_por\_id (

&#x20;   reserva\_id,

&#x20;   pasajero\_id,

&#x20;   vuelo\_id,

&#x20;   numero\_asiento,

&#x20;   fecha\_reserva,

&#x20;   estado

)

VALUES (

&#x20;   99999999-9999-4999-8999-999999999999,

&#x20;   af65cd22-ae00-5a4a-8268-45d22029b352,

&#x20;   7738e6e4-6f78-5a6a-9adc-1f33c41fe130,

&#x20;   'TTL-TEST',

&#x20;   toTimestamp(now()),

&#x20;   'EXPIRABLE'

)

USING TTL 30;

```



Posteriormente se consultó:



```sql

TTL(estado)

```



obteniéndose inicialmente:



```text

22 segundos

```



y posteriormente:



```text

11 segundos

```



Una vez finalizados los 30 segundos, Cassandra devolvió:



```text

0 rows

```



demostrando la eliminación automática de la información.



El TTL de 30 segundos se utilizó únicamente con fines demostrativos. En un sistema real, el valor se establecería en función del tiempo permitido para mantener una reserva pendiente.



\---



\# 20. Consistency Levels



Se analizaron los niveles:



```text

ONE

QUORUM

ALL

```



Con Replication Factor 3:



```text

ONE    requiere 1 réplica.

QUORUM requiere 2 réplicas.

ALL    requiere 3 réplicas.

```



Cada nivel fue probado 20 veces para obtener métricas de disponibilidad y latencia.



\---



\# 21. Prueba con tres nodos disponibles



Con los tres nodos en estado `UN` se obtuvieron los siguientes resultados:



| Nivel | Éxitos | Errores | Mínima | Promedio | Máxima |

|---|---:|---:|---:|---:|---:|

| ONE | 20 | 0 | 15.781 ms | 17.041 ms | 21.171 ms |

| QUORUM | 20 | 0 | 7.487 ms | 16.109 ms | 25.148 ms |

| ALL | 20 | 0 | 9.179 ms | 16.960 ms | 28.605 ms |



Los tres niveles fueron capaces de responder correctamente.



Las pequeñas diferencias de latencia observadas corresponden a una prueba ejecutada localmente mediante Docker y no deben interpretarse como una medición general del rendimiento teórico de cada nivel.



\---



\# 22. Simulación de falla



Para simular una falla se detuvo:



```text

cassandra3

```



mediante:



```bash

docker stop cassandra3

```



El comando:



```bash

nodetool status aerolinea

```



mostró posteriormente:



```text

cassandra1 -> UN

cassandra2 -> UN

cassandra3 -> DN

```



donde:



```text

D = Down

N = Normal

```



\---



\# 23. Prueba con un nodo caído



Con únicamente dos réplicas disponibles se obtuvieron:



| Nivel | Éxitos | Errores | Mínima | Promedio | Máxima |

|---|---:|---:|---:|---:|---:|

| ONE | 20 | 0 | 6.567 ms | 15.107 ms | 21.327 ms |

| QUORUM | 20 | 0 | 10.802 ms | 16.361 ms | 23.195 ms |

| ALL | 0 | 20 | 8.916 ms | 15.749 ms | 22.702 ms |



ONE continuó funcionando debido a que únicamente requiere una réplica disponible.



QUORUM también continuó funcionando porque, para RF=3, requiere dos réplicas.



ALL dejó de funcionar porque necesita las tres réplicas.



El error retornado fue:



```text

Cannot achieve consistency level ALL

required\_replicas: 3

alive\_replicas: 2

```



Este comportamiento demuestra el compromiso existente entre consistencia y disponibilidad.



\---



\# 24. Recuperación del clúster



El nodo fue restaurado utilizando:



```bash

docker start cassandra3

```



Posteriormente los tres nodos regresaron al estado:



```text

UN

UN

UN

```



Se repitieron las pruebas de consistencia.



Resultados:



| Nivel | Éxitos | Errores | Mínima | Promedio | Máxima |

|---|---:|---:|---:|---:|---:|

| ONE | 20 | 0 | 12.334 ms | 16.667 ms | 21.832 ms |

| QUORUM | 20 | 0 | 12.785 ms | 15.671 ms | 17.908 ms |

| ALL | 20 | 0 | 14.424 ms | 16.481 ms | 18.664 ms |



El nivel ALL volvió a funcionar correctamente después de la recuperación de `cassandra3`.



\---



\# 25. Resultados generales



La implementación final consiguió:



```text

Clúster Cassandra:          3 nodos

Versión Cassandra:          4.1.12

Replication Factor:         3

Estrategia:                 NetworkTopologyStrategy



Tablas:                     11

Reservas:                   100,000

Pagos:                      100,000

Pasajeros:                  5,000

Vuelos:                     1,000

Asientos:                   120,000



Batch Writes:               20,000

Tiempo carga:               26.44 segundos



Consultas requeridas:       5/5

JOIN utilizados:            0

ALLOW FILTERING utilizados: 0



TTL:                        Validado

Falla de nodo:              Validada

Recuperación:               Validada

ONE:                        Validado

QUORUM:                     Validado

ALL:                        Validado

```



\---



\# 26. Organización del código



Los principales archivos del proyecto son:



```text

Primer Proyecto/

│

├── cql/

│   ├── 01\_keyspace.cql

│   ├── 02\_schema.cql

│   └── 03\_queries.cql

│

├── scripts/

│   ├── 01\_verificar\_conexion.py

│   ├── 02\_carga\_prueba.py

│   ├── 03\_carga\_masiva.py

│   └── 04\_prueba\_tolerancia.py

│

├── diagramas/

│   ├── modelo\_er\_conceptual.mmd

│   ├── modelo\_er\_conceptual.pdf

│   ├── modelo\_logico\_cassandra.mmd

│   └── modelo\_logico\_cassandra.pdf

│

├── docs/

│   ├── diseno\_query\_driven.md

│   └── documentacion\_tecnica.md

│

├── evidencias/

│   ├── carga/

│   ├── cluster/

│   ├── consultas/

│   └── tolerancia\_fallos/

│

├── docker-compose.yml

└── requirements.txt

```



\---



\# 27. Conclusiones técnicas



Apache Cassandra permitió implementar una solución distribuida capaz de almacenar y consultar un volumen considerable de información sin depender de JOIN o consultas con ALLOW FILTERING.



El enfoque Query-Driven permitió diseñar cada tabla según su patrón específico de acceso. Esto permitió que las cinco consultas solicitadas utilizaran directamente sus respectivas partition keys y clustering columns.



La desnormalización fue fundamental para integrar información de pasajeros, vuelos, reservas, asientos y pagos dentro de las tablas requeridas por cada consulta.



La utilización de contadores y datos materializados permitió evitar cálculos costosos sobre el conjunto completo de registros.



La carga de 100,000 reservas mediante Python y Batch Writes demostró que la infraestructura desarrollada puede manejar operaciones masivas de escritura de forma automatizada.



La configuración con NetworkTopologyStrategy y Replication Factor 3 permitió mantener tres copias de la información dentro del clúster.



Las pruebas de consistencia evidenciaron que ONE y QUORUM continúan disponibles ante la caída de uno de los tres nodos, mientras que ALL requiere la disponibilidad de todas las réplicas.



Finalmente, la recuperación de `cassandra3` permitió restablecer completamente el clúster y volver a ejecutar satisfactoriamente consultas con Consistency Level ALL.

