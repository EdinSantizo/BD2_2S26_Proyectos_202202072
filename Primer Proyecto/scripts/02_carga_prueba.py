import time
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import NAMESPACE_DNS, uuid5

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
from faker import Faker


TOTAL_RESERVAS = 1000
TOTAL_PASAJEROS = 100
TOTAL_VUELOS = 10
CAPACIDAD_VUELO = 120
LETRAS = "ABCDEF"


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


def nuevo_batch():
    return BatchStatement(
        batch_type=BatchType.UNLOGGED,
        consistency_level=ConsistencyLevel.ONE
    )


def main():
    inicio = time.perf_counter()

    Faker.seed(202202072)
    fake = Faker("es_MX")

    cluster = Cluster(
        contact_points=["127.0.0.1"],
        port=9042
    )

    session = cluster.connect("aerolinea")
    session.default_timeout = 60

    try:
        # =====================================================
        # LIMPIEZA
        # =====================================================

        print("Limpiando tablas antes de la prueba...")

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

        print("Tablas limpias.")

        # =====================================================
        # PREPARED STATEMENTS
        # =====================================================

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

        # =====================================================
        # PASAJEROS
        # =====================================================

        print("Cargando pasajeros...")

        pasajeros = []

        for i in range(TOTAL_PASAJEROS):
            pasajero = {
                "id": uid("pasajero", i),
                "nombre": fake.name(),
                "email": fake.email(),
                "documento": f"DOC-{i + 1:05d}",
                "telefono": f"5{i + 1000000:07d}"
            }

            pasajeros.append(pasajero)

            session.execute(
                insertar_pasajero,
                (
                    pasajero["id"],
                    pasajero["nombre"],
                    pasajero["email"],
                    pasajero["documento"],
                    pasajero["telefono"],
                    "Guatemala"
                )
            )

        # =====================================================
        # AERONAVE
        # =====================================================

        print("Cargando aeronave...")

        aeronave_id = uid("aeronave", 1)

        session.execute(
            insertar_aeronave,
            (
                aeronave_id,
                "Airbus A320",
                "Aerolinea Demo",
                "TG-001",
                CAPACIDAD_VUELO
            )
        )

        # =====================================================
        # VUELOS Y ASIENTOS
        # =====================================================

        print("Cargando vuelos y asientos...")

        vuelos = []
        fecha_base = datetime(2026, 1, 1, 8, 0, 0)

        for i in range(TOTAL_VUELOS):

            vuelo = {
                "id": uid("vuelo", i),
                "codigo": f"GT{i + 1:03d}",
                "salida": fecha_base + timedelta(days=i),
                "origen": "GUA",
                "destino": "MEX" if i % 2 == 0 else "SAL"
            }

            vuelos.append(vuelo)

            session.execute(
                insertar_vuelo,
                (
                    vuelo["id"],
                    vuelo["codigo"],
                    aeronave_id,
                    vuelo["origen"],
                    vuelo["destino"],
                    vuelo["salida"],
                    vuelo["salida"] + timedelta(hours=2),
                    "PROGRAMADO"
                )
            )

            batch_asientos = nuevo_batch()

            for posicion in range(CAPACIDAD_VUELO):

                numero, fila, letra, clase = obtener_asiento(
                    posicion
                )

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
                        "DISPONIBLE"
                    )
                )

                # 40 asientos por batch.
                if (posicion + 1) % 40 == 0:
                    session.execute(batch_asientos)
                    batch_asientos = nuevo_batch()

        # =====================================================
        # RESERVAS
        # =====================================================

        print(
            "Cargando 1,000 reservas mediante Batch Writes..."
        )

        batch = nuevo_batch()
        reservas_en_batch = 0

        for i in range(TOTAL_RESERVAS):

            indice_vuelo = i % TOTAL_VUELOS
            vuelo = vuelos[indice_vuelo]

            indice_pasajero = (
                i * 37 + i // TOTAL_VUELOS
            ) % TOTAL_PASAJEROS

            pasajero = pasajeros[indice_pasajero]

            # Cada vuelo recibe 100 reservas.
            posicion = i // TOTAL_VUELOS

            numero, fila, letra, clase = obtener_asiento(
                posicion
            )

            reserva_id = uid("reserva", i)
            pago_id = uid("pago", i)

            fecha_reserva = vuelo["salida"] - timedelta(
                days=(i % 30) + 1
            )

            # 80 % confirmadas
            # 10 % pendientes
            # 10 % canceladas

            if i % 10 == 0:
                estado_reserva = "CANCELADA"
                estado_pago = "REEMBOLSADO"

            elif i % 10 == 1:
                estado_reserva = "PENDIENTE"
                estado_pago = "PENDIENTE"

            else:
                estado_reserva = "CONFIRMADA"
                estado_pago = "PAGADO"

            if clase == "BUSINESS":
                monto = Decimal("650.00")

            elif clase == "PREMIUM":
                monto = Decimal("350.00")

            else:
                monto = Decimal("150.00")

            # ---------------------------------------------
            # Escritura 1: reserva base
            # ---------------------------------------------

            batch.add(
                insertar_reserva,
                (
                    reserva_id,
                    pasajero["id"],
                    vuelo["id"],
                    numero,
                    fecha_reserva,
                    estado_reserva
                )
            )

            # ---------------------------------------------
            # Escritura 2: pago
            # ---------------------------------------------

            batch.add(
                insertar_pago,
                (
                    reserva_id,
                    pago_id,
                    monto,
                    "TARJETA",
                    fecha_reserva + timedelta(hours=1),
                    estado_pago
                )
            )

            # ---------------------------------------------
            # Escritura 3: Q2
            # ---------------------------------------------

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
                    monto
                )
            )

            # ---------------------------------------------
            # Escritura 4: Q3
            # ---------------------------------------------

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
                    estado_pago
                )
            )

            reservas_en_batch += 1

            # 5 reservas x 4 escrituras
            # = 20 statements por Batch Write.
            if reservas_en_batch == 5:

                session.execute(batch)

                batch = nuevo_batch()
                reservas_en_batch = 0

        if reservas_en_batch > 0:
            session.execute(batch)

        duracion = time.perf_counter() - inicio

        print()
        print("Carga de prueba finalizada correctamente.")
        print(f"Reservas cargadas: {TOTAL_RESERVAS:,}")
        print(f"Tiempo total: {duracion:.2f} segundos")

    finally:
        cluster.shutdown()


if __name__ == "__main__":
    main()