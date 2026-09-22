# MANUAL DE USUARIO



## Sistema de Gestión de Reservas y Boletos Aéreos con Apache Cassandra



**Universidad de San Carlos de Guatemala**  

**Facultad de Ingeniería**  

**Ingeniería en Ciencias y Sistemas**  

**Curso:** Sistemas de Bases de Datos 2  

**Proyecto:** Primer Proyecto  

**Carné:** 202202072  



---



# 1. Introducción



El presente manual describe el procedimiento necesario para instalar, configurar y ejecutar el Sistema de Gestión de Reservas y Boletos Aéreos desarrollado con Apache Cassandra.



El sistema utiliza un clúster Cassandra compuesto por tres nodos ejecutados mediante Docker Compose.



También utiliza scripts Python para:



- Verificar la conexión con Cassandra.

- Generar datos de prueba.

- Realizar la carga masiva de reservas.

- Ejecutar pruebas de consistencia y tolerancia a fallos.



---



# 2. Requisitos previos



Para ejecutar el proyecto se requiere:



- Windows 10 o superior.

- Docker Desktop.

- Docker Compose.

- Python 3.12.

- Git.

- PowerShell.



Las versiones utilizadas durante el desarrollo fueron:



```text

Apache Cassandra: 4.1.12

Python: 3.12

cassandra-driver: 3.30.1

Faker: 40.39.0

```



---



# 3. Estructura del proyecto



La estructura principal es:



```text

Primer Proyecto/

│

├── cql/

│   ├── 01_keyspace.cql

│   ├── 02_schema.cql

│   └── 03_queries.cql

│

├── scripts/

│   ├── 01_verificar_conexion.py

│   ├── 02_carga_prueba.py

│   ├── 03_carga_masiva.py

│   └── 04_prueba_tolerancia.py

│

├── diagramas/

│   ├── modelo_er_conceptual.mmd

│   ├── modelo_er_conceptual.pdf

│   ├── modelo_logico_cassandra.mmd

│   └── modelo_logico_cassandra.pdf

│

├── docs/

│   ├── diseno_query_driven.md

│   ├── documentacion_tecnica.md

│   └── manual_usuario.md

│

├── evidencias/

│   ├── carga/

│   ├── cluster/

│   ├── consultas/

│   └── tolerancia_fallos/

│

├── docker-compose.yml

└── requirements.txt

```



---



# 4. Abrir el proyecto



Abrir PowerShell y dirigirse a la carpeta del proyecto:



```powershell

cd "C:\Users\Admin\Documents\BD2_2S26_Proyectos_202202072\Primer Proyecto"

```



Todos los comandos de este manual deben ejecutarse desde esta ubicación, salvo que se indique lo contrario.



---



# 5. Levantar el clúster Cassandra



El proyecto utiliza tres nodos definidos en:



```text

docker-compose.yml

```



Para iniciar el clúster completo ejecutar:



```powershell

docker compose up -d

```



Docker iniciará:



```text

cassandra1

cassandra2

cassandra3

```



Los puertos publicados son:



```text

cassandra1 -> 9042

cassandra2 -> 9043

cassandra3 -> 9044

```



---



# 6. Verificar los contenedores



Ejecutar:



```powershell

docker compose ps

```



Se deben visualizar los tres contenedores con estado similar a:



```text

Up

```



También puede utilizarse:



```powershell

docker ps

```



---



# 7. Esperar el inicio de Cassandra



Aunque Docker indique que un contenedor se encuentra `Up`, Cassandra puede tardar algunos segundos adicionales en iniciar completamente.



Para verificar el clúster ejecutar:



```powershell

docker exec cassandra1 nodetool status

```



El resultado esperado debe contener tres nodos con estado:



```text

UN

```



donde:



```text

U = Up

N = Normal

```



Ejemplo:



```text

UN  nodo1

UN  nodo2

UN  nodo3

```



---



# 8. Verificar información del clúster



Ejecutar:



```powershell

docker exec cassandra1 nodetool describecluster

```



Se debe observar información similar a:



```text

Name: AerolineaCluster

Live: 3

Unreachable: 0

datacenter1 #Nodes: 3 #Down: 0

```



La versión utilizada durante el desarrollo fue:



