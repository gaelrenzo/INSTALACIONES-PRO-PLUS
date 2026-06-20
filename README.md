# Electra Platform

> Plataforma de ingeniería eléctrica para transformar croquis arquitectónicos en diseños eléctricos completos, cálculos normativos CNE, planos CAD, expedientes técnicos PDF y presupuestos automatizados.

**Arquitectura:** DDD + Hexagonal · **Python** 3.11+ · **Pydantic** v2 · **ezdxf** · **CNE Perú**

> Toda salida técnica requiere revisión humana y contraste con el Código Nacional de Electricidad, el RNE y las condiciones reales de obra.

---

## Características

| Módulo | Descripción | Estado |
|--------|-------------|--------|
| 🏗️ **Arquitectura** | Extracción de ambientes, muros, puertas, ventanas desde croquis | ⚙️ Manual (IA) |
| ⚡ **Diseño Eléctrico** | Luminarias, tomacorrientes, interruptores, circuitos por ambiente | ✅ |
| 🔢 **Cálculos CNE** | Demanda, conductores, protecciones, caída de tensión, BOM | ✅ |
| 📐 **CAD** | Planos DXF arquitectónicos + superposición eléctrica + PDF | ✅ |
| 🔣 **Simbología DGE** | Biblioteca de símbolos normativos para planos eléctricos | ✅ |
| 🏛️ **BIM** | Exportación IFC (ifcopenshell) | ⚙️ Parcial |
| 💰 **Presupuestos** | BOM → cotización multi-proveedor | ✅ |
| 📄 **Expediente** | Memoria descriptiva, cálculos, especificaciones, metrados, planos | ✅ |

## Flujo completo

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ CROQUIS  │──▶│ ARQUITEC │──▶│ ELÉCTRIC │──▶│ CÁLCULOS │──▶│   CAD    │
│ (imagen) │   │ TURA     │   │ O        │   │ CNE      │   │ DXF/PDF  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                                   │              │
                                                   ▼              ▼
                                              ┌──────────┐   ┌──────────┐
                                              │    BOM   │   │ UNIFILAR │
                                              └────┬─────┘   └────┬─────┘
                                                   │              │
                                                   ▼              ▼
                                              ┌──────────┐   ┌──────────┐
                                              │ COTIZAR  │   │ EXPEDIENT│
                                              │ Multi-   │   │ E TÉCNIC │
                                              │ proveed. │   │ O PDF    │
                                              └──────────┘   └──────────┘
```

## Roadmap

```
Q3 2026 ── Foundation ── Modelos unificados, cálculos y CAD migrados a nueva arquitectura
Q4 2026 ── Features ──── Extracción de croquis vía IA, UI interactiva drag & drop
Q1 2027 ── Automation ── FastAPI REST API, web frontend, multi-proyecto
Q2 2027 ── Scale ─────── Plugins, nuevas normativas (NEC, IEC), optimizaciones
```

Ver plan de migración detallado en `docs/architecture/README.md`.

---

## Estructura

```text
.
├── AGENTS.md                        Reglas de trabajo para agentes IA
├── Makefile                         Comandos frecuentes (test, lint)
├── requirements.txt                 Dependencias Python
├── pyproject.toml                   Proyecto electra_core (src/)
│
├── docs/                            Arquitectura, flujo y politica de datos
│   ├── arquitectura.md              Principios y estructura del repositorio
│   ├── flujo-agentes.md             Flujo de trabajo con agentes IA
│   └── politica-datos.md            Politica de datos canonicos
│
├── src/electra_core/                Plataforma Python (DDD + Hexagonal)
│   ├── core/                        Logica base (normativas CNE/IEC, topologia, resolver)
│   ├── dominios/                    Modulos de negocio (CAD, BIM, calculos, cotizaciones, documentos)
│   ├── modelos/                     Modelos Pydantic (RedElectrica, Circuito, etc.)
│   ├── interfaces/                  Puertos (contratos entre capas)
│   └── orquestador/                 Pipeline de ejecucion (Orquestador)
│
├── herramientas/                    Motores reutilizables
│   ├── pipeline_automatizado.py     Orquestador principal CLI
│   ├── cad/                         Generacion de planos DXF/PDF
│   │   ├── scripts/                 dxf_generator, electrical_overlay, auto_routing, unifilar
│   │   ├── examples/                layout.json de ejemplo
│   │   └── cad-scripts/             Exportacion a PDF via QCAD
│   ├── calculos/                    Motor de calculos electricos
│   │   ├── scripts/                 calcular_instalacion, generar_bom
│   │   ├── datos/                   ampacidades.yaml (tabla CNE)
│   │   └── docs/                    Notas de formulas
│   ├── cotizacion/                  Cotizacion multi-proveedor
│   │   ├── proveedores/             Conectores: Promart, Sodimac, Maestro, MercadoLibre
│   │   ├── tests/                   Pruebas con fixtures HTML
│   │   └── data/                    Reglas de normalizacion y equivalencias
│   ├── simbologia/                  Biblioteca de simbolos DGE
│   │   └── scripts/                 Generador de catalogo DXF
│   └── calculadora/                 Calculadora web interactiva HTML
│
├── proyectos/                       Proyectos de vivienda
│   ├── aquiles/                     Vivienda de 2 pisos
│   │   ├── fuentes/                 Croquis, documentos, fotos
│   │   ├── arquitectura/            Datos canonicos de arquitectura
│   │   ├── diseno-electrico/        Datos canonicos de diseno electrico
│   │   ├── presupuesto/             BOM, cotizaciones, comparativa
│   │   └── expediente/              Documento tecnico (capitulos, docs)
│   └── renzo/                       Vivienda de 3 pisos
│       ├── fuentes/                 Croquis, catastro, ubicacion
│       ├── arquitectura/            Datos canonicos de arquitectura
│       ├── diseno-electrico/        Datos canonicos de diseno electrico
│       ├── scripts/                 Pipeline nativo (construir_expediente.py)
│       ├── tests/                   Tests de calculos del proyecto
│       └── expediente/              Documento tecnico
│
├── plantillas/                      Plantillas HTML (reporte_tecnico.html)
├── referencias/                     Normativa versionada
│   └── normativa/                   CNE, fichas, PDFs
├── tests/                           Tests del core (topologia, caida tension, DXF, pipeline)
└── build/                           Resultados regenerables (ignorado por Git)
```

## Inicio rapido

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
make test
```

