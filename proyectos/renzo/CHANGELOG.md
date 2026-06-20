# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-06-13
### Changed
- Se separaron fuentes, datos canonicos, expediente, documentacion,
  entregables e historial.
- El pipeline usa tres layouts activos y un unico modelo electrico canonico.
- Los resultados regenerables se escriben en `build/renzo/`.
- Las fuentes LaTeX se trasladaron a `expediente/`.
- Las iteraciones `v1`, `v2` y `v3` se aislaron en `archivo/`.

### Removed
- Duplicados DXF/PDF/SVG y la carpeta `dwg/` que contenia archivos DXF.
- El paquete Python vacio y configuracion de empaquetado sin implementacion.
- Tres copias identicas del modelo electrico historico.

## [2.1.0] - 2026-06-12
### Added
- Integrated pytest test suite under `/tests` to validate electrical engineering formulas, including CNE-U 050-200 demand, voltage drop calculations, ITM sizing, and budgeting.
- Added `requirements.txt` and `pyproject.toml` for standard Python packaging.
- Added GitHub Actions CI pipeline in `.github/workflows/tests.yml` to run unit tests automatically.
- Integrated unified orchestrator script `scripts/build_project.py` to run the entire pipeline in a single command.

### Changed
- Restructured repository layout into numbered technical folders:
  - `01_memoria_descriptiva/` (centralized description in markdown)
  - `04_metrados/` (independent metrados folder)
  - `05_presupuesto/` (independent budgeting folder)
  - `06_planos/` (unifies sources, diagrams, and entregables)
  - `07_anexos/` (support figures and documents)
- Reorganized revision md files into `docs/revisiones/pisos/` and `docs/revisiones/circuitos/`.
- Consolidated diagrams in `06_planos/diagramas/`.

### Fixed
- Fixed unescaped LaTeX characters like `#` and unicode symbols like `≈` in `partidas/03-canalizaciones-tuberias.tex` to resolve compiler crashes.
- Fixed console encoding errors in python pipeline scripts under Windows.

## [2.0.0] - 2026-06-03
### Added
- Created modular python package `src/electrica_peru/`.
- Configured YAML settings in `config/` for project, rules, and vendors.
- Standardized relative paths in automation scripts.

## [1.0.0] - 2026-05-15
### Added
- Initial academic files for the LaTeX single-family residential electrical project.