```text

Apache Cassandra 4.1.12

```



---



# 9. Crear el keyspace



El archivo:



```text

cql/01_keyspace.cql

```



contiene la creación del keyspace:



```text

aerolinea

```



Para ejecutarlo:



```powershell

Get-Content -Raw .\cql\01_keyspace.cql | docker exec -i cassandra1 cqlsh

```



La configuración utiliza:



```text

NetworkTopologyStrategy

Replication Factor = 3

Datacenter = datacenter1

```



---



# 10. Verificar el keyspace



Ejecutar:



```powershell

docker exec cassandra1 cqlsh -e "SELECT keyspace_name, replication FROM system_schema.keyspaces WHERE keyspace_name = 'aerolinea';"

```



Debe observarse:



```text

NetworkTopologyStrategy

datacenter1: 3

```



También puede verificarse:



```powershell

docker exec cassandra1 nodetool status aerolinea

```



Los tres nodos deben mostrar:



```text

UN

```



y ownership efectivo del 100%.



---



# 11. Crear las tablas



El esquema Cassandra se encuentra en:



```text

cql/02_schema.cql

```



Para crearlo ejecutar:



```powershell

Get-Content -Raw .\cql\02_schema.cql | docker exec -i cassandra1 cqlsh

```



El proyecto crea 11 tablas.



---



# 12. Verificar las tablas



Ejecutar:



```powershell

docker exec cassandra1 cqlsh -e "SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'aerolinea';"

```



Se deben obtener 11 tablas:



```text

aeronaves_por_id

asientos_por_vuelo

disponibilidad_asientos_por_vuelo_clase

historial_reservas_por_pasajero

manifiesto_por_vuelo

ocupacion_por_ruta_mes

pagos_por_reserva

pasajeros_por_id

ranking_ingresos_por_periodo

reservas_por_id

vuelos_por_id

```



---



# 13. Crear el entorno virtual Python



Ejecutar:



```powershell

python -m venv .venv

```



El entorno se creará en:



```text

.venv/

```



---



# 14. Instalar dependencias Python



Las dependencias se encuentran en:



```text

requirements.txt

```



Para instalarlas:



```powershell

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

```



Las principales librerías utilizadas son:



```text

cassandra-driver

Faker

pyasyncore

```



`pyasyncore` es necesario para utilizar el driver Cassandra con Python 3.12 en este entorno.



---



# 15. Verificar conexión Python con Cassandra



Ejecutar:



```powershell

.\.venv\Scripts\python.exe scripts\01_verificar_conexion.py

```



Si la conexión es correcta se mostrará:



```text

Conexion establecida correctamente.

Keyspace actual: aerolinea

Version Cassandra: 4.1.12

```



También deben encontrarse:



```text

11 tablas

```



---



# 16. Carga de prueba



Antes de ejecutar la carga definitiva puede realizarse una prueba utilizando:



```powershell

.\.venv\Scripts\python.exe scripts\02_carga_prueba.py

```



El script genera:



```text

100 pasajeros

1 aeronave

10 vuelos

1,200 asientos

1,000 reservas

1,000 pagos

```



Esta carga se utiliza únicamente para validar el funcionamiento del modelo.



---



# 17. Carga masiva



La carga definitiva se realiza con:



```text

scripts/03_carga_masiva.py

```



Para generar las 100,000 reservas solicitadas:



```powershell

.\.venv\Scripts\python.exe -W ignore::DeprecationWarning -u scripts\03_carga_masiva.py --reservas 100000

```



El proceso realiza automáticamente la limpieza de las tablas antes de iniciar.



Por esta razón no debe ejecutarse nuevamente si se desea conservar la carga actual.



---



# 18. Resultado esperado de la carga



La carga definitiva genera aproximadamente:



```text

Reservas:      100,000

Pagos:         100,000

Pasajeros:       5,000

Aeronaves:          20

Vuelos:          1,000

Asientos:      120,000

```



También materializa las tablas necesarias para las cinco consultas principales.



Durante las pruebas realizadas se obtuvo:



```text

Confirmadas: 80,000

Pendientes:  10,000

Canceladas:  10,000

Batch Writes: 20,000

Tiempo total: 26.44 segundos

```



