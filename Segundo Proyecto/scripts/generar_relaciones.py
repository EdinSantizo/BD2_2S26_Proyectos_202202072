
"""
Proyecto 2 - Sistemas de Bases de Datos 2
Generacion reproducible de relaciones para Neo4j.
Carnet: 202202072
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 202202073
rng = random.Random(SEMILLA)

BASE = Path(__file__).resolve().parent.parent
NODOS = BASE / "data" / "nodos"
SALIDA = BASE / "data" / "relaciones"
SALIDA.mkdir(parents=True, exist_ok=True)


def leer(nombre):
    with (NODOS / nombre).open(
        newline="", encoding="utf-8-sig"
    ) as archivo:
        return list(csv.DictReader(archivo))


def guardar(nombre, columnas, filas):
    ruta = SALIDA / nombre

    with ruta.open(
        "w", newline="", encoding="utf-8"
    ) as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=columnas
        )
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"{nombre}: {len(filas)} relaciones")


usuarios = leer("usuarios.csv")
restaurantes = leer("restaurantes.csv")
chefs = leer("chefs.csv")
platillos = leer("platillos.csv")
cocinas = leer("tipos_cocina.csv")

assert (
    len(usuarios),
    len(restaurantes),
    len(chefs),
    len(platillos),
    len(cocinas),
) == (500, 200, 100, 50, 15)

precios = {
    int(p["id"]): float(p["precio"])
    for p in platillos
}

rangos = {
    int(r["id"]): r["rango_precios"]
    for r in restaurantes
}

fecha_inicio = date(2025, 1, 1)
fecha_fin = date(2026, 9, 30)


def fecha_aleatoria():
    dias = (fecha_fin - fecha_inicio).days
    return (
        fecha_inicio
        + timedelta(days=rng.randint(0, dias))
    ).isoformat()


def registrar(filas, vistos, clave, registro):
    if clave not in vistos:
        vistos.add(clave)
        filas.append(registro)


# =========================================
# 1. ES_AMIGO_DE
# =========================================

amistades, vistos = [], set()


def amistad(a, b, fecha=None):
    par = tuple(sorted((a, b)))
    registrar(
        amistades,
        vistos,
        par,
        {
            "id_usuario1": a,
            "id_usuario2": b,
            "fecha_amistad": fecha or fecha_aleatoria(),
        },
    )


amistad(1, 2, "2024-01-15")

for i in range(2, 500):
    amistad(i, i + 1)

for i in range(5, 496, 3):
    amistad(i, i + 5)

guardar(
    "amistades.csv",
    ["id_usuario1", "id_usuario2", "fecha_amistad"],
    amistades,
)


# =========================================
# 2. PERTENECE_A
# =========================================

pertenencias, vistos = [], set()


def pertenece(r, t):
    registrar(
        pertenencias,
        vistos,
        (r, t),
        {"id_restaurante": r, "id_cocina": t},
    )


for r in range(1, 201):
    principal = (r - 1) % 15 + 1
    pertenece(r, principal)

    if r > 1 and rng.random() < 0.14:
        opciones = [
            i for i in range(1, 16)
            if i != principal
        ]
        pertenece(r, rng.choice(opciones))

guardar(
    "pertenencias.csv",
    ["id_restaurante", "id_cocina"],
    pertenencias,
)


# =========================================
# 3. OFRECE
# =========================================

ofertas, vistos = [], set()


def ofrece(r, p, precio=None, disponible=True):
    if precio is None:
        precio = max(
            5.0,
            precios[p] + rng.uniform(-5, 20),
        )

    registrar(
        ofertas,
        vistos,
        (r, p),
        {
            "id_restaurante": r,
            "id_platillo": p,
            "precio": f"{precio:.2f}",
            "disponible": str(disponible).lower(),
        },
    )


ofrece(1, 1, 65.0)

for p in range(1, 51):
    cocina = (p - 1) % 15 + 1

    for r in (cocina, cocina + 15, cocina + 30):
        ofrece(r, p)

for r in range(1, 201):
    principal = (r - 1) % 15 + 1

    platos_cocina = [
        p for p in range(1, 51)
        if (p - 1) % 15 + 1 == principal
    ]

    for p in platos_cocina:
        ofrece(
            r, p,
            disponible=rng.random() > 0.04,
        )

for p in range(1, 11):
    ofrece(16, p)

guardar(
    "ofertas.csv",
    [
        "id_restaurante", "id_platillo",
        "precio", "disponible",
    ],
    ofertas,
)


# =========================================
# 4. PREPARA
# =========================================

preparaciones, vistos = [], set()


def prepara(c, p, estilo=None, especialidad=None):
    registrar(
        preparaciones,
        vistos,
        (c, p),
        {
            "id_chef": c,
            "id_platillo": p,
            "estilo": estilo or rng.choice(
                ["tradicional", "moderno", "fusion"]
            ),
            "especialidad": (
                especialidad or "cocina internacional"
            ),
        },
    )


prepara(1, 1, "tradicional", "cocina italiana")

for c in range(1, 101):
    for p in rng.sample(range(1, 51), k=3):
        prepara(c, p)

guardar(
    "preparaciones.csv",
    [
        "id_chef", "id_platillo",
        "estilo", "especialidad",
    ],
    preparaciones,
)


# =========================================
# 5. TRABAJA_EN
# =========================================

trabajos, vistos = [], set()


def trabaja(c, r, fecha=None, puesto=None):
    registrar(
        trabajos,
        vistos,
        (c, r),
        {
            "id_chef": c,
            "id_restaurante": r,
            "fecha_inicio": fecha or fecha_aleatoria(),
            "puesto": puesto or "Chef",
        },
    )


trabaja(1, 1, "2020-02-01", "Chef principal")
trabaja(1, 16)
trabaja(1, 31)

for c in range(1, 101):
    for r in rng.sample(range(1, 201), k=2):
        trabaja(c, r)

for c in range(2, 13):
    trabaja(c, 16)

guardar(
    "trabajos.csv",
    [
        "id_chef", "id_restaurante",
        "fecha_inicio", "puesto",
    ],
    trabajos,
)


# =========================================
# 6. LE_GUSTA
# =========================================

gustos, vistos = [], set()


def gusta(u, t, nivel):
    registrar(
        gustos,
        vistos,
        (u, t),
        {
            "id_usuario": u,
            "id_cocina": t,
            "nivel_interes": nivel,
        },
    )


gusta(1, 1, 5)
gusta(10, 1, 5)

for u in range(2, 501):
    if u == 10:
        continue

    cantidad = rng.randint(1, 3)

    for t in rng.sample(range(1, 16), k=cantidad):
        gusta(u, t, rng.randint(1, 5))

guardar(
    "gustos.csv",
    ["id_usuario", "id_cocina", "nivel_interes"],
    gustos,
)


# =========================================
# 7. CALIFICO
# =========================================

calificaciones, vistos = [], set()


def califica(u, r, nota, fecha=None, comentario=None):
    registrar(
        calificaciones,
        vistos,
        (u, r),
        {
            "id_usuario": u,
            "id_restaurante": r,
            "puntuacion": nota,
            "fecha": fecha or fecha_aleatoria(),
            "comentario": (
                comentario or "Calificacion de prueba"
            ),
        },
    )


califica(
    1, 1, 5,
    "2026-09-10",
    "excelente comida",
)

# Amigos que recomiendan restaurantes.
for u in (2, 3, 4):
    califica(u, 16, 5)
    califica(u, 31, 4)

for r in range(1, 201):
    for u in rng.sample(range(2, 501), k=28):
        if r == 1:
            nota = 5
        elif r == 50:
            nota = rng.randint(1, 2)
        else:
            nota = rng.choices(
                [1, 2, 3, 4, 5],
                weights=[1, 2, 4, 8, 7],
            )[0]

        califica(u, r, nota)

guardar(
    "calificaciones.csv",
    [
        "id_usuario", "id_restaurante",
        "puntuacion", "fecha", "comentario",
    ],
    calificaciones,
)


# =========================================
# 8. VISITO
# =========================================

visitas = []

# Referencias de consumo para generar datos
# sinteticos; no son rangos oficiales del PDF.
valores_esperados = {
    "bajo": 60,
    "medio": 120,
    "alto": 240,
}


def visitar(u, r, consumo, reserva, fecha=None):
    visitas.append({
        "id_visita": len(visitas) + 1,
        "id_usuario": u,
        "id_restaurante": r,
        "fecha_visita": fecha or fecha_aleatoria(),
        "consumo": f"{consumo:.2f}",
        "con_reserva": str(reserva).lower(),
    })


visitar(1, 1, 85, True, "2026-09-09")

for r in range(1, 201):
    base = valores_esperados[rangos[r]]

    for u in rng.sample(range(2, 501), k=28):
        if r == 75:
            consumo = round(
                base * rng.uniform(2.3, 2.7), 2
            )
        else:
            consumo = round(
                base * rng.uniform(0.7, 1.3), 2
            )

        reserva = (
            True if r == 50
            else rng.random() < 0.42
        )

        visitar(u, r, consumo, reserva)

# El usuario 10 declara preferencia italiana,
# pero registra visitas frecuentes a cocina mexicana.
for k in range(15):
    r = [2, 17, 32, 47, 62][k % 5]
    visitar(10, r, 100 + k, True)

guardar(
    "visitas.csv",
    [
        "id_visita", "id_usuario",
        "id_restaurante", "fecha_visita",
        "consumo", "con_reserva",
    ],
    visitas,
)


# =========================================
# VALIDACIONES FINALES
# =========================================

assert len({
    int(v["id_visita"]) for v in visitas
}) == len(visitas)

assert len({
    (o["id_restaurante"], o["id_platillo"])
    for o in ofertas
}) == len(ofertas)

assert all(
    1 <= int(c["puntuacion"]) <= 5
    for c in calificaciones
)

print()
print("Generacion de relaciones completada.")
print(f"Semilla utilizada: {SEMILLA}")
