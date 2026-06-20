# Electra Platform — Architecture Document

> **Version:** 1.0
> **Date:** 2026-06-20
> **Author:** CTO & Principal Architect

---

## A. Clasificación de carpetas actuales

### Dominio (Domain)
| Carpeta | Descripción |
|---------|-------------|
| `src/electra_core/core/` | Lógica de dominio: normativas, topología, resolución de red |
| `src/electra_core/core/normativas/` | Estrategias de validación (CNE, IEC) |
| `src/electra_core/modelos/` | Modelos de dominio Pydantic (RedElectrica, Circuito, Tablero) |

### Aplicación (Application)
| Carpeta | Descripción |
|---------|-------------|
| `src/electra_core/interfaces/` | Puertos/contratos entre capas |
| `src/electra_core/orquestador/` | Orquestación del pipeline |
| `herramientas/pipeline_automatizado.py` | CLI orchestrator |
| `herramientas/calculadora/` | UI web interactiva |

### Infraestructura (Infrastructure)
| Carpeta | Descripción |
|---------|-------------|
| `src/electra_core/dominios/cad/` | Generación DXF (thin wrapper) |
| `src/electra_core/dominios/bim/` | Exportación IFC |
| `src/electra_core/dominios/calculos/` | Cálculos CNE (thin) |
| `src/electra_core/dominios/cotizaciones/` | BOM calculator |
| `src/electra_core/dominios/documentos/` | PDF generator |
| `herramientas/cad/scripts/` | Motor CAD completo (dxf_generator, electrical_overlay, auto_routing) |
| `herramientas/cad/cad-scripts/` | QCAD export |
| `herramientas/calculos/scripts/` | Motor de cálculos (calcular_instalacion, generar_bom) |
| `herramientas/cotizacion/` | Cotización multi-proveedor con scraping |
| `herramientas/cotizacion/proveedores/` | Conectores individuales |
| `herramientas/simbologia/` | Librería de símbolos DGE |
| `.github/workflows/` | CI/CD |

### Datos (Data)
| Carpeta | Descripción |
|---------|-------------|
| `herramientas/calculos/datos/` | Ampacidades YAML |
| `herramientas/cotizacion/data/` | Reglas de matching, equivalencias, proveedores |
| `herramientas/simbologia/simbologia_*.json` | Definiciones de símbolos |
| `plantillas/` | Templates HTML/YAML |
| `referencias/` | Normativa PDF, fichas |
| `herramientas/cad/examples/` | Layout JSON de ejemplo |

### Proyectos cliente (Client Projects)
| Carpeta | Descripción |
|---------|-------------|
| `proyectos/aquiles/` | Vivienda 2 pisos — proyecto completo |
| `proyectos/renzo/` | Vivienda 3 pisos — proyecto completo |

### Herramientas auxiliares
| Carpeta | Descripción |
|---------|-------------|
| `herramientas/` | Scripts legacy (a migrar al core) |

---

## B. Duplicidades detectadas

### B.1 CAD — DUPLICADO CRÍTICO
Dos implementaciones de generación DXF:

| Archivo | Líneas | Estado |
|---------|--------|--------|
| `herramientas/cad/scripts/dxf_generator.py` | ~659 | Completo: muros, puertas, ventanas, mobiliario, cotas, PDF |
| `src/electra_core/dominios/cad/generador_dxf.py` | ~34 | Esqueleto, solo exporta un diagrama simple |

**Veredicto:** `herramientas/cad/scripts/dxf_generator.py` es la implementación real. La de `src/electra_core/` es un stub.

### B.2 Cálculos — DUPLICADO
| Archivo | Líneas | Estado |
|---------|--------|--------|
| `herramientas/calculos/scripts/calcular_instalacion.py` | ~200 | Completo: demanda, conductores, protecciones, LaTeX |
| `src/electra_core/dominios/calculos/cne_norma.py` | ~28 | Stub |
| `src/electra_core/core/resolver.py` | ~53 | Resolución de flujo |

### B.3 BOM — TRIPLICADO
| Archivo | Líneas |
|---------|--------|
| `herramientas/calculos/scripts/generar_bom.py` | ~100 |
| `src/electra_core/dominios/cotizaciones/calculador_bom.py` | ~31 |
| `herramientas/pipeline_automatizado.py:generar_bom()` | ~130 |

