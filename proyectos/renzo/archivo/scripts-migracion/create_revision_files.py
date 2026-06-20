import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
base_dir = os.path.join(project_dir, "06_informes_y_revisiones", "revisiones")
os.makedirs(base_dir, exist_ok=True)

def create_rev_file(filename, title, content):
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Revisión guardada: {filepath}")

# ====================================================
# PISO 1 REVISIONS
# ====================================================
p1_v1_text = """# Revisión Plano Primer Piso - Versión 1 (Básica)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Primer Piso
**Versión:** v1 (Básica)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Muros:** Se dibujan los contornos de las habitaciones Tienda, Cocina, Pasadizo y Escalera. Espesores de muro correctos de 0.15 m y 0.10 m.
- **Ambientes:** Ubicación ortogonal correcta de todos los espacios.
- **Aberturas:** Sin aberturas de puertas ni ventanas en esta versión.

### 2. Observaciones Visuales
- La planta refleja la geometría general de 4.50m x 8.50m.
- Se observan las divisiones internas limpias, pero las habitaciones son inaccesibles por la falta de vanos.

### 3. Conclusiones y Cambios para v2
- Incorporar vanos y abatimiento de puertas en Tienda (calle y pasadizo), Cocina (pasadizo) e Ingreso Principal.
"""

p1_v2_text = """# Revisión Plano Primer Piso - Versión 2 (Aberturas)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Primer Piso
**Versión:** v2 (Puertas)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Muros:** Líneas de muros dobles correctas.
- **Puertas:** Se agregaron 4 puertas: D1 (Tienda-Pasadizo), D2 (Cocina-Pasadizo), D3 (Portón calle Tienda) y D4 (Ingreso calle Pasadizo).
- **Ventanas:** Pendientes.

### 2. Observaciones Visuales
- El abatimiento de las puertas se genera correctamente con arcos de 90°.
- El muro del pasadizo tiene intersecciones con la caja de escalera que cierran el paso físico.

### 3. Conclusiones y Cambios para v3
- Usar la opción `ignored_walls` para abrir la caja de escalera hacia el pasadizo.
- Agregar las ventanas exteriores de la Tienda y Cocina.
- Ajustar cantidad de pasos de la escalera (8 pasos).
"""

p1_v3_text = """# Revisión Plano Primer Piso - Versión 3 (Consolidada)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Primer Piso
**Versión:** v3 (Consolidada/Arquitectura)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Muros y Aberturas:** Muros perfectamente integrados. La caja de la escalera se conecta directamente con el pasadizo sin muros residuales.
- **Puertas y Ventanas:** Todas las puertas tienen el giro y orientación correctos. Se agregaron las ventanas exteriores (Tienda y Cocina).
- **Escalera:** Configurada con 8 pasos de $0.27\text{ m}$ de huella y descanso.
- **Cotas:** Líneas de cota exteriores automáticas alineadas a los bordes.

### 2. Observaciones Visuales
- Presentación limpia y profesional. Las cotas son legibles y el membrete identifica al estudiante Renzo Mamani.
- El plano está listo para servir como plantilla base de los circuitos de alumbrado y tomacorrientes.
"""

# ====================================================
# PISO 2 REVISIONS
# ====================================================
p2_v1_text = """# Revisión Plano Segundo Piso - Versión 1 (Básica)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Segundo Piso
**Versión:** v1 (Básica)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Muros:** Distribución de Dormitorio Principal, Dormitorio 3, Sala, Baño y Escalera.
- **Aberturas:** Sin puertas ni ventanas.

### 2. Observaciones Visuales
- El Dormitorio Principal ocupa correctamente todo el ancho frontal ($4.50\text{ m}$).
- Muros y etiquetas alineados.

### 3. Conclusiones y Cambios para v2
- Agregar puertas de paso de dormitorios y baño.
"""

