\# Sistema de Gestión de Reservas y Boletos Aéreos con Apache Cassandra



Proyecto desarrollado para el curso de \*\*Sistemas de Bases de Datos 2\*\* de la Universidad de San Carlos de Guatemala.



\*\*Carné:\*\* 202202072



\---



\## Descripción



El proyecto implementa un sistema de gestión de reservas y boletos aéreos utilizando \*\*Apache Cassandra\*\* como base de datos distribuida.



La solución fue diseñada utilizando un enfoque \*\*Query-Driven\*\*, donde las tablas se crean a partir de las consultas que el sistema debe resolver.



El sistema administra información relacionada con:



\- Pasajeros.

\- Aeronaves.

\- Vuelos.

\- Asientos.

\- Reservas.

\- Pagos.



Además, implementa:



\- Clúster Cassandra de 3 nodos.

\- Replication Factor 3.

\- NetworkTopologyStrategy.

\- 100,000 reservas.

\- Batch Writes.

\- 5 consultas Query-Driven.

\- Contadores Cassandra.

\- TTL.

\- Pruebas con ONE, QUORUM y ALL.

\- Simulación de caída y recuperación de nodos.



\---



\# Arquitectura



El clúster está compuesto por:



```text

cassandra1

cassandra2

cassandra3

```



Configuración:



```text

Cluster: AerolineaCluster

Datacenter: datacenter1

Rack: rack1

Replication Factor: 3

Replication Strategy: NetworkTopologyStrategy

Cassandra: 4.1.12

```



Puertos:



```text

cassandra1 -> localhost:9042

cassandra2 -> localhost:9043

cassandra3 -> localhost:9044

```



\---



\# Estructura del proyecto



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

├── docs/

│   ├── diseno\_query\_driven.md

│   ├── documentacion\_tecnica.md

│   ├── documentacion\_tecnica.pdf

│   ├── manual\_usuario.md

│   └── manual\_usuario.pdf

│

├── diagramas/

│   ├── modelo\_er\_conceptual.mmd

│   ├── modelo\_er\_conceptual.pdf

│   ├── modelo\_logico\_cassandra.mmd

│   └── modelo\_logico\_cassandra.pdf

│

├── evidencias/

│   ├── carga/

│   ├── cluster/

│   ├── consultas/

│   └── tolerancia\_fallos/

│

├── docker-compose.yml

├── requirements.txt

└── README.md

```



\---



\# Requisitos



Para ejecutar el proyecto se requiere:



\- Docker Desktop.

\- Docker Compose.

\- Python 3.12.

\- Git.

\- PowerShell.



\---



\# Iniciar el clúster



Desde la carpeta `Primer Proyecto`:



```powershell

docker compose up -d

```



Verificar los contenedores:



```powershell

docker compose ps

```



Verificar el estado del clúster:



```powershell

docker exec cassandra1 nodetool status

```



Los tres nodos deben aparecer en estado:



```text

UN

```



donde:



```text

U = Up

N = Normal

```



\---



\# Crear el keyspace



Ejecutar:



```powershell

Get-Content -Raw .\\cql\\01\_keyspace.cql | docker exec -i cassandra1 cqlsh

```



El keyspace principal es:



```text

aerolinea

```



Configurado con:



```text

NetworkTopologyStrategy

datacenter1 = 3

```



\---



\# Crear las tablas



Ejecutar:



```powershell

Get-Content -Raw .\\cql\\02\_schema.cql | docker exec -i cassandra1 cqlsh

```



El esquema contiene \*\*11 tablas\*\*.



\---



\# Tablas principales



\## Tablas operativas



```text

pasajeros\_por\_id

aeronaves\_por\_id

vuelos\_por\_id

asientos\_por\_vuelo

reservas\_por\_id

pagos\_por\_reserva

```



\## Tablas Query-Driven



```text

Q1 -> disponibilidad\_asientos\_por\_vuelo\_clase

Q2 -> historial\_reservas\_por\_pasajero

Q3 -> manifiesto\_por\_vuelo

Q4 -> ocupacion\_por\_ruta\_mes

Q5 -> ranking\_ingresos\_por\_periodo

```



Las consultas principales no utilizan:



```text

JOIN

ALLOW FILTERING

```



\---



\# Entorno Python



Crear el entorno virtual:



```powershell

python -m venv .venv

```



Instalar las dependencias:



```powershell

.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



\---



\# Verificar conexión



Ejecutar:



```powershell

.\\.venv\\Scripts\\python.exe scripts\\01\_verificar\_conexion.py

```



La ejecución debe confirmar:



```text

Conexion establecida correctamente.

Keyspace actual: aerolinea

Version Cassandra: 4.1.12

Tablas encontradas: 11

```



\---



\# Carga masiva



El script principal de carga es:



```text

scripts/03\_carga\_masiva.py

```



Para generar las \*\*100,000 reservas\*\*:



```powershell

.\\.venv\\Scripts\\python.exe -W ignore::DeprecationWarning -u scripts\\03\_carga\_masiva.py --reservas 100000

```



Resultado obtenido durante la ejecución del proyecto:



```text

Reservas:      100,000

Confirmadas:    80,000

Pendientes:     10,000

Canceladas:     10,000



Pasajeros:       5,000

Aeronaves:          20

Vuelos:          1,000

Asientos:      120,000



Batch Writes:    20,000

Tiempo total:     26.44 segundos

```



El tiempo de ejecución puede variar dependiendo del equipo.