### B.4 Pipeline — DUPLICADO
| Archivo | Líneas | Estado |
|---------|--------|--------|
| `herramientas/pipeline_automatizado.py` | ~878 | Completo: orquesta todo el flujo |
| `src/electra_core/orquestador/pipeline.py` | ~84 | Versión OOP simplificada |

### B.5 Modelos de datos — DUPLICADO PARCIAL
| Archivo | Contenido |
|---------|-----------|
| `src/electra_core/modelos/topologia.py` | Modelos core Pydantic |
| `herramientas/cotizacion/modelos.py` | Modelos de pricing propios |
| `proyectos/*/datos/` | JSON/YAML con esquemas propios |

---

## C. Carpetas a fusionar

| Acción | Origen | Destino |
|--------|--------|---------|
| 🔀 Fusionar | `herramientas/cad/scripts/` | `src/electra_core/dominios/cad/` |
| 🔀 Fusionar | `herramientas/cad/cad-scripts/` | `src/electra_core/dominios/cad/` |
| 🔀 Fusionar | `herramientas/calculos/scripts/` | `src/electra_core/dominios/calculos/` |
| 🔀 Fusionar | `herramientas/calculos/datos/` | `src/electra_core/dominios/calculos/` |
| 🔀 Fusionar | `herramientas/cotizacion/` | `src/electra_core/dominios/cotizaciones/` |
| 🔀 Fusionar | `herramientas/simbologia/` | `src/electra_core/dominios/cad/simbologia/` |
| 🔀 Fusionar | `src/electra_core/interfaces/puertos.py` | `src/electra_core/aplicacion/puertos/` |
| 🔀 Fusionar | `src/electra_core/orquestador/` | `src/electra_core/aplicacion/servicios/` |
| 🔀 Fusionar | `herramientas/pipeline_automatizado.py` | `src/electra_core/aplicacion/cli/` |
| 🗑️ Deprecar | `herramientas/calculadora/` | Migrar a `src/electra_core/aplicacion/web/` |
| 📦 Mover | `plantillas/` | `src/electra_core/infraestructura/plantillas/` |
| 📦 Mantener | `proyectos/` | Sin cambios (datos de clientes) |
| 📦 Mantener | `referencias/` | Sin cambios |

---

## D. Arquitectura DDD + Hexagonal

### Capas

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INTERFACES DE USUARIO                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │  CLI     │  │  Web UI  │  │  API     │  │  Agent Interface   │  │
│  │ (Click)  │  │ (Vue/SFC)│  │(FastAPI) │  │  (opencode)        │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬───────────┘  │
│       │              │             │                  │              │
├───────┴──────────────┴─────────────┴──────────────────┴─────────────┤
│                    CAPA DE APLICACIÓN                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Casos de Uso (Use Cases / Commands & Queries)               │   │
│  │  ┌────────────────────┐  ┌───────────────────────────────┐   │   │
│  │  │ ExtraerCroquis     │  │ GenerarProyectoCompleto      │   │   │
│  │  │ ValidarArquitectura│  │ CalcularYDimensional          │   │   │
│  │  │ DefinirComponentes │  │ ExportarPlanos                │   │   │
│  │  │ GenerarBOM         │  │ GenerarExpediente             │   │   │
│  │  └────────────────────┘  └───────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Servicios de Aplicación                                      │   │
│  │  Orquestador, Pipeline, DTOs, Mappers                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    CAPA DE DOMINIO                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Modelos (Agregados, Entidades, Value Objects)               │   │
│  │  Proyecto, Piso, Ambiente, Circuito, Carga, Conductor,       │   │
│  │  Tablero, Proteccion, Canalizacion, Simbolo                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Servicios de Dominio                                         │   │
│  │  ServicioCalculosCNE, ServicioValidacionNormativa,            │   │
│  │  ServicioTopologiaRed, ServicioMaximaDemanda                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Puertos (Interfaces / Ports)                                 │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │   │
│  │  │ CAD Port │ │ BIM Port │ │ PDF Port │ │ Pricing Port   │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    INFRAESTRUCTURA                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐   │
│  │ Adaptador│ │ Adaptador│ │ Adaptador│ │ Adaptadores        │   │
│  │ CAD      │ │ BIM      │ │ PDF      │ │ Web Scraping       │   │
│  │ (ezdxf)  │ │(ifcopen) │ │(weasypr.)│ │ (requests/bs4)     │   │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐   │
│  │ Repos.   │ │ Repos.   │ │ Export.  │ │ Plantillas         │   │
│  │ YAML     │ │ JSON     │ │ LaTeX    │ │ Jinja2             │   │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Principios DDD aplicados

