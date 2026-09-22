import argparse
import calendar
import math
import time
from datetime import datetime, timedelta, date
from decimal import Decimal
from uuid import NAMESPACE_DNS, uuid5

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
from faker import Faker


# ============================================================
# CONFIGURACION GENERAL
# ============================================================

CAPACIDAD_VUELO = 120
RESERVAS_POR_VUELO = 100
LETRAS = "ABCDEF"

TAMANO_BATCH_RESERVAS = 5
MAX_OPERACIONES_ASINCRONAS = 50

RUTAS = [
    ("GUA", "MEX"),
    ("GUA", "SAL"),
    ("GUA", "SJO"),
    ("GUA", "PTY"),
    ("MEX", "GUA"),
    ("SAL", "GUA"),
]


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def uid(tipo, numero):
    return uuid5(
        NAMESPACE_DNS,
        f"bd2-202202072-{tipo}-{numero}"
    )


def obtener_asiento(indice):
    fila = (indice // 6) + 1
    letra = LETRAS[indice % 6]

    if fila <= 2:
        clase = "BUSINESS"
    elif fila <= 5:
        clase = "PREMIUM"
    else:
        clase = "ECONOMY"

    return f"{fila}{letra}", fila, letra, clase


def obtener_monto(clase):
    if clase == "BUSINESS":
        return Decimal("650.00")

    if clase == "PREMIUM":
        return Decimal("350.00")

    return Decimal("150.00")


def obtener_estado(indice):
    """
    Distribucion:
        80 % confirmadas
        10 % pendientes
        10 % canceladas
    """

    valor = indice % 10

    if valor == 0:
        return "CANCELADA", "REEMBOLSADO"

    if valor == 1:
        return "PENDIENTE", "PENDIENTE"

    return "CONFIRMADA", "PAGADO"


def nuevo_batch():
    return BatchStatement(
        batch_type=BatchType.UNLOGGED,
        consistency_level=ConsistencyLevel.ONE
    )


def esperar_pendientes(pendientes):
    for future in pendientes:
        future.result()

    pendientes.clear()


def enviar_async(session, consulta, pendientes, parametros=None):
    if parametros is None:
        future = session.execute_async(consulta)
    else:
        future = session.execute_async(
            consulta,
            parametros
        )

    pendientes.append(future)

    if len(pendientes) >= MAX_OPERACIONES_ASINCRONAS:
        esperar_pendientes(pendientes)


def limpiar_tablas(session):
    print("Limpiando tablas...")

    tablas = [
        "ranking_ingresos_por_periodo",
        "ocupacion_por_ruta_mes",
        "manifiesto_por_vuelo",
        "historial_reservas_por_pasajero",
        "disponibilidad_asientos_por_vuelo_clase",
        "pagos_por_reserva",
        "reservas_por_id",
        "asientos_por_vuelo",
        "vuelos_por_id",
        "aeronaves_por_id",
        "pasajeros_por_id",
    ]

    for tabla in tablas:
        session.execute(f"TRUNCATE {tabla}")

    print("Tablas limpias correctamente.")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Carga masiva de datos para el proyecto Cassandra"
    )

    parser.add_argument(
        "--reservas",
        type=int,
        default=100000,
        help="Cantidad de reservas a generar"
    )

    args = parser.parse_args()

    total_reservas = args.reservas

    if total_reservas <= 0:
        raise ValueError(
            "La cantidad de reservas debe ser mayor que cero."
        )

    total_vuelos = math.ceil(
        total_reservas / RESERVAS_POR_VUELO
    )

    total_pasajeros = min(
        5000,
        max(
            100,
            total_reservas // 20
        )
    )

    total_aeronaves = min(
        20,
        max(
            1,
            math.ceil(total_vuelos / 50)
        )
    )

    inicio_total = time.perf_counter()

    Faker.seed(202202072)
    fake = Faker("es_MX")

    print("=" * 60)
    print("CARGA MASIVA - APACHE CASSANDRA")
    print("=" * 60)
    print(f"Reservas solicitadas : {total_reservas:,}")
    print(f"Pasajeros            : {total_pasajeros:,}")
    print(f"Aeronaves            : {total_aeronaves:,}")
    print(f"Vuelos               : {total_vuelos:,}")
    print(
        f"Asientos aproximados : "
        f"{total_vuelos * CAPACIDAD_VUELO:,}"
    )
    print()

    cluster = Cluster(
        contact_points=["127.0.0.1"],
        port=9042
    )

    session = cluster.connect("aerolinea")

    session.default_timeout = 120

    # Este ajuste funciona correctamente con cassandra-driver 3.30.1.
    # Puede mostrar un DeprecationWarning, pero no afecta el proyecto.
    session.default_consistency_level = ConsistencyLevel.ONE

    pendientes = []

    try:

        # ====================================================
        # LIMPIEZA
        # ====================================================

        limpiar_tablas(session)

        # ====================================================
        # PREPARED STATEMENTS
        # ====================================================

        print("\nPreparando sentencias CQL...")

        insertar_pasajero = session.prepare("""
            INSERT INTO pasajeros_por_id
            (
                pasajero_id,
                nombre,
                email,
                documento_identificacion,
                telefono,
                nacionalidad
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """)

        insertar_aeronave = session.prepare("""
            INSERT INTO aeronaves_por_id
            (
                aeronave_id,
                modelo,
                aerolinea_operadora,
                matricula,
                capacidad_maxima
            )
            VALUES (?, ?, ?, ?, ?)
        """)

        insertar_vuelo = session.prepare("""
            INSERT INTO vuelos_por_id
            (
                vuelo_id,
                codigo_vuelo,
                aeronave_id,
                aeropuerto_origen,
                aeropuerto_destino,
                fecha_hora_salida,
                fecha_hora_llegada,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """)

        insertar_asiento = session.prepare("""
            INSERT INTO asientos_por_vuelo
            (
                vuelo_id,
                numero_asiento,
                asiento_id,
                fila_asiento,
                letra_asiento,
                clase,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        insertar_reserva = session.prepare("""
            INSERT INTO reservas_por_id
            (
                reserva_id,
                pasajero_id,
                vuelo_id,
                numero_asiento,
                fecha_reserva,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """)

        insertar_pago = session.prepare("""
            INSERT INTO pagos_por_reserva
            (
                reserva_id,
                pago_id,
                monto,
                metodo_pago,
                fecha_pago,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """)

        insertar_historial = session.prepare("""
            INSERT INTO historial_reservas_por_pasajero
            (
                pasajero_id,
                fecha_salida,
                reserva_id,
                codigo_vuelo,
                aeropuerto_origen,
                aeropuerto_destino,
                fecha_reserva,
                numero_asiento,
                clase,
                estado_reserva,
                estado_pago,
                monto_pago
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)

        insertar_manifiesto = session.prepare("""
            INSERT INTO manifiesto_por_vuelo
            (
                vuelo_id,
                fila_asiento,
                letra_asiento,
                numero_asiento,
                reserva_id,
                pasajero_id,
                nombre_pasajero,
                documento_identificacion,
                clase,
                estado_reserva,
                estado_pago
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)

        actualizar_disponibilidad = session.prepare("""
            UPDATE disponibilidad_asientos_por_vuelo_clase
            SET
                disponibles = disponibles + ?,
                ocupados = ocupados + ?
            WHERE
                vuelo_id = ?
                AND clase = ?
        """)

        actualizar_ocupacion = session.prepare("""
            UPDATE ocupacion_por_ruta_mes
            SET
                reservas_confirmadas =
                    reservas_confirmadas + ?,
                capacidad_total =
                    capacidad_total + ?
            WHERE
                origen = ?
                AND destino = ?
                AND anio_mes = ?
                AND fecha_salida = ?
                AND vuelo_id = ?
        """)

        insertar_ranking = session.prepare("""
            INSERT INTO ranking_ingresos_por_periodo
            (
                fecha_inicio,
                fecha_fin,
                ingreso_total,
                vuelo_id,
                codigo_vuelo,
                fecha_salida,
                origen,
                destino
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """)

        # ====================================================
        # PASAJEROS
        # ====================================================

        print("\nCargando pasajeros...")

        pasajeros = []

        for i in range(total_pasajeros):
            pasajero = {
                "id": uid("pasajero", i),
                "nombre": fake.name(),
                "email": fake.email(),
                "documento": f"DOC-{i + 1:06d}",
                "telefono": f"5{i + 1000000:07d}",
            }

            pasajeros.append(pasajero)

            enviar_async(
                session,
                insertar_pasajero,
                pendientes,
                (
                    pasajero["id"],
                    pasajero["nombre"],
                    pasajero["email"],
                    pasajero["documento"],
                    pasajero["telefono"],
                    "Guatemala",
                )
            )

        esperar_pendientes(pendientes)

        print(
            f"Pasajeros cargados: {len(pasajeros):,}"
        )

        # ====================================================
        # AERONAVES
        # ====================================================

        print("\nCargando aeronaves...")

        aeronaves = []

        modelos = [
            "Airbus A320",
            "Boeing 737-800",
            "Airbus A319",
        ]

        for i in range(total_aeronaves):
            aeronave = {
                "id": uid("aeronave", i),
                "modelo": modelos[i % len(modelos)],
                "matricula": f"TG-A{i + 1:03d}",
            }

            aeronaves.append(aeronave)

            enviar_async(
                session,
                insertar_aeronave,
                pendientes,
                (
                    aeronave["id"],
                    aeronave["modelo"],
                    "AeroGuate",
                    aeronave["matricula"],
                    CAPACIDAD_VUELO,
                )
            )

        esperar_pendientes(pendientes)

        print(
            f"Aeronaves cargadas: {len(aeronaves):,}"
        )

        # ====================================================
        # VUELOS Y ASIENTOS
        # ====================================================

        print("\nCargando vuelos y asientos...")

        vuelos = []

        fecha_base = datetime(
            2026,
            1,
            1,
            6,
            0,
            0
        )

        for i in range(total_vuelos):

            origen, destino = RUTAS[
                i % len(RUTAS)
            ]

            fecha_salida = (
                fecha_base
                + timedelta(hours=i * 8)
            )

            vuelo = {
                "id": uid("vuelo", i),
                "codigo": f"AG{i + 1:04d}",
                "aeronave_id": aeronaves[
                    i % len(aeronaves)
                ]["id"],
                "origen": origen,
                "destino": destino,
                "salida": fecha_salida,
            }

            vuelos.append(vuelo)

            enviar_async(
                session,
                insertar_vuelo,
                pendientes,
                (
                    vuelo["id"],
                    vuelo["codigo"],
                    vuelo["aeronave_id"],
                    vuelo["origen"],
                    vuelo["destino"],
                    vuelo["salida"],
                    vuelo["salida"]
                    + timedelta(hours=2),
                    "PROGRAMADO",
                )
            )

            batch_asientos = nuevo_batch()

            for posicion in range(
                CAPACIDAD_VUELO
            ):

                numero, fila, letra, clase = (
                    obtener_asiento(posicion)
                )

                indice_global_reserva = (
                    i * RESERVAS_POR_VUELO
                    + posicion
                )

                tiene_reserva = (
                    posicion < RESERVAS_POR_VUELO
                    and
                    indice_global_reserva
                    < total_reservas
                )

                estado_asiento = "DISPONIBLE"

                if tiene_reserva:
                    estado_reserva, _ = obtener_estado(
                        indice_global_reserva
                    )

                    if estado_reserva != "CANCELADA":
                        estado_asiento = "OCUPADO"

                batch_asientos.add(
                    insertar_asiento,
                    (
                        vuelo["id"],
                        numero,
                        uid(
                            "asiento",
                            i * 1000 + posicion
                        ),
                        fila,
                        letra,
                        clase,
                        estado_asiento,
                    )
                )

                if (
                    (posicion + 1) % 40 == 0
                ):
                    enviar_async(
                        session,
                        batch_asientos,
                        pendientes
                    )

                    batch_asientos = nuevo_batch()

        esperar_pendientes(pendientes)

        print(
            f"Vuelos cargados: {len(vuelos):,}"
        )

        print(
            "Asientos cargados: "
            f"{len(vuelos) * CAPACIDAD_VUELO:,}"
        )

        # ====================================================
        # RESERVAS
        # ====================================================

        print("\nCargando reservas mediante Batch Writes...")

        total_confirmadas = 0
        total_pendientes = 0
        total_canceladas = 0

        total_batches = 0
        reserva_global = 0

        agregados_vuelos = []

        for indice_vuelo, vuelo in enumerate(
            vuelos
        ):

            restantes = (
                total_reservas
                - reserva_global
            )

            reservas_este_vuelo = min(
                RESERVAS_POR_VUELO,
                restantes
            )

            if reservas_este_vuelo <= 0:
                break

            ocupados_por_clase = {
                "BUSINESS": 0,
                "PREMIUM": 0,
                "ECONOMY": 0,
            }

            confirmadas_vuelo = 0
            ingreso_vuelo = Decimal("0.00")

            batch = nuevo_batch()
            reservas_en_batch = 0

            for posicion in range(
                reservas_este_vuelo
            ):

                indice = reserva_global

                pasajero = pasajeros[
                    (
                        indice * 37
                        + indice_vuelo * 13
                    )
                    % total_pasajeros
                ]

                numero, fila, letra, clase = (
                    obtener_asiento(posicion)
                )

                estado_reserva, estado_pago = (
                    obtener_estado(indice)
                )

                monto = obtener_monto(clase)

                if estado_reserva == "CONFIRMADA":
                    total_confirmadas += 1
                    confirmadas_vuelo += 1
                    ingreso_vuelo += monto

                elif estado_reserva == "PENDIENTE":
                    total_pendientes += 1

                else:
                    total_canceladas += 1

                if estado_reserva != "CANCELADA":
                    ocupados_por_clase[
                        clase
                    ] += 1

                reserva_id = uid(
                    "reserva",
                    indice
                )

                pago_id = uid(
                    "pago",
                    indice
                )

                fecha_reserva = (
                    vuelo["salida"]
                    - timedelta(
                        days=(indice % 60) + 1
                    )
                )

                # ------------------------------------------
                # Reserva base
                # ------------------------------------------

                batch.add(
                    insertar_reserva,
                    (
                        reserva_id,
                        pasajero["id"],
                        vuelo["id"],
                        numero,
                        fecha_reserva,
                        estado_reserva,
                    )
                )

                # ------------------------------------------
                # Pago
                # ------------------------------------------

                batch.add(
                    insertar_pago,
                    (
                        reserva_id,
                        pago_id,
                        monto,
                        "TARJETA",
                        fecha_reserva
                        + timedelta(hours=1),
                        estado_pago,
                    )
                )

                # ------------------------------------------
                # Q2 - Historial del pasajero
                # ------------------------------------------

                batch.add(
                    insertar_historial,
                    (
                        pasajero["id"],
                        vuelo["salida"],
                        reserva_id,
                        vuelo["codigo"],
                        vuelo["origen"],
                        vuelo["destino"],
                        fecha_reserva,
                        numero,
                        clase,
                        estado_reserva,
                        estado_pago,
                        monto,
                    )
                )

                # ------------------------------------------
                # Q3 - Manifiesto
                # ------------------------------------------

                batch.add(
                    insertar_manifiesto,
                    (
                        vuelo["id"],
                        fila,
                        letra,
                        numero,
                        reserva_id,
                        pasajero["id"],
                        pasajero["nombre"],
                        pasajero["documento"],
                        clase,
                        estado_reserva,
                        estado_pago,
                    )
                )

                reservas_en_batch += 1
                reserva_global += 1

                if (
                    reservas_en_batch
                    == TAMANO_BATCH_RESERVAS
                ):

                    enviar_async(
                        session,
                        batch,
                        pendientes
                    )

                    total_batches += 1

                    batch = nuevo_batch()
                    reservas_en_batch = 0

                if (
                    reserva_global % 10000 == 0
                    or
                    reserva_global
                    == total_reservas
                ):
                    print(
                        "  Progreso: "
                        f"{reserva_global:,}"
                        f"/{total_reservas:,}"
                    )

            if reservas_en_batch > 0:
                enviar_async(
                    session,
                    batch,
                    pendientes
                )

                total_batches += 1

            agregados_vuelos.append(
                {
                    "vuelo": vuelo,
                    "ocupados": ocupados_por_clase,
                    "confirmadas": confirmadas_vuelo,
                    "ingreso": ingreso_vuelo,
                }
            )

        esperar_pendientes(pendientes)

        # ====================================================
        # Q1 - DISPONIBILIDAD
        # ====================================================

        print(
            "\nInicializando contadores de "
            "disponibilidad Q1..."
        )

        capacidades = {
            "BUSINESS": 12,
            "PREMIUM": 18,
            "ECONOMY": 90,
        }

        for agregado in agregados_vuelos:

            vuelo = agregado["vuelo"]

            for clase, capacidad in (
                capacidades.items()
            ):

                ocupados = agregado[
                    "ocupados"
                ][clase]

                disponibles = (
                    capacidad - ocupados
                )

                enviar_async(
                    session,
                    actualizar_disponibilidad,
                    pendientes,
                    (
                        disponibles,
                        ocupados,
                        vuelo["id"],
                        clase,
                    )
                )

        esperar_pendientes(pendientes)

        # ====================================================
        # Q4 - OCUPACION POR RUTA/MES
        # ====================================================

        print(
            "Inicializando agregados de ocupacion Q4..."
        )

        for agregado in agregados_vuelos:

            vuelo = agregado["vuelo"]

            anio_mes = vuelo[
                "salida"
            ].strftime("%Y-%m")

            enviar_async(
                session,
                actualizar_ocupacion,
                pendientes,
                (
                    agregado["confirmadas"],
                    CAPACIDAD_VUELO,
                    vuelo["origen"],
                    vuelo["destino"],
                    anio_mes,
                    vuelo["salida"],
                    vuelo["id"],
                )
            )

        esperar_pendientes(pendientes)

        # ====================================================
        # Q5 - RANKING DE INGRESOS
        # ====================================================

        print(
            "Materializando ranking de ingresos Q5..."
        )

        for agregado in agregados_vuelos:

            vuelo = agregado["vuelo"]

            anio = vuelo["salida"].year
            mes = vuelo["salida"].month

            fecha_inicio = date(
                anio,
                mes,
                1
            )

            ultimo_dia = calendar.monthrange(
                anio,
                mes
            )[1]

            fecha_fin = date(
                anio,
                mes,
                ultimo_dia
            )

            enviar_async(
                session,
                insertar_ranking,
                pendientes,
                (
                    fecha_inicio,
                    fecha_fin,
                    agregado["ingreso"],
                    vuelo["id"],
                    vuelo["codigo"],
                    vuelo["salida"],
                    vuelo["origen"],
                    vuelo["destino"],
                )
            )

        esperar_pendientes(pendientes)

        # ====================================================
        # RESULTADOS
        # ====================================================

        duracion = (
            time.perf_counter()
            - inicio_total
        )

        print()
        print("=" * 60)
        print("CARGA FINALIZADA CORRECTAMENTE")
        print("=" * 60)

        print(
            f"Reservas totales   : "
            f"{reserva_global:,}"
        )

        print(
            f"Confirmadas        : "
            f"{total_confirmadas:,}"
        )

        print(
            f"Pendientes         : "
            f"{total_pendientes:,}"
        )

        print(
            f"Canceladas         : "
            f"{total_canceladas:,}"
        )

        print(
            f"Batch Writes       : "
            f"{total_batches:,}"
        )

        print(
            "Statements/reserva : 4"
        )

        print(
            f"Tiempo total       : "
            f"{duracion:.2f} segundos"
        )

        print()
        print(
            f"Vuelo ejemplo      : "
            f"{vuelos[0]['id']}"
        )

        print(
            f"Codigo vuelo       : "
            f"{vuelos[0]['codigo']}"
        )

        print(
            f"Pasajero ejemplo   : "
            f"{pasajeros[0]['id']}"
        )

        print()
        print(
            "Las tablas Q1, Q4 y Q5 tambien "
            "fueron materializadas."
        )

    finally:
        cluster.shutdown()


if __name__ == "__main__":
    main()