\---



\# Batch Writes



La carga utiliza:



```python

BatchStatement(

&#x20;   batch\_type=BatchType.UNLOGGED,

&#x20;   consistency\_level=ConsistencyLevel.ONE

)

```



Cada batch contiene:



```text

5 reservas

x

4 escrituras por reserva

=

20 statements

```



Las cuatro escrituras corresponden a:



```text

reservas\_por\_id

pagos\_por\_reserva

historial\_reservas\_por\_pasajero

manifiesto\_por\_vuelo

```



\---



\# Consultas requeridas



Las consultas se encuentran en:



```text

cql/03\_queries.cql

```



\## Q1 - Disponibilidad de asientos por clase



Obtiene:



```text

Clase

Asientos disponibles

Asientos ocupados

```



para un vuelo específico.



\---



\## Q2 - Historial de pasajero



Permite consultar el historial de un pasajero dentro de un rango de fechas.



La información incluye:



```text

Vuelo

Origen

Destino

Asiento

Clase

Estado de reserva

Estado de pago

Monto

```



\---



\## Q3 - Manifiesto de vuelo



Obtiene los pasajeros asignados a un vuelo ordenados correctamente por número de asiento.



Ejemplo:



```text

1A

1B

1C

...

10A

10B

...

```



\---



\## Q4 - Ocupación por ruta



Calcula el porcentaje de ocupación de una ruta dentro de un rango de fechas utilizando datos previamente agregados.



Resultado utilizado durante las pruebas:



```text

Ruta: GUA -> MEX

Reservas confirmadas: 1280

Capacidad total: 1920

Ocupación: 66.67 %

```



\---



\## Q5 - Top N por ingresos



Obtiene los vuelos con mayores ingresos dentro de un período.



La tabla está ordenada mediante:



```text

ingreso\_total DESC

```



por lo que Cassandra puede aplicar directamente:



```sql

LIMIT N

```



sin ordenar resultados en Python.



\---



\# TTL



Se realizó una prueba de expiración automática utilizando:



```sql

USING TTL 30

```



La reserva temporal mostró inicialmente un TTL restante y posteriormente fue eliminada automáticamente.



Resultado final:



```text

0 rows

```



\---



\# Tolerancia a fallos



Se evaluaron los niveles de consistencia:



```text

ONE

QUORUM

ALL

```



Cada nivel fue ejecutado 20 veces.



\## Tres nodos activos



```text

ONE     -> 20 éxitos / 0 errores

QUORUM  -> 20 éxitos / 0 errores

ALL     -> 20 éxitos / 0 errores

```



\## Un nodo caído



Se detuvo:



```text

cassandra3

```



Resultado:



```text

ONE     -> 20 éxitos / 0 errores

QUORUM  -> 20 éxitos / 0 errores

ALL     -> 0 éxitos / 20 errores

```



Error obtenido con ALL:



```text

Cannot achieve consistency level ALL

required\_replicas: 3

alive\_replicas: 2

```



\## Clúster recuperado



Después de iniciar nuevamente `cassandra3`:



```text

ONE     -> 20 éxitos / 0 errores

QUORUM  -> 20 éxitos / 0 errores

ALL     -> 20 éxitos / 0 errores

```



\---



\# Documentación



La documentación técnica completa se encuentra en:



```text

docs/documentacion\_tecnica.pdf

```



El manual de usuario se encuentra en:



```text

docs/manual\_usuario.pdf

```



El análisis Query-Driven se encuentra en:



```text

docs/diseno\_query\_driven.md

```



\---



\# Diagramas



Modelo conceptual:



```text

diagramas/modelo\_er\_conceptual.pdf

```



Modelo lógico Cassandra:



```text

diagramas/modelo\_logico\_cassandra.pdf

```



\---



\# Evidencias



Las evidencias del desarrollo se encuentran organizadas en:



```text

evidencias/cluster/

evidencias/carga/

evidencias/consultas/

evidencias/tolerancia\_fallos/

```



Incluyen:



\- Estado de los tres nodos.

\- Configuración del clúster.

\- Schema Agreement.

\- Replication Factor 3.

\- Carga de 100,000 reservas.

\- Resultados de las cinco consultas.

\- Prueba de TTL.

\- Caída de un nodo.

\- Pruebas ONE, QUORUM y ALL.

\- Recuperación del clúster.



\---



\# Detener el sistema



Para detener los contenedores:



```powershell

docker compose stop

```



Para reiniciarlos:



```powershell

docker compose start

```



Los datos permanecen almacenados en los volúmenes Docker.



No utilizar:



```powershell

docker compose down -v

```



si se desea conservar la información almacenada.



\---



\# Resultados finales



```text

Clúster Cassandra                  3 nodos

Apache Cassandra                   4.1.12

Replication Factor                 3

NetworkTopologyStrategy            Sí



Tablas                             11

Reservas                           100,000

Batch Writes                       20,000



Q1                                 Completada

Q2                                 Completada

Q3                                 Completada

Q4                                 Completada

Q5                                 Completada



JOIN                               No

ALLOW FILTERING                    No



TTL                                Validado

ONE                                Validado

QUORUM                             Validado

ALL                                Validado

Falla de nodo                      Validada

Recuperación                       Validada

```



\---



\## Autor



\*\*Carné:\*\* 202202072  

\*\*Universidad de San Carlos de Guatemala\*\*  

\*\*Ingeniería en Ciencias y Sistemas\*\*

