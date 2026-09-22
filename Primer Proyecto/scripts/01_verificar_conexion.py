from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement


def main():
    cluster = None

    try:
        print("Conectando con Apache Cassandra...")

        # Cassandra 1 está expuesto desde Docker en localhost:9042
        cluster = Cluster(
            contact_points=["127.0.0.1"],
            port=9042
        )

        session = cluster.connect("aerolinea")

        print("Conexion establecida correctamente.")
        print(f"Keyspace actual: {session.keyspace}")

        # ------------------------------------------------------
        # Comprobar versión de Cassandra
        # ------------------------------------------------------

        version = session.execute(
            "SELECT release_version FROM system.local"
        ).one()

        print(f"Version Cassandra: {version.release_version}")

        # ------------------------------------------------------
        # Comprobar las tablas del proyecto
        # ------------------------------------------------------

        consulta_tablas = SimpleStatement(
            """
            SELECT table_name
            FROM system_schema.tables
            WHERE keyspace_name = 'aerolinea'
            """,
            consistency_level=ConsistencyLevel.ONE
        )

        filas = session.execute(consulta_tablas)

        tablas = sorted([fila.table_name for fila in filas])

        print(f"\nTablas encontradas: {len(tablas)}")

        for tabla in tablas:
            print(f" - {tabla}")

        if len(tablas) == 11:
            print("\nValidacion correcta: se encontraron las 11 tablas esperadas.")
        else:
            print(
                f"\nAdvertencia: se esperaban 11 tablas y se encontraron {len(tablas)}."
            )

    except Exception as error:
        print("\nERROR AL CONECTAR CON CASSANDRA")
        print(type(error).__name__)
        print(error)

    finally:
        if cluster is not None:
            cluster.shutdown()
            print("\nConexion cerrada.")


if __name__ == "__main__":
    main()