| Principio | Implementación |
|-----------|---------------|
| **Aggregate Root** | `Proyecto` es raíz de agregado; contiene `Piso[]`, `Tablero[]`, `Circuito[]` |
| **Value Objects** | `Coordenadas`, `SeccionConductor`, `Potencia`, `PorcentajeCaida` |
| **Domain Events** | `ProyectoCreado`, `CalculosCompletados`, `PlanosGenerados` |
| **Repository** | `Interfaces/RepositorioProyecto` → `Infraestructura/RepositorioProyectoYAML` |
| **Factory** | `FabricaProyecto`, `FabricaCircuito` para crear agregados complejos |
| **Strategy** | `EstrategiaNormativa` base → `CNEPeru`, `NEC`, `IEC` |
| **Specification** | `EspecificacionCumplimientoCNE`, `EspecificacionSeccionMinima` |

---

## E. Diseño de módulos

### E.1 Módulo Arquitectura
```
src/electra_core/dominio/arquitectura/
├── modelos.py           Ambiente, Piso, Muro, Puerta, Ventana, Escalera, Coordenadas
├── servicios.py         ServicioValidacionArquitectonica, ServicioExtraccionCroquis
├── eventos.py           ArquitecturaValidada, AmbienteModificado
├── repositorio.py       Puerto: RepositorioArquitectura
├── fabrica.py           FabricaArquitectura (crea desde JSON/croquis)
└── specs.py             Especificaciones de validación (cierre geométrico, escala)
```

### E.2 Módulo Diseño Eléctrico
```
src/electra_core/dominio/diseno_electrico/
├── modelos.py           Circuito, Carga, Tablero, Proteccion, Canalizacion
├── servicios.py         ServicioDisenoElectrico (distribución de circuitos)
├── eventos.py           DisenoIniciado, CircuitoAgregado
├── repositorio.py       Puerto: RepositorioDisenoElectrico
└── fabrica.py           FabricaCircuito, FabricaTablero
```

### E.3 Módulo Cálculos
```
src/electra_core/dominio/calculos/
├── modelos.py           DemandaResultado, ConductorSeleccion, CaidaTension
├── servicios.py         ServicioCalculoDemanda, ServicioSeleccionConductor
├── estrategias/         CNE, NEC, IEC
│   ├── __init__.py
│   ├── base.py
│   ├── cne_peru.py
│   ├── nec_usa.py
│   └── iec.py
├── datos/               Ampacidades, Factores de corrección
│   ├── ampacidades.yaml
│   └── factores_correccion.yaml
└── eventos.py           CalculosCompletados, DemandaCalculada
```

### E.4 Módulo CAD
```
src/electra_core/infraestructura/cad/
├── adaptador.py         Implementación de PuertoCAD (ezdxf)
├── dxf_generator.py     Motor completo de generación DXF
├── electrical_overlay.py Superposición de simbología eléctrica
├── auto_routing.py      Enrutamiento A* de canalizaciones
├── unifilar.py          Diagrama unifilar
├── pdf.py               Exportación PDF (matplotlib / QCAD)
├── simbologia/          Biblioteca de símbolos DGE
│   ├── simbolos.json
│   └── generador_catalogo.py
└── ejemplos/            Layouts de ejemplo
```

### E.5 Módulo BIM
```
src/electra_core/infraestructura/bim/
├── adaptador.py         Implementación de PuertoBIM (ifcopenshell)
└── exportador_ifc.py    Exportación IFC
```

