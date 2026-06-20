import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

folders = [
    "01_memoria_descriptiva",
    "01_memoria_descriptiva/catastro_y_ubicacion",
    "02_memoria_calculo",
    "02_memoria_calculo/hojas_excel",
    "03_especificaciones",
    "04_metrados_y_presupuesto",
    "05_planos_y_diagramas",
    "06_informes_y_revisiones",
    "capitulos",
    "figuras",
    "layouts",
    "planos",
    "metrados",
    "presupuesto",
    "electricos"
]

for folder in folders:
    path = os.path.join(base_dir, folder)
    os.makedirs(path, exist_ok=True)
    print(f"Creado: {path}")

print("Carpetas creadas con éxito.")
