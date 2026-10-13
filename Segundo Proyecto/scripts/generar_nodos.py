
"""
Proyecto 2 - Sistemas de Bases de Datos 2
Generacion reproducible de nodos para Neo4j.
Carnet: 202202072
"""

import csv
import random
from pathlib import Path

SEED = 202202072
rng = random.Random(SEED)

BASE = Path(__file__).resolve().parent.parent
SALIDA = BASE / "data" / "nodos"
SALIDA.mkdir(parents=True, exist_ok=True)


def guardar_csv(nombre, campos, registros):
    ruta = SALIDA / nombre

    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(registros)

    print(f"{nombre}: {len(registros)} registros")


# =========================================
# 1. TIPOS DE COCINA (15)
# =========================================

cocinas = [
    "Italiana",
    "Mexicana",
    "Guatemalteca",
    "Japonesa",
    "China",
    "Francesa",
    "India",
    "Española",
    "Peruana",
    "Coreana",
    "Tailandesa",
    "Mediterranea",
    "Argentina",
    "Vegetariana",
    "Arabe",
]

tipos_cocina = []

for i, nombre in enumerate(cocinas, start=1):
    descripcion = (
        "Cocina tradicional de Italia"
        if i == 1
        else f"Especialidades de cocina {nombre.lower()}"
    )

    tipos_cocina.append({
        "id": i,
        "nombre": nombre,
        "descripcion": descripcion,
    })

guardar_csv(
    "tipos_cocina.csv",
    ["id", "nombre", "descripcion"],
    tipos_cocina,
)


# =========================================
# 2. USUARIOS (500)
# =========================================

usuarios = [
    {
        "id": 1,
        "nombre": "Juan Perez",
        "email": "juan@gmail.com",
        "edad": 25,
        "pais": "Guatemala",
    },
    {
        "id": 2,
        "nombre": "Maria Lopez",
        "email": "maria@gmail.com",
        "edad": 27,
        "pais": "Guatemala",
    },
]

nombres = [
    "Ana", "Luis", "Sofia", "Pedro", "Lucia",
    "Diego", "Elena", "Andres", "Valeria", "Carlos",
]

apellidos = [
    "Garcia", "Lopez", "Morales", "Gomez", "Ramirez",
    "Mendez", "Castillo", "Pineda", "Torres", "Reyes",
]

paises = [
    "Guatemala", "Mexico", "El Salvador",
    "Honduras", "Costa Rica", "Colombia", "Peru",
]

for i in range(3, 501):
    usuarios.append({
        "id": i,
        "nombre": f"{rng.choice(nombres)} {rng.choice(apellidos)}",
        "email": f"usuario{i:04d}@example.com",
        "edad": rng.randint(18, 65),
        "pais": rng.choice(paises),
    })

guardar_csv(
    "usuarios.csv",
    ["id", "nombre", "email", "edad", "pais"],
    usuarios,
)


# =========================================
# 3. RESTAURANTES (200)
# =========================================

restaurantes = [
    {
        "id": 1,
        "nombre": "La Parrilla",
        "anio_apertura": 2015,
        "rango_precios": "medio",
        "descripcion": "Restaurante de carnes",
    }
]

rangos = ["bajo", "medio", "alto"]
prefijos = ["Casa", "Sabor", "Rincon", "Mesa", "Bistro"]

for i in range(2, 201):
    cocina = cocinas[(i - 1) % len(cocinas)]

    restaurantes.append({
        "id": i,
        "nombre": f"{prefijos[(i - 2) % len(prefijos)]} {cocina} {i:03d}",
        "anio_apertura": rng.randint(1990, 2025),
        "rango_precios": rangos[(i - 1) % len(rangos)],
        "descripcion": f"Restaurante de cocina {cocina.lower()}",
    })

guardar_csv(
    "restaurantes.csv",
    ["id", "nombre", "anio_apertura", "rango_precios", "descripcion"],
    restaurantes,
)


# =========================================
# 4. CHEFS (100)
# =========================================

chefs = [
    {
        "id": 1,
        "nombre": "Carlos Lopez",
        "fecha_nacimiento": "1985-04-12",
        "nacionalidad": "Guatemalteca",
    }
]

nacionalidades = [
    "Guatemalteca", "Mexicana", "Peruana",
    "Argentina", "Colombiana",
]

for i in range(2, 101):
    anio = rng.randint(1965, 2000)
    mes = rng.randint(1, 12)
    dia = rng.randint(1, 28)

    chefs.append({
        "id": i,
        "nombre": f"{rng.choice(nombres)} {rng.choice(apellidos)}",
        "fecha_nacimiento": f"{anio:04d}-{mes:02d}-{dia:02d}",
        "nacionalidad": rng.choice(nacionalidades),
    })

guardar_csv(
    "chefs.csv",
    ["id", "nombre", "fecha_nacimiento", "nacionalidad"],
    chefs,
)


# =========================================
# 5. PLATILLOS (50)
# =========================================

platillos = [
    {
        "id": 1,
        "nombre": "Pizza Margarita",
        "precio": "65.00",
        "descripcion": "Pizza con tomate y mozzarella",
    }
]

for i in range(2, 51):
    cocina = cocinas[(i - 1) % len(cocinas)]
    precio = 35 + (i % 10) * 15

    platillos.append({
        "id": i,
        "nombre": f"Especialidad {cocina} {i:03d}",
        "precio": f"{precio:.2f}",
        "descripcion": f"Platillo de cocina {cocina.lower()}",
    })

guardar_csv(
    "platillos.csv",
    ["id", "nombre", "precio", "descripcion"],
    platillos,
)


# =========================================
# RESUMEN
# =========================================

total = (
    len(usuarios)
    + len(restaurantes)
    + len(chefs)
    + len(platillos)
    + len(tipos_cocina)
)

assert len(usuarios) == 500
assert len(restaurantes) == 200
assert len(chefs) == 100
assert len(platillos) == 50
assert len(tipos_cocina) == 15

print()
print("Generacion completada.")
print(f"Total de nodos preparados: {total}")
print(f"Semilla utilizada: {SEED}")