El tiempo puede variar según el equipo donde se ejecute.



---



# 19. Verificar cantidad de reservas



Ejecutar:



```powershell

docker exec cassandra1 cqlsh -e "SELECT COUNT(*) FROM aerolinea.reservas_por_id;"

```



El resultado esperado después de la carga definitiva es:



```text

100000

```



Cassandra puede mostrar:



```text

Aggregation query used without partition key

```



durante esta comprobación.



Esto es únicamente una advertencia debido a que se está realizando un conteo administrativo sobre toda la tabla.



Las consultas principales del sistema no utilizan este patrón.



---



# 20. Consultas principales



Las cinco consultas se encuentran almacenadas en:



```text

cql/03_queries.cql

```



No utilizan:



```text

JOIN

ALLOW FILTERING

```



Cada consulta utiliza una tabla diseñada específicamente para su patrón de acceso.



---



# 21. Consulta Q1 - Disponibilidad por clase



Objetivo:



Consultar cuántos asientos se encuentran disponibles y ocupados por clase para un vuelo.



Ejemplo:



```sql

SELECT

    clase,

    disponibles,

    ocupados

FROM disponibilidad_asientos_por_vuelo_clase

WHERE vuelo_id =

    7738e6e4-6f78-5a6a-9adc-1f33c41fe130;

```



Resultado obtenido:



```text

BUSINESS -> disponibles: 2, ocupados: 10

PREMIUM  -> disponibles: 1, ocupados: 17

ECONOMY  -> disponibles: 27, ocupados: 63

```



---



# 22. Consulta Q2 - Historial del pasajero



Objetivo:



Consultar el historial de reservas de un pasajero dentro de un rango de fechas.



Ejemplo:



```sql

SELECT

    fecha_salida,

    codigo_vuelo,

    aeropuerto_origen,

    aeropuerto_destino,

    numero_asiento,

    clase,

    estado_reserva,

    estado_pago,

    monto_pago

FROM historial_reservas_por_pasajero

WHERE pasajero_id =

    af65cd22-ae00-5a4a-8268-45d22029b352

  AND fecha_salida >= '2026-01-10T00:00:00Z'

  AND fecha_salida <= '2026-01-26T23:59:59Z';

```



Resultado obtenido durante la prueba:



```text

13 filas

```



Las filas se encuentran ordenadas de la fecha más reciente a la más antigua.



---



# 23. Consulta Q3 - Manifiesto de vuelo



Objetivo:



Obtener los pasajeros asignados a un vuelo ordenados por número de asiento.



Ejemplo:



```sql

SELECT

    numero_asiento,

    clase,

    nombre_pasajero,

    documento_identificacion,

    estado_reserva,

    estado_pago

FROM manifiesto_por_vuelo

WHERE vuelo_id =

    7738e6e4-6f78-5a6a-9adc-1f33c41fe130;

```



Resultado:



```text

100 filas

```



Orden:



```text

1A

1B

1C

...

10A

10B

...

```



---



# 24. Consulta Q4 - Ocupación por ruta



Objetivo:



Obtener el porcentaje de ocupación para una ruta dentro de un rango de fechas.



Ejemplo:



```sql

SELECT

    SUM(reservas_confirmadas) AS reservas_confirmadas,

    SUM(capacidad_total) AS capacidad_total,

    (CAST(SUM(reservas_confirmadas) AS decimal) * 100)

        / SUM(capacidad_total) AS porcentaje_ocupacion

FROM ocupacion_por_ruta_mes

WHERE origen = 'GUA'

  AND destino = 'MEX'

  AND anio_mes = '2026-01'

  AND fecha_salida >= '2026-01-01T00:00:00Z'

  AND fecha_salida <= '2026-01-31T23:59:59Z';

```



Resultado de la prueba:



```text

Reservas confirmadas: 1280

Capacidad total:      1920

Ocupación:            66.67 %

```



---



# 25. Consulta Q5 - Top N de vuelos por ingresos



Objetivo:



Obtener los vuelos con mayores ingresos dentro de un período determinado.



Ejemplo:



