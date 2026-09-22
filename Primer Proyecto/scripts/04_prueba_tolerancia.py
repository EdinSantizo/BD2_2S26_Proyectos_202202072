import argparse
import statistics
import time

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement


TOTAL_PRUEBAS = 20

VUELO_ID = "7738e6e4-6f78-5a6a-9adc-1f33c41fe130"

CONSISTENCIAS = [
    ("ONE", ConsistencyLevel.ONE),
    ("QUORUM", ConsistencyLevel.QUORUM),
    ("ALL", ConsistencyLevel.ALL),
]


def ejecutar_pruebas(session, nombre, nivel):
    consulta = SimpleStatement(
        f"""
        SELECT clase, disponibles, ocupados
        FROM disponibilidad_asientos_por_vuelo_clase
        WHERE vuelo_id = {VUELO_ID}
        """,
        consistency_level=nivel
    )

    tiempos = []
    exitos = 0
    errores = 0
    ultimo_error = None

    for _ in range(TOTAL_PRUEBAS):
        inicio = time.perf_counter()

        try:
            resultado = session.execute(consulta)

            # Forzar la lectura completa del resultado.
            list(resultado)

            fin = time.perf_counter()

            tiempos.append(
                (fin - inicio) * 1000
            )

            exitos += 1

        except Exception as error:
            fin = time.perf_counter()

            tiempos.append(
                (fin - inicio) * 1000
            )

            errores += 1

            ultimo_error = (
                f"{type(error).__name__}: {error}"
            )

    print()
    print("-" * 60)
    print(f"CONSISTENCY LEVEL: {nombre}")
    print("-" * 60)

    print(f"Pruebas ejecutadas : {TOTAL_PRUEBAS}")
    print(f"Exitos             : {exitos}")
    print(f"Errores            : {errores}")

    if tiempos:
        print(
            f"Latencia minima    : "
            f"{min(tiempos):.3f} ms"
        )

        print(
            f"Latencia promedio  : "
            f"{statistics.mean(tiempos):.3f} ms"
        )

        print(
            f"Latencia maxima    : "
            f"{max(tiempos):.3f} ms"
        )

    if ultimo_error is not None:
        print()
        print("Ultimo error:")
        print(ultimo_error)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Prueba de tolerancia a fallos "
            "ONE / QUORUM / ALL"
        )
    )

    parser.add_argument(
        "--escenario",
        required=True,
        help=(
            "Nombre del escenario, por ejemplo: "
            "3_nodos o 1_nodo_caido"
        )
    )

    args = parser.parse_args()

    print("=" * 60)
    print("PRUEBA DE CONSISTENCIA Y TOLERANCIA A FALLOS")
    print("=" * 60)
    print(f"Escenario: {args.escenario}")
    print(f"Repeticiones por nivel: {TOTAL_PRUEBAS}")
    print(f"Vuelo utilizado: {VUELO_ID}")

    cluster = Cluster(
        contact_points=["127.0.0.1"],
        port=9042
    )

    try:
        session = cluster.connect("aerolinea")

        for nombre, nivel in CONSISTENCIAS:
            ejecutar_pruebas(
                session,
                nombre,
                nivel
            )

    finally:
        cluster.shutdown()

    print()
    print("=" * 60)
    print("PRUEBA FINALIZADA")
    print("=" * 60)


if __name__ == "__main__":
    main()