# Electra Platform — AGENTS.md

> Reglas de trabajo para agentes de IA en el proyecto Electra.
> Arquitectura: DDD + Hexagonal. Versión: 1.0.

---

## 1. Arquitectura del proyecto

```
electra/                              ← Raíz del proyecto (package: electra)
├── src/electra/                      ← Código fuente
│   ├── aplicacion/                   ← Casos de uso, CLI, DTOs, orquestador
│   ├── dominio/                      ← Modelos, servicios, puertos, eventos
│   └── infraestructura/              ← Adaptadores CAD, BIM, PDF, scraping
├── proyectos/                        ← Datos de clientes (aquiles, renzo)
├── referencias/                      ← Normativa PDF
├── tests/                            ← Tests (unit, integration, fixtures)
├── pyproject.toml                    ← Dependencias y configuración
├── README.md
└── AGENTS.md                         ← Este archivo
```

## 2. Contrato de capas

### Dominio (`src/electra/dominio/`)
- **Modelos**: Pydantic puro. Sin dependencias externas (ni ezdxf, ni requests).
- **Servicios**: Lógica de negocio pura. Inyectar dependencias por constructor.
- **Puertos**: Interfaces abstractas (ABC) que implementa infraestructura.
- **Eventos**: Notificaciones de cambios en el dominio.
- **NO** debe depender de `aplicacion/` ni de `infraestructura/`.

### Aplicación (`src/electra/aplicacion/`)
- **Casos de uso**: Un archivo por operación. Recibe DTO, llama al dominio, retorna resultado.
- **Orquestador**: Coordina múltiples casos de uso (pipeline completo).
- **CLI**: Interfaz de línea de comandos (Click). Wrapper thin sobre casos de uso.
- **DTOs**: Objetos planos para entrada/salida de casos de uso.
- **NO** debe contener lógica de dominio ni de infraestructura.

### Infraestructura (`src/electra/infraestructura/`)
- **Adaptadores**: Implementan los puertos definidos en dominio.
- **Persistencia**: Lectura/escritura de YAML, JSON, archivos.
- **CAD**: Generación de DXF/PDF via ezdxf, matplotlib.
- **BIM**: Exportación IFC via ifcopenshell.
- **Presupuestos**: Web scraping a proveedores.
- **Documentación**: Generación PDF via weasyprint, LaTeX.
- **NO** debe contener lógica de dominio.

## 3. Estándares de código

### 3.1 Convenciones
- **Lenguaje**: Python 3.11+
- **Tipado**: Anotaciones de tipo obligatorias en todas las funciones.
- **Validación**: Pydantic v2 para modelos de datos.
- **Tests**: pytest. Unitarios por módulo, integración por flujo.
- **Formato**: ruff (line-length=100).
- **Logging**: `import logging; logger = logging.getLogger(__name__)`.
- **Errores**: Excepciones de dominio personalizadas en `dominio/*/excepciones.py`.

### 3.2 Estructura de archivos
```python
# Archivo de dominio
"""Módulo de arquitectura — modelos del dominio."""

from __future__ import annotations

from pydantic import BaseModel, Field
from electra.dominio.shared.value_objects import Coordenadas, Dimension


class Ambiente(BaseModel):
    """Un ambiente dentro de un piso."""
    nombre: str
    coordenadas: Coordenadas
    dimension: Dimension
    tipo: TipoAmbiente = TipoAmbiente.OTRO
```

### 3.3 Inyección de dependencias
```python
# Puerto (dominio)
class RepositorioProyecto(ABC):
    @abstractmethod
    def cargar(self, id: str) -> Proyecto: ...

# Implementación (infraestructura)
class RepositorioProyectoYAML(RepositorioProyecto):
    def cargar(self, id: str) -> Proyecto:
        ...

# Uso (aplicación)
class CasoUsoEjecutarCalculos:
    def __init__(self, repo: RepositorioProyecto, calculos: ServicioCalculos):
        self._repo = repo
        self._calculos = calculos
```

## 4. Contrato de directorios

| Directorio | Propósito | Reglas |
|------------|-----------|--------|
| `proyectos/<id>/fuentes/` | Evidencia original | NO modificar ni sobrescribir |
| `proyectos/<id>/arquitectura/datos/` | Geometría aprobada | Solo lectura por el pipeline |
| `proyectos/<id>/diseno-electrico/datos/` | Circuitos y cargas | Solo lectura por el pipeline |
| `proyectos/<id>/expediente/` | Fuentes del documento técnico | Editar solo para correcciones |
| `proyectos/<id>/entregables/` | Archivos aprobados | Solo copia manual tras revisión |
| `proyectos/<id>/archivo/` | Histórico | NO usar como entrada activa |
| `build/` | Resultados regenerables | Ignorado por Git, borrable |
| `referencias/local/` | Material pesado | Puede no existir en otro clon |

## 5. Secuencia de operación