p2_v2_text = """# Revisión Plano Segundo Piso - Versión 2 (Aberturas)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Segundo Piso
**Versión:** v2 (Puertas)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Puertas:** Se agregaron D1 (Dormitorio Principal), D2 (Dormitorio 3) y D3 (Baño) desde la Sala/Hall.
- **Ventanas:** Pendientes.

### 2. Observaciones Visuales
- Las puertas abren hacia el interior de los dormitorios de forma correcta.
- Hay un muro superpuesto en la zona de recibo de la escalera hacia el hall.

### 3. Conclusiones y Cambios para v3
- Ignorar los muros colindantes de la escalera hacia el hall para permitir paso libre.
- Agregar ventanas en el Dormitorio Principal (frente) y en Dormitorio 3/Sala (lados).
"""

p2_v3_text = """# Revisión Plano Segundo Piso - Versión 3 (Consolidada)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Segundo Piso
**Versión:** v3 (Consolidada/Arquitectura)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Geometría General:** Correcta distribución de muros, vanos de puertas libres y ventanas integradas.
- **Escalera:** 8 pasos dibujados de forma precisa en el lado izquierdo.
- **Cotas y Rótulo:** Centrado en el dibujo con membrete y dimensiones generales.

### 2. Observaciones Visuales
- Plano limpio y consistente. La unión entre la escalera y la sala de distribución es fluida.
"""

# ====================================================
# PISO 3 REVISIONS
# ====================================================
p3_v1_text = """# Revisión Plano Tercer Piso - Versión 1 (Básica)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Tercer Piso
**Versión:** v1 (Básica)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Muros:** Distribución longitudinal de Dormitorio 4 y Dormitorio 5, Pasadizo, Baño y Escalera.

### 2. Observaciones Visuales
- Refleja los dos dormitorios simétricos alargados ($2.25\text{ m} \times 7.50\text{ m}$).

### 3. Conclusiones y Cambios para v2
- Agregar puertas de ingreso a los dormitorios y al baño.
"""

p3_v2_text = """# Revisión Plano Tercer Piso - Versión 2 (Aberturas)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Tercer Piso
**Versión:** v2 (Puertas)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Puertas:** D1 y D2 agregadas en la base de los dormitorios. D3 agregada en el baño.

### 2. Observaciones Visuales
- Las puertas de los dormitorios se abren hacia adentro, lo cual es funcional.
- Se debe liberar la unión del pasadizo para que la escalera no quede encerrada.

### 3. Conclusiones y Cambios para v3
- Definir muros ignorados entre la escalera y el vestíbulo.
- Incorporar ventanas frontales y de baño.
"""

p3_v3_text = """# Revisión Plano Tercer Piso - Versión 3 (Consolidada)
**Proyecto:** Vivienda Unifamiliar
**Nivel:** Tercer Piso
**Versión:** v3 (Consolidada/Arquitectura)
**Fecha de Evaluación:** 2026-06-03

### 1. Elementos Evaluados
- **Distribución:** Plano completamente depurado, con vanos e iluminación natural bien colocados en dormitorios y baño.
- **Acabado CAD:** Cotas claras y rótulo de identificación institucional.
"""

# Write all
create_rev_file("revision_piso1_v1.md", "Piso 1 v1", p1_v1_text)
create_rev_file("revision_piso1_v2.md", "Piso 1 v2", p1_v2_text)
create_rev_file("revision_piso1_v3.md", "Piso 1 v3", p1_v3_text)

create_rev_file("revision_piso2_v1.md", "Piso 2 v1", p2_v1_text)
create_rev_file("revision_piso2_v2.md", "Piso 2 v2", p2_v2_text)
create_rev_file("revision_piso2_v3.md", "Piso 2 v3", p2_v3_text)

create_rev_file("revision_piso3_v1.md", "Piso 3 v1", p3_v1_text)
create_rev_file("revision_piso3_v2.md", "Piso 3 v2", p3_v2_text)
create_rev_file("revision_piso3_v3.md", "Piso 3 v3", p3_v3_text)

print("Archivos de revisión visual iterativa generados con éxito.")
