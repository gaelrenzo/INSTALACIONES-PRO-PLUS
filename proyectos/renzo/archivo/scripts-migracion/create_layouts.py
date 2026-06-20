import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
base_dir = os.path.join(project_dir, "layouts")
os.makedirs(base_dir, exist_ok=True)

# Helper to save JSON
def save_layout(filename, data):
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"JSON guardado: {filepath}")

# ====================================================
# PRIMER PISO LAYOUTS
# ====================================================
primer_piso_rooms = [
    {"id": "R1", "name": "Tienda", "x": 0.0, "y": 0.0, "width": 3.0, "height": 3.5},
    {"id": "R2", "name": "Cocina", "x": 0.0, "y": 3.5, "width": 3.0, "height": 3.5},
    {"id": "R3", "name": "Pasadizo", "x": 3.0, "y": 0.0, "width": 1.5, "height": 7.0},
    {"id": "R4", "name": "Escalera", "x": 0.0, "y": 7.0, "width": 2.5, "height": 1.5}
]

# v1: Basic rooms
p1_v1 = {
    "project": "Vivienda Unifamiliar - Primer Piso v1",
    "author": "Mamani Galindo Renzo Gabriel",
    "date": "2026-06-03",
    "units": "meters",
    "dimensions": {"width": 4.5, "height": 8.5, "margin": 1.5},
    "rooms": primer_piso_rooms
}

# v2: Add doors
p1_v2 = p1_v1.copy()
p1_v2["project"] = "Vivienda Unifamiliar - Primer Piso v2"
p1_v2["doors"] = [
    {"id": "D1", "room_from": "R3", "room_to": "R1", "x": 3.0, "y": 2.5, "width": 0.8, "orientation": "vertical", "swing": "bottom-left"},
    {"id": "D2", "room_from": "R3", "room_to": "R2", "x": 3.0, "y": 6.0, "width": 0.8, "orientation": "vertical", "swing": "bottom-left"},
    {"id": "D3", "room_from": "Exterior", "room_to": "R1", "x": 0.3, "y": 0.0, "width": 0.9, "orientation": "horizontal", "swing": "top-right"},
    {"id": "D4", "room_from": "Exterior", "room_to": "R3", "x": 3.3, "y": 0.0, "width": 0.9, "orientation": "horizontal", "swing": "top-right"}
]

# v3: Add windows, stairs definition, ignored walls for clean merge
p1_v3 = p1_v2.copy()
p1_v3["project"] = "Vivienda Unifamiliar - Primer Piso v3"
p1_v3["windows"] = [
    {"id": "W1", "x": 1.5, "y": 0.0, "width": 1.2, "orientation": "horizontal"},
    {"id": "W2", "x": 0.0, "y": 1.75, "width": 1.0, "orientation": "vertical"},
    {"id": "W3", "x": 0.0, "y": 5.25, "width": 1.0, "orientation": "vertical"}
]
p1_v3["stairs"] = [
    {"x1": 0.15, "y1": 7.0, "x2": 2.5, "y2": 8.5, "steps": 8}
]
# Remove division between R4 (Escalera area) and R3 (Pasadizo end)
p1_v3["ignored_walls"] = [
    [[2.5, 7.0], [2.5, 8.5]],
    [[3.0, 7.0], [4.5, 7.0]]
]

save_layout("primer_piso_v1.json", p1_v1)
save_layout("primer_piso_v2.json", p1_v2)
save_layout("primer_piso_v3.json", p1_v3)

# ====================================================
# SEGUNDO PISO LAYOUTS
# ====================================================
segundo_piso_rooms = [
    {"id": "R1", "name": "Dormitorio Principal", "x": 0.0, "y": 0.0, "width": 4.5, "height": 4.0},
    {"id": "R2", "name": "Dormitorio 3", "x": 0.0, "y": 4.0, "width": 3.0, "height": 3.5},
    {"id": "R3", "name": "Sala / Hall", "x": 3.0, "y": 4.0, "width": 1.5, "height": 3.5},
    {"id": "R4", "name": "Baño", "x": 3.0, "y": 7.5, "width": 1.5, "height": 1.5},
    {"id": "R5", "name": "Escalera", "x": 0.0, "y": 7.5, "width": 2.5, "height": 1.5}
]

# v1: Basic rooms
p2_v1 = {
    "project": "Vivienda Unifamiliar - Segundo Piso v1",
    "author": "Mamani Galindo Renzo Gabriel",
    "date": "2026-06-03",
    "units": "meters",
    "dimensions": {"width": 4.5, "height": 9.0, "margin": 1.5},
    "rooms": segundo_piso_rooms
}