### E.6 Módulo Presupuestos
```
src/electra_core/dominio/presupuestos/
├── modelos.py           Material, BOMItem, Cotizacion, Proveedor, Precio
├── servicios.py         ServicioCalculoBOM, ServicioComparativaPrecios
├── repositorio.py       Puerto: RepositorioPrecios
├── normalizador.py      Normalización de materiales por proveedor
└── eventos.py           BOMModificado, CotizacionCompletada

src/electra_core/infraestructura/presupuestos/
├── adaptadores/         Conectores a proveedores
│   ├── promart.py
│   ├── sodimac.py
│   ├── maestro.py
│   └── mercadolibre.py
└── datos/               Reglas de matching, equivalencias
```

### E.7 Módulo Documentación
```
src/electra_core/dominio/documentacion/
├── modelos.py           Documento, Capitulo, Seccion, Plantilla
├── servicios.py         ServicioGeneracionExpediente
└── eventos.py           DocumentoGenerado

src/electra_core/infraestructura/documentacion/
├── pdf.py               Generación PDF (weasyprint)
├── latex.py             Generación LaTeX
└── plantillas/          Templates Jinja2
```

---

## F. Árbol final optimizado

```
electra/
├── docs/                             Documentación
│   ├── architecture/                 Documento de arquitectura
│   ├── guias/                        Guías de uso
│   └── referencias/                  Normativa
│
├── src/
│   └── electra/                      Raíz del paquete Python
│       │
│       ├── aplicacion/               Capa de aplicación
│       │   ├── __init__.py
│       │   ├── puertos/              Interfaces entre capas
│       │   │   ├── repositorios.py   Puerto: persistencia
│       │   │   ├── exportadores.py   Puerto: CAD, BIM, PDF
│       │   │   └── precios.py        Puerto: cotización
│       │   ├── casos_uso/            Use cases / commands
│       │   │   ├── __init__.py
│       │   │   ├── extraer_croquis.py
│       │   │   ├── validar_arquitectura.py
│       │   │   ├── disenar_electrico.py
│       │   │   ├── ejecutar_calculos.py
│       │   │   ├── generar_planos.py
│       │   │   ├── cotizar_materiales.py
│       │   │   └── generar_expediente.py
│       │   ├── servicios/            Servicios de aplicación
│       │   │   ├── __init__.py
│       │   │   └── orquestador.py    Pipeline principal
│       │   ├── dto/                  Data Transfer Objects
│       │   │   ├── arquitectura.py
│       │   │   ├── electrico.py
│       │   │   ├── calculos.py
│       │   │   └── presupuesto.py
│       │   ├── cli/                  Interfaz CLI
│       │   │   ├── __init__.py
│       │   │   ├── main.py           Punto de entrada
│       │   │   ├── comandos/
│       │   │   │   ├── proyecto.py
│       │   │   │   ├── calculos.py
│       │   │   │   ├── cad.py
│       │   │   │   └── cotizacion.py
│       │   │   └── opciones.py       Opciones compartidas
│       │   └── web/                  Interfaz web (futuro)
│       │       └── calculadora/      Calculadora HTML (a migrar)
│       │
│       ├── dominio/                  Capa de dominio
│       │   ├── __init__.py
│       │   ├── shared/               Objetos compartidos
│       │   │   ├── value_objects.py  Coordenadas, Potencia, Seccion, Porcentaje
│       │   │   ├── enums.py          Tipos de circuito, conductor, normativa
│       │   │   └── eventos.py        Eventos de dominio base
│       │   │
│       │   ├── arquitectura/         Módulo Arquitectura
│       │   │   ├── modelos.py        Ambiente, Piso, Muro, Puerta, Escalera
│       │   │   ├── servicios.py      Validación de croquis
│       │   │   └── excepciones.py
│       │   │
│       │   ├── diseno_electrico/     Módulo Diseño Eléctrico
│       │   │   ├── modelos.py        Circuito, Carga, Tablero, Proteccion
│       │   │   └── servicios.py      Distribución y balanceo
│       │   │
│       │   ├── calculos/             Módulo Cálculos
│       │   │   ├── modelos.py        ResultadoDemanda, ConductorSeleccionado
│       │   │   ├── servicios.py      Cálculo de demanda, conductores, caída
│       │   │   └── estrategias/      Estrategias normativas
│       │   │       ├── base.py
│       │   │       ├── cne_peru.py   Implementación CNE Perú
│       │   │       └── iec.py        Implementación IEC
│       │   │
│       │   ├── presupuestos/         Módulo Presupuestos
│       │   │   ├── modelos.py        Material, BOMItem, Cotizacion
│       │   │   └── servicios.py      Cálculo BOM, comparativa
│       │   │
│       │   └── documentacion/        Módulo Documentación
│       │       ├── modelos.py        Documento, Capitulo, Plantilla
│       │       └── servicios.py      Generación de expediente
│       │
│       └── infraestructura/          Capa de infraestructura
│           ├── __init__.py
│           ├── persistencia/         Repositorios concretos
│           │   ├── repositorio_yaml.py
│           │   ├── repositorio_json.py
│           │   └── proyecto_loader.py
│           ├── cad/                  Adaptador CAD
│           │   ├── adaptador.py
│           │   ├── dxf_generator.py
│           │   ├── electrical_overlay.py
│           │   ├── auto_routing.py
│           │   ├── unifilar.py
│           │   ├── pdf.py
│           │   ├── simbologia/
│           │   └── ejemplos/
│           ├── bim/                  Adaptador BIM
│           │   ├── adaptador.py
│           │   └── exportador_ifc.py
│           ├── presupuestos/         Adaptadores de proveedores
│           │   ├── adaptador_promart.py
│           │   ├── adaptador_sodimac.py
│           │   ├── adaptador_maestro.py
│           │   ├── adaptador_mercadolibre.py
│           │   ├── normalizador.py
│           │   └── datos/            Reglas de matching, equivalencias
│           └── documentacion/        Adaptadores de documentos
│               ├── pdf.py            PDF via weasyprint
│               ├── latex.py          LaTeX
│               └── plantillas/       Templates
│
├── proyectos/                        Proyectos de clientes (sin cambios)
│   ├── aquiles/
│   └── renzo/
│
├── referencias/                      Normativa (sin cambios)
│
├── tests/                            Tests
│   ├── unit/                         Tests unitarios por módulo
│   │   ├── dominio/
│   │   │   ├── test_arquitectura.py
│   │   │   ├── test_diseno_electrico.py
│   │   │   ├── test_calculos.py
│   │   │   ├── test_presupuestos.py
│   │   │   └── test_documentacion.py
│   │   ├── aplicacion/
│   │   │   └── test_casos_uso.py
│   │   └── infraestructura/
│   │       ├── test_cad.py
│   │       ├── test_bim.py
│   │       └── test_persistencia.py
│   ├── integration/                  Tests de integración
│   │   ├── test_pipeline_completo.py
│   │   └── test_proyectos_legacy.py
│   └── fixtures/                    Datos de prueba
│       ├── proyecto_ejemplo.yaml
│       └── layout_ejemplo.json
│
├── pyproject.toml
├── README.md
└── AGENTS.md
```