```text
FASE 1: INGESTA
  Croquis (imagen) ──→ fuentes/ (guardar original, NO modificar)
       ↓
FASE 2: EXTRACCIÓN (Agente IA)
  Analizar imagen ──→ arquitectura/datos/<piso>.json
   - Muros, puertas, ventanas, escaleras
   - Ambientes con nombre y dimensiones
   - Cotas verificables
   - Marcar incertidumbres con estado: "observado"|"inferido"|"por confirmar"
       ↓
FASE 3: VALIDACIÓN ARQUITECTÓNICA
  Verificar cierre geométrico, escala, coherencia entre pisos
  SI falla → detener, dejar observación
       ↓
FASE 4: DISEÑO ELÉCTRICO
  Definir por cada ambiente:
   - Luminarias (cantidad, tipo, circuito)
   - Tomacorrientes (cantidad, tipo, circuito)
   - Interruptores (cantidad, tipo, circuito)
   - Equipos especiales (cocina, bomba, etc.)
  Guardar en: diseno-electrico/datos/<piso>.json
       ↓
FASE 5: CÁLCULOS (Pipeline)
  python -m electra.aplicacion.cli calculos --proyecto <id>
   - Demanda por circuito
   - Selección de conductores
   - Protecciones
   - Caída de tensión
   - BOM preliminar
       ↓
FASE 6: CAD (Pipeline)
  python -m electra.aplicacion.cli cad --proyecto <id>
   - Plano arquitectónico DXF
   - Superposición eléctrica
   - Diagrama unifilar
   - PDF
       ↓
FASE 7: COTIZACIÓN (Pipeline)
  python -m electra.aplicacion.cli cotizar --proyecto <id>
   - BOM final
   - Consulta a proveedores
   - Comparativa de precios
       ↓
FASE 8: EXPEDIENTE (Pipeline)
  python -m electra.aplicacion.cli expediente --proyecto <id>
   - Memoria descriptiva
   - Cálculos justificativos
   - Especificaciones técnicas
   - Metrados y presupuesto
   - Planos
       ↓
FASE 9: REVISIÓN HUMANA
  Comparar planos con croquis
  Revisar cálculos
  Documentar observaciones
  SI aprueba → copiar a entregables/
```

## 6. Reglas técnicas

1. **Trazabilidad**: Todo valor extraído por IA debe incluir `{"valor": X, "unidad": "m", "origen": "...", "confianza": 0.95, "estado": "observado"|"inferido"|"por confirmar"}`.
2. **No inventar**: No agregar cotas, cargas, ubicaciones de tablero, SPAT ni datos del propietario sin evidencia. Usar `null` o `por confirmar`.
3. **Separación**: Dato observado ≠ dato calculado ≠ supuesto ≠ decisión humana. Cada uno en su campo correspondiente.
4. **Fuentes intocables**: Los archivos en `fuentes/` NUNCA se modifican. Si necesitas corregir, crea un nuevo archivo.
5. **Publicación controlada**: Los resultados van primero a `build/`. Solo después de revisión humana se copian a `entregables/`.
6. **Archivo congelado**: Los archivos en `archivo/` no deben usarse como entrada para resultados vigentes.
7. **Herramientas genéricas**: `src/electra/` no debe contener nombres, rutas ni datos de un proyecto específico. Eso pertenece a `proyectos/<id>/`.
8. **Pruebas**: Toda migración de código legacy debe mantener los tests existentes y agregar nuevos.
9. **Etapas bloqueantes**: Si una etapa falla o tiene incertidumbre crítica, detener las etapas dependientes y dejar observación explícita.
10. **Ramas Git**: No trabajar directamente en `main`. Usar `feature/<nombre>` y mergear vía PR.

## 7. Comandos frecuentes

```bash
# Instalar
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,bim]"

# Tests
python3 -m pytest tests/
python3 -m pytest tests/unit/
python3 -m pytest tests/integration/ -v

# Lint
ruff check src/
mypy src/

# Pipeline completo (nuevo)
python3 -m electra.aplicacion.cli pipeline --proyecto aquiles

# Pipeline completo (legacy - soportado hasta v2.0)
python3 herramientas/pipeline_automatizado.py --proyecto aquiles
```

## 8. Skills disponibles en el ecosistema

| Skill | Cuándo usarlo |
|-------|---------------|
| `ingenieria-electromecanica` | Cálculos eléctricos, normativa CNE, diseño de instalaciones |
| `spice` | Simulación de circuitos analógicos (filtros, divisores) |
| `kicad` | Diseño de PCBs y esquemáticos electrónicos |
| `bom` | Gestión de BOM, sourcing de componentes electrónicos |
| `emc` | Análisis de compatibilidad electromagnética |

## 9. Skills que podrían crearse para Electra

| Skill Propuesto | Propósito |
|-----------------|-----------|
| `electra-arquitectura` | Extracción de croquis a JSON arquitectónico |
| `electra-calculos-cne` | Validación de cálculos contra CNE Perú |
| `electra-diseno-electrico` | Diseño de circuitos y distribución eléctrica |
| `electra-expediente` | Generación de expediente técnico LaTeX |