```sql

SELECT

    codigo_vuelo,

    fecha_salida,

    origen,

    destino,

    ingreso_total

FROM ranking_ingresos_por_periodo

WHERE fecha_inicio = '2026-01-01'

  AND fecha_fin = '2026-01-31'

ORDER BY ingreso_total DESC

LIMIT 10;

```



Resultado:



```text

10 vuelos

```



Durante la carga utilizada en el proyecto varios vuelos obtienen el mismo ingreso debido a la distribución uniforme de los datos generados.



---



# 26. Ejecutar el archivo de consultas



También es posible ejecutar el archivo completo mediante:



```powershell

Get-Content -Raw .\cql\03_queries.cql | docker exec -i cassandra1 cqlsh

```



Debe considerarse que el archivo también contiene una demostración de TTL.



---



# 27. Uso de TTL



El proyecto incluye una demostración de Time To Live.



La reserva temporal se crea utilizando:



```sql

USING TTL 30

```



Esto indica a Cassandra que los datos deben eliminarse automáticamente después de 30 segundos.



Ejemplo:



```sql

INSERT INTO reservas_por_id (

    reserva_id,

    pasajero_id,

    vuelo_id,

    numero_asiento,

    fecha_reserva,

    estado

)

VALUES (

    99999999-9999-4999-8999-999999999999,

    af65cd22-ae00-5a4a-8268-45d22029b352,

    7738e6e4-6f78-5a6a-9adc-1f33c41fe130,

    'TTL-TEST',

    toTimestamp(now()),

    'EXPIRABLE'

)

USING TTL 30;

```



---



# 28. Consultar el TTL restante



Ejecutar:



```sql

SELECT

    reserva_id,

    numero_asiento,

    estado,

    TTL(estado) AS ttl_restante

FROM reservas_por_id

WHERE reserva_id =

    99999999-9999-4999-8999-999999999999;

```



El valor de:



```text

ttl_restante

```



irá disminuyendo hasta que el registro expire.



Una vez transcurridos los 30 segundos la consulta debe devolver:



```text

0 rows

```



---



# 29. Pruebas de consistencia



El script:



```text

scripts/04_prueba_tolerancia.py

```



permite probar:



```text

ONE

QUORUM

ALL

```



Cada nivel se ejecuta 20 veces y se registran:



```text

Cantidad de éxitos

Cantidad de errores

Latencia mínima

Latencia promedio

Latencia máxima

```



---



# 30. Prueba con tres nodos activos



Primero verificar:



```powershell

docker exec cassandra1 nodetool status aerolinea

```



Los tres nodos deben encontrarse:



```text

UN

UN

UN

```



Ejecutar:



```powershell

.\.venv\Scripts\python.exe -u scripts\04_prueba_tolerancia.py --escenario 3_nodos

```



Con los tres nodos activos se espera que:



```text

ONE    -> funcione

QUORUM -> funcione

ALL    -> funcione

```



---



# 31. Simular la caída de un nodo



Detener `cassandra3`:



```powershell

docker stop cassandra3

```



Esperar algunos segundos y verificar:



```powershell

docker exec cassandra1 nodetool status aerolinea

```



Debe aparecer:



```text

cassandra1 -> UN

cassandra2 -> UN

cassandra3 -> DN

```



---



# 32. Ejecutar prueba con un nodo caído



Ejecutar:



```powershell

.\.venv\Scripts\python.exe -u scripts\04_prueba_tolerancia.py --escenario 1_nodo_caido

```



Con RF=3 se espera:



```text

ONE    -> funciona

QUORUM -> funciona

ALL    -> falla

```



El error esperado para `ALL` es similar a:



```text

Cannot achieve consistency level ALL

required_replicas: 3

alive_replicas: 2

```



Este comportamiento es correcto.



---



# 33. Recuperar el nodo



Ejecutar:



```powershell

docker start cassandra3

```



Esperar aproximadamente entre 20 y 40 segundos.



Verificar:



```powershell

docker exec cassandra1 nodetool status aerolinea

```



Los tres nodos deben regresar a:



```text

UN

UN

UN

```



---



# 34. Verificar recuperación



Ejecutar nuevamente:



```powershell

.\.venv\Scripts\python.exe -u scripts\04_prueba_tolerancia.py --escenario cluster_recuperado

```



