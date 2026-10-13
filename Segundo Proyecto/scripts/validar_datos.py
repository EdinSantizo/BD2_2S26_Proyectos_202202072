
"""
Proyecto 2 - Sistemas de Bases de Datos 2
Validacion de archivos CSV antes de LOAD CSV.
"""

import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
NODOS = BASE / "data" / "nodos"
RELACIONES = BASE / "data" / "relaciones"


def leer(carpeta, archivo):
    ruta = carpeta / archivo
    with ruta.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        return list(csv.DictReader(f))


# =========================================
# 1. VALIDAR NODOS
# =========================================

definiciones = {
    "usuarios.csv": (500, "id"),
    "restaurantes.csv": (200, "id"),
    "chefs.csv": (100, "id"),
    "platillos.csv": (50, "id"),
    "tipos_cocina.csv": (15, "id"),
}

ids_nodos = {}

print("===== VALIDACION DE NODOS =====")

for archivo, (cantidad, campo) in definiciones.items():
    filas = leer(NODOS, archivo)
    ids = [int(fila[campo]) for fila in filas]

    assert len(filas) == cantidad, (
        f"Cantidad incorrecta en {archivo}"
    )

    assert len(ids) == len(set(ids)), (
        f"IDs duplicados en {archivo}"
    )

    ids_nodos[archivo] = set(ids)
    print(f"OK - {archivo}: {len(filas)} nodos")

usuarios = leer(NODOS, "usuarios.csv")
emails = [u["email"] for u in usuarios]

assert len(emails) == len(set(emails)), (
    "Existen emails duplicados"
)


# =========================================
# 2. VALIDAR REFERENCIAS DE RELACIONES
# =========================================

definiciones_relaciones = {
    "amistades.csv": (
        "id_usuario1", "usuarios.csv",
        "id_usuario2", "usuarios.csv"
    ),
    "pertenencias.csv": (
        "id_restaurante", "restaurantes.csv",
        "id_cocina", "tipos_cocina.csv"
    ),
    "ofertas.csv": (
        "id_restaurante", "restaurantes.csv",
        "id_platillo", "platillos.csv"
    ),
    "preparaciones.csv": (
        "id_chef", "chefs.csv",
        "id_platillo", "platillos.csv"
    ),
    "trabajos.csv": (
        "id_chef", "chefs.csv",
        "id_restaurante", "restaurantes.csv"
    ),
    "gustos.csv": (
        "id_usuario", "usuarios.csv",
        "id_cocina", "tipos_cocina.csv"
    ),
    "calificaciones.csv": (
        "id_usuario", "usuarios.csv",
        "id_restaurante", "restaurantes.csv"
    ),
    "visitas.csv": (
        "id_usuario", "usuarios.csv",
        "id_restaurante", "restaurantes.csv"
    ),
}

datos_relaciones = {}

print("\n===== VALIDACION DE RELACIONES =====")

for archivo, definicion in definiciones_relaciones.items():
    origen, archivo_origen, destino, archivo_destino = definicion
    filas = leer(RELACIONES, archivo)

    for fila in filas:
        assert int(fila[origen]) in ids_nodos[archivo_origen], (
            f"Origen inexistente en {archivo}"
        )

        assert int(fila[destino]) in ids_nodos[archivo_destino], (
            f"Destino inexistente en {archivo}"
        )

    datos_relaciones[archivo] = filas
    print(f"OK - {archivo}: {len(filas)} referencias validas")


# =========================================
# 3. VALIDAR REGLAS DE NEGOCIO
# =========================================

print("\n===== REGLAS DE NEGOCIO =====")

for archivo, filas in datos_relaciones.items():
    if archivo == "visitas.csv":
        continue

    origen, _, destino, _ = definiciones_relaciones[archivo]

    pares = [
        (fila[origen], fila[destino])
        for fila in filas
    ]

    assert len(pares) == len(set(pares)), (
        f"Relaciones duplicadas en {archivo}"
    )

print("OK - Sin relaciones duplicadas indebidas")

calificaciones = datos_relaciones["calificaciones.csv"]

assert all(
    1 <= int(c["puntuacion"]) <= 5
    for c in calificaciones
)
print("OK - Calificaciones entre 1 y 5")

gustos = datos_relaciones["gustos.csv"]

assert all(
    1 <= int(g["nivel_interes"]) <= 5
    for g in gustos
)
print("OK - Niveles de interes entre 1 y 5")

visitas = datos_relaciones["visitas.csv"]

ids_visitas = [int(v["id_visita"]) for v in visitas]

assert len(ids_visitas) == len(set(ids_visitas))
assert all(
    v["con_reserva"] in ("true", "false")
    for v in visitas
)

print("OK - Visitas con identificadores unicos")
print("OK - Valores booleanos de reserva correctos")


# =========================================
# 4. CASOS CONTROLADOS
# =========================================

print("\n===== CASOS DE PRUEBA =====")

assert any(
    a["id_usuario1"] == "1"
    and a["id_usuario2"] == "2"
    for a in datos_relaciones["amistades.csv"]
)

assert all(
    int(c["puntuacion"]) <= 2
    for c in calificaciones
    if c["id_restaurante"] == "50"
)

assert all(
    v["con_reserva"] == "true"
    for v in visitas
    if v["id_restaurante"] == "50"
)

assert any(
    g["id_usuario"] == "10"
    and g["id_cocina"] == "1"
    and g["nivel_interes"] == "5"
    for g in gustos
)

print("OK - Amistad Juan y Maria")
print("OK - Restaurante 50: baja calificacion y reservas")
print("OK - Usuario 10: preferencia italiana declarada")


# =========================================
# 5. RESUMEN
# =========================================

total_nodos = sum(
    len(ids) for ids in ids_nodos.values()
)

total_relaciones = sum(
    len(filas) for filas in datos_relaciones.values()
)

assert total_nodos == 865
assert total_relaciones == 14303

print("\n===== RESULTADO FINAL =====")
print(f"Nodos: {total_nodos}")
print(f"Relaciones: {total_relaciones}")
print("VALIDACION COMPLETADA CORRECTAMENTE")