---

## G. Plan de migración paso a paso

### Fase 0: Preparación (Semana 1)
```
[ ] Crear rama refactor/arquitectura-hexagonal
[ ] Congelar cambios en herramientas/ legacy
[ ] Ejecutar tests actuales y registrar baseline
[ ] Hito: tests pasan antes de tocar nada
```

### Fase 1: Unificar modelos de dominio (Semana 2-3)
```
[ ] Mover src/electra_core/modelos/topologia.py → src/electra/dominio/shared/
[ ] Unificar con herramientas/cotizacion/modelos.py
[ ] Agregar value objects: Coordenadas, Potencia, SeccionConductor
[ ] Crear enums unificados en dominio/shared/enums.py
[ ] Mantener compatibilidad: imports legacy funcionan
[ ] Hito: from electra.dominio.shared import RedElectrica
```

### Fase 2: Migrar cálculos (Semana 3-4)
```
[ ] Mover herramientas/calculos/scripts/calcular_instalacion.py → dominio/calculos/
[ ] Mover herramientas/calculos/datos/ → infraestructura o dominio/calculos/datos/
[ ] Refactor: inyectar estrategia normativa (Strategy Pattern)
[ ] Mantener CLI legacy como wrapper del nuevo módulo
[ ] Hito: python -m electra.aplicacion.cli calculos --proyecto aquiles
```