Después de recuperar el nodo se espera:



```text

ONE    -> funciona

QUORUM -> funciona

ALL    -> funciona

```



---



# 35. Detener el sistema



Para detener los contenedores sin eliminarlos:



```powershell

docker compose stop

```



Los volúmenes persistentes conservarán los datos.



---



# 36. Reiniciar el sistema



Para iniciar nuevamente los contenedores:



```powershell

docker compose start

```



Después esperar a que Cassandra termine su proceso de inicio y verificar:



```powershell

docker exec cassandra1 nodetool status aerolinea

```



---



# 37. Eliminar el entorno Docker



Si se desea eliminar únicamente los contenedores y la red:



```powershell

docker compose down

```



Los volúmenes permanecerán almacenados.



No utilizar:



```powershell

docker compose down -v

```



si se desean conservar los datos, debido a que la opción `-v` elimina también los volúmenes del clúster.



---



# 38. Restaurar el proyecto desde cero



Si el proyecto se ejecuta en un equipo nuevo, el procedimiento general es:



```text

1. Instalar Docker Desktop.

2. Instalar Python 3.12.

3. Clonar el repositorio.

4. Abrir PowerShell en "Primer Proyecto".

5. Ejecutar docker compose up -d.

6. Esperar que los tres nodos estén UN.

7. Ejecutar cql/01_keyspace.cql.

8. Ejecutar cql/02_schema.cql.

9. Crear el entorno virtual Python.

10. Instalar requirements.txt.

11. Verificar conexión con 01_verificar_conexion.py.

12. Ejecutar 03_carga_masiva.py con 100000 reservas.

13. Ejecutar las consultas de cql/03_queries.cql.

```



---



# 39. Problemas comunes



## Cassandra todavía no está listo



Puede aparecer:



```text

No nodes present in the cluster.

Has this node finished starting up?

```



Solución:



Esperar algunos segundos y volver a ejecutar:



```powershell

docker exec cassandra1 nodetool status

```



---



## Python no puede utilizar cassandra-driver



En Python 3.12 puede aparecer un error relacionado con:



```text

asyncore

```



Verificar que esté instalada la dependencia:



```text

pyasyncore

```



Mediante:



```powershell

.\.venv\Scripts\python.exe -m pip install pyasyncore

```



---



## ALL falla durante la prueba de nodo caído



Esto es comportamiento esperado.



Con:



```text

RF = 3

```



el nivel:



```text

ALL

```



requiere las tres réplicas disponibles.



Si únicamente existen dos nodos activos, Cassandra no puede satisfacer ese nivel de consistencia.



---



## Warning durante COUNT(*)



Puede aparecer:



```text

Aggregation query used without partition key

```



Este warning aparece únicamente en verificaciones administrativas realizadas sobre tablas completas.



Las consultas Q1-Q5 utilizan sus correspondientes partition keys y no requieren ALLOW FILTERING.



---



# 40. Archivos de evidencia



Los resultados de las pruebas realizadas se encuentran en:



```text

evidencias/cluster/

evidencias/carga/

evidencias/consultas/

evidencias/tolerancia_fallos/

```



Estos archivos permiten verificar:



- Estado de los tres nodos.

- Replication Factor.

- Schema Agreement.

- Carga de 100,000 reservas.

- Ejecución de las cinco consultas.

- Funcionamiento de TTL.

- Caída de un nodo.

- Comportamiento de ONE, QUORUM y ALL.

- Recuperación del clúster.



---



# 41. Consideraciones finales



El sistema debe ejecutarse con los tres nodos disponibles durante su funcionamiento normal.



El uso de Replication Factor 3 permite mantener una copia de los datos en cada nodo del clúster.



Las consultas principales no deben modificarse para utilizar JOIN o ALLOW FILTERING, ya que el esquema fue diseñado específicamente para resolverlas mediante acceso directo a particiones.



La carga masiva puede volver a ejecutarse indicando otra cantidad mediante:



```powershell

.\.venv\Scripts\python.exe scripts\03_carga_masiva.py --reservas CANTIDAD

```



Debe recordarse que el script limpia las tablas antes de realizar cada nueva carga.



Para la entrega final se recomienda mantener los tres nodos en estado `UN`.