Pipeline general de Aquiles:

```bash
python3 herramientas/pipeline_automatizado.py --proyecto aquiles
```

Pipeline nativo y expediente de Renzo:

```bash
python3 herramientas/pipeline_automatizado.py --proyecto renzo
# equivalente: cd proyectos/renzo && python3 scripts/construir_expediente.py
```

Calculadora web interactiva:

```bash
start herramientas/calculadora/index.html
```

Todas las ejecuciones escriben resultados regenerables en `build/<proyecto>/`.

## Flujo completo

```
CROQUIS (imagen) ──→ Agente IA extrae ambientes, muros, cotas
                           ↓
                    JSON arquitectura (rooms, walls, doors, windows)
                           ↓
CUESTIONARIO ──→ Usuario define componentes por ambiente
                           ↓
                    JSON componentes (luminarias, tomacorrientes, equipos)
                           ↓
                    YAML del proyecto
                           ↓
                    pipeline_automatizado.py
                           ↓
                    Calculos → DXF → PDF → BOM → Cotizacion → Expediente
```

## Flujo esperado

1. Conservar el croquis original sin modificarlo.
2. Extraer geometria, ambientes, cotas e incertidumbres a JSON.
3. Validar la planta arquitectonica antes del diseno electrico.
4. Definir cargas, circuitos, protecciones, conductores y canalizaciones.
5. Ejecutar calculos, CAD, BOM y cotizacion.
6. Registrar observaciones y revision humana.
7. Publicar unicamente resultados aprobados en `entregables/`.

## Documentación

| Recurso | Descripción |
|---------|-------------|
| `docs/architecture/README.md` | Arquitectura DDD + Hexagonal: clasificación, duplicidades, plan de migración, roadmap 12 meses |
| `docs/flujo-agentes.md` | Flujo de trabajo detallado con agentes IA |
| `docs/arquitectura.md` | Principios y estructura del repositorio |
| `AGENTS.md` | Reglas completas para desarrollo asistido por IA |

## Convenciones

- **Capas**: Dominio → Aplicación → Infraestructura. Dependencias solo hacia adentro.
- **Reutilización**: Las herramientas NO deben contener nombres, rutas ni datos exclusivos de un proyecto.
- **Inmutabilidad**: `fuentes/` nunca se modifica. `build/` es regenerable. `archivo/` no es entrada activa.
- **Trazabilidad**: Separar dato observado, dato calculado, supuesto y decisión humana.
- **Calidad**: Tipado obligatorio, tests por módulo, CI en GitHub Actions.

## Datos pesados y respaldos

`referencias/local/` y `proyectos/*/fuentes/local/` contienen material pesado o restringido que no se sube a Git.

Consulta [docs/arquitectura.md](docs/arquitectura.md), [docs/flujo-agentes.md](docs/flujo-agentes.md) y [AGENTS.md](AGENTS.md) antes de modificar datos canonicos.