### Fase 3: Migrar CAD (Semana 5-6)
```
[ ] Mover herramientas/cad/scripts/ → infraestructura/cad/
[ ] Unificar con src/electra_core/dominios/cad/ → dominar la implementación completa
[ ] Mover simbologia/ → infraestructura/cad/simbologia/
[ ] Crear adaptador que implementa puerto de exportación CAD
[ ] Hito: ambos pipelines (legacy y nuevo) producen mismo DXF
```

### Fase 4: Migrar cotización (Semana 6-7)
```
[ ] Mover herramientas/cotizacion/ → infraestructura/presupuestos/
[ ] Mover src/electra_core/dominios/cotizaciones/ → dominio/presupuestos/
[ ] Unificar con herramientas/pipeline_automatizado.py:generar_bom()
[ ] Normalizador como servicio de dominio
[ ] Hito: cotización desde nuevo pipeline = mismo resultado
```

### Fase 5: Unificar pipelines (Semana 8-9)
```
[ ] Refactor orquestador: unificar herramientas/pipeline_automatizado.py + src/electra_core/orquestador/
[ ] Crear casos de uso independientes (extraer, calcular, generar, cotizar)
[ ] CLI nuevo usa casos de uso
[ ] CLI legacy redirige al nuevo
[ ] Hito: pipeline_automatizado.py es wrapper thin
```

### Fase 6: Documentación y BIM (Semana 10)
```
[ ] Migrar documentación a dominio/documentacion/
[ ] Migrar BIM a infraestructura/bim/
[ ] Plantillas a infraestructura/documentacion/plantillas/
[ ] Hito: generación de expediente unificada
```

### Fase 7: Limpieza (Semana 11)
```
[ ] Deprecar herramientas/ (todo migrado al core)
[ ] Mover calculadora web a aplicacion/web/
[ ] AGENTS.md actualizado
[ ] Hito: herramientas/ contiene solo README.md con referencia
```

### Fase 8: Polishing (Semana 12)
```
[ ] Tests de integración: pipeline completo desde YAML hasta PDF
[ ] CI/CD actualizado
[ ] Documentación de arquitectura finalizada
[ ] Hito: v1.0.0-alpha
```

---

## H. AGENTS.md — Ver archivo separado

## I. README — Ver archivo separado

## J. Roadmap técnico 12 meses

### Q3 2026 (Jul-Sep) — Foundation
```
Jul [Fase 0-1]: Modelos de dominio unificados
Aug [Fase 2-3]: Cálculos y CAD migrados
Sep [Fase 4-5]: Cotización y pipeline unificados
    🎯 Hito: v1.0.0-alpha — pipeline completo desde YAML
```

### Q4 2026 (Oct-Dic) — Features
```
Oct [Fase 6-7]: Documentación, BIM, limpieza
    🎯 Hito: v1.0.0 — release estable
Nov: Extracción de croquis vía IA (OpenCV + agente)
    - Detección de ambientes desde imagen
    - Extracción de muros y cotas
    - Generación automática de JSON arquitectura
Dec: Cuestionario interactivo web
    - UI drag & drop para componentes eléctricos
    - Export directo a pipeline
    - 🎯 Hito: v1.1.0 — croquis → proyecto completo
```

### Q1 2027 (Ene-Mar) — Automation
```
Jan: FastAPI REST API
    - Endpoints para cada caso de uso
    - Documentación OpenAPI
    - 🎯 Hito: v1.2.0 — API pública
Feb: Web frontend (React/Vue)
    - Carga de croquis
    - Editor visual de planos
    - Previsualización en tiempo real
Mar: Multi-proyecto y workspaces
    - 🎯 Hito: v1.3.0 — plataforma multi-usuario
```

### Q2 2027 (Abr-Jun) — Scale
```
Apr: Plugins / extensiones
    - Nuevos proveedores
    - Nuevas normativas (NEC, IEC completas)
    - 🎯 Hito: v2.0.0 — plataforma extensible
May: Optimizaciones
    - Caché de cálculos
    - Generación paralela de planos
    - Renderizado SVG en tiempo real
Jun: Release estable v2.1.0
    - Documentación completa
    - Tests de regresión automatizados
    - 🎯 Hito: v2.1.0 — production-ready
```