# v2: Add doors
p2_v2 = p2_v1.copy()
p2_v2["project"] = "Vivienda Unifamiliar - Segundo Piso v2"
p2_v2["doors"] = [
    {"id": "D1", "room_from": "R3", "room_to": "R1", "x": 1.5, "y": 4.0, "width": 0.8, "orientation": "horizontal", "swing": "bottom-left"},
    {"id": "D2", "room_from": "R3", "room_to": "R2", "x": 1.0, "y": 4.0, "width": 0.8, "orientation": "horizontal", "swing": "top-right"},
    {"id": "D3", "room_from": "R3", "room_to": "R4", "x": 3.5, "y": 7.5, "width": 0.7, "orientation": "horizontal", "swing": "top-left"}
]

# v3: Add windows, stairs, ignored walls
p2_v3 = p2_v2.copy()
p2_v3["project"] = "Vivienda Unifamiliar - Segundo Piso v3"
p2_v3["windows"] = [
    {"id": "W1", "x": 2.25, "y": 0.0, "width": 1.5, "orientation": "horizontal"},
    {"id": "W2", "x": 0.0, "y": 5.75, "width": 1.2, "orientation": "vertical"},
    {"id": "W3", "x": 4.5, "y": 5.75, "width": 1.0, "orientation": "vertical"}
]
p2_v3["stairs"] = [
    {"x1": 0.15, "y1": 7.5, "x2": 2.5, "y2": 9.0, "steps": 8}
]
p2_v3["ignored_walls"] = [
    [[2.5, 7.5], [2.5, 9.0]],
    [[3.0, 7.5], [3.0, 9.0]]  # merge hall space
]

save_layout("segundo_piso_v1.json", p2_v1)
save_layout("segundo_piso_v2.json", p2_v2)
save_layout("segundo_piso_v3.json", p2_v3)

# ====================================================
# TERCER PISO LAYOUTS
# ====================================================
tercer_piso_rooms = [
    {"id": "R1", "name": "Dormitorio 4", "x": 0.0, "y": 0.0, "width": 2.25, "height": 7.5},
    {"id": "R2", "name": "Dormitorio 5", "x": 2.25, "y": 0.0, "width": 2.25, "height": 7.5},
    {"id": "R3", "name": "Pasadizo", "x": 0.0, "y": 7.5, "width": 2.25, "height": 1.5},
    {"id": "R4", "name": "Baño", "x": 2.25, "y": 7.5, "width": 2.25, "height": 1.5},
    {"id": "R5", "name": "Escalera", "x": 0.0, "y": 7.5, "width": 2.1, "height": 1.5}
]

# v1: Basic rooms
p3_v1 = {
    "project": "Vivienda Unifamiliar - Tercer Piso v1",
    "author": "Mamani Galindo Renzo Gabriel",
    "date": "2026-06-03",
    "units": "meters",
    "dimensions": {"width": 4.5, "height": 9.0, "margin": 1.5},
    "rooms": tercer_piso_rooms
}

# v2: Add doors
p3_v2 = p3_v1.copy()
p3_v2["project"] = "Vivienda Unifamiliar - Tercer Piso v2"
p3_v2["doors"] = [
    {"id": "D1", "room_from": "R3", "room_to": "R1", "x": 1.12, "y": 7.5, "width": 0.8, "orientation": "horizontal", "swing": "bottom-left"},
    {"id": "D2", "room_from": "R3", "room_to": "R2", "x": 2.25, "y": 7.5, "width": 0.8, "orientation": "horizontal", "swing": "bottom-right"},
    {"id": "D3", "room_from": "R3", "room_to": "R4", "x": 3.37, "y": 7.5, "width": 0.7, "orientation": "horizontal", "swing": "top-right"}
]

# v3: Add windows, stairs, ignored walls
p3_v3 = p3_v2.copy()
p3_v3["project"] = "Vivienda Unifamiliar - Tercer Piso v3"
p3_v3["windows"] = [
    {"id": "W1", "x": 1.12, "y": 0.0, "width": 1.0, "orientation": "horizontal"},
    {"id": "W2", "x": 3.37, "y": 0.0, "width": 1.0, "orientation": "horizontal"},
    {"id": "W3", "x": 4.5, "y": 8.25, "width": 0.8, "orientation": "vertical"}
]
p3_v3["stairs"] = [
    {"x1": 0.15, "y1": 7.5, "x2": 2.1, "y2": 9.0, "steps": 8}
]
p3_v3["ignored_walls"] = [
    [[2.1, 7.5], [2.1, 9.0]],
    [[2.25, 7.5], [2.25, 9.0]]  # clean lobby entrance
]

save_layout("tercer_piso_v1.json", p3_v1)
save_layout("tercer_piso_v2.json", p3_v2)
save_layout("tercer_piso_v3.json", p3_v3)

print("Todos los layouts JSON generados exitosamente.")
