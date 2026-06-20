"""Orquestador unificado del pipeline de diseño eléctrico.

Coordina las etapas de cálculo, CAD, BOM y cotización
usando los módulos de dominio e infraestructura de Electra.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from electra.aplicacion.orquestador.dto import (
    EtapaResultado,
    PipelineConfig,
    PipelineResultado,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
PROJECTS_DIR = REPO_ROOT / "proyectos"


class Orquestador:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self._calculo_json: Optional[Path] = None

    @classmethod
    def desde_proyecto(
        cls,
        proyecto_id: str,
        output_dir: Optional[Path] = None,
        skip_cad: bool = False,
        skip_bom: bool = False,
    ) -> Orquestador:
        config_path = PROJECTS_DIR / proyecto_id / "proyecto.yaml"
        if not config_path.exists():
            config_path = PROJECTS_DIR / proyecto_id / "proyecto.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Configuracion no encontrada: {proyecto_id}")

        with open(config_path, encoding="utf-8") as f:
            datos = yaml.safe_load(f) if config_path.suffix in (".yaml", ".yml") else json.load(f)

        out = output_dir or REPO_ROOT / "build" / proyecto_id

        cfg = PipelineConfig(
            proyecto_id=proyecto_id,
            config_path=config_path,
            output_dir=out,
            proyecto_nombre=datos.get("proyecto", proyecto_id),
            propietario=datos.get("propietario", ""),
            skip_cad=skip_cad,
            skip_bom=skip_bom,
            datos_config=datos,
        )
        return cls(cfg)

    def ejecutar(self) -> PipelineResultado:
        resultado = PipelineResultado(
            exitoso=True,
            proyecto_id=self.config.proyecto_id,
        )
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        resultado.agregar(self._etapa_calculos())
        if not resultado.exitoso:
            return resultado

        if not self.config.skip_cad:
            resultado.agregar(self._etapa_cad())

        if not self.config.skip_bom:
            resultado.agregar(self._etapa_bom())

        return resultado

    def _etapa_calculos(self) -> EtapaResultado:
        from electra.dominio.calculos import CNEPeru

        try:
            config = self.config.datos_config
            pisos = config.get("pisos", [])
            circuitos_data = []
            for piso in pisos:
                for c in piso.get("circuitos", []):
                    circuitos_data.append({
                        "id": c.get("id", f"C{len(circuitos_data)+1}"),
                        "descripcion": f"{c['uso']} - {piso['nombre']}",
                        "potencia_instalada_w": c["potencia_w"],
                        "factor_demanda": c.get("factor_demanda", 1.0),
                        "longitud_m": c.get("longitud_m", 15.0),
                        "seccion_conductor_mm2": c.get("seccion_mm2", 2.5),
                    })

            calculo_dir = self.config.output_dir / "calculos"
            calculo_dir.mkdir(parents=True, exist_ok=True)

            cne = CNEPeru()
            resultados_circuitos = []
            for c in circuitos_data:
                params = {
                    "potencia_w": c["potencia_instalada_w"],
                    "tension_v": config.get("tension_v", 220),
                    "fases": config.get("fases", 1),
                    "longitud_m": c["longitud_m"],
                    "factor_potencia": config.get("factor_potencia", 0.90),
                    "factor_diseno": config.get("factor_diseno", 1.25),
                }
                try:
                    calc = cne.calcular_conductor(**params)
                except Exception:
                    calc = self._calculo_fallback(params)

                calc["id"] = c["id"]
                calc["descripcion"] = c["descripcion"]
                calc["longitud_m"] = c["longitud_m"]
                resultados_circuitos.append(calc)

            resumen = self._resumen_calculos(resultados_circuitos, config)

            data = {
                "proyecto": self.config.proyecto_nombre,
                "propietario": self.config.propietario,
                "escenario_dimensionamiento": {
                    "circuitos_calculados": resultados_circuitos,
                    "resumen_general": resumen,
                },
            }

            calculo_path = calculo_dir / "resultados.json"
            with open(calculo_path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._calculo_json = calculo_path

            return EtapaResultado(
                nombre="Calculos",
                exitoso=True,
                mensaje=f"{len(resultados_circuitos)} circuitos calculados",
                archivos_generados={"resultados": calculo_path},
                datos=data,
            )
        except Exception as e:
            return EtapaResultado(
                nombre="Calculos",
                exitoso=False,
                mensaje="Error en calculos",
                error=str(e),
            )

    def _calculo_fallback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        potencia = params["potencia_w"]
        tension = params["tension_v"]
        fases = params.get("fases", 1)
        cosphi = params.get("factor_potencia", 0.90)
        longitud = params.get("longitud_m", 15)
        fd = params.get("factor_diseno", 1.25)

        if fases == 1:
            ib = potencia / (tension * cosphi)
        else:
            ib = potencia / (tension * 1.732 * cosphi)

        ib_diseno = ib * fd
        seccion = 2.5 if ib_diseno <= 24 else 4.0 if ib_diseno <= 32 else 6.0 if ib_diseno <= 40 else 10.0
        itm = f"{fases}P {max(10, round(ib * 1.25 / 5) * 5)}A"
        return {
            "potencia_calculo_w": potencia,
            "corriente_ib_a": round(ib, 2),
            "corriente_diseno_id_a": round(ib_diseno, 2),
            "seccion_conductor_mm2": seccion,
            "itm_sugerido": itm,
            "caida_tension_porc": round(2 * 0.0175 * longitud * ib_diseno / seccion / tension * 100, 3),
        }

    def _resumen_calculos(
        self, circuitos: list[Dict[str, Any]], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        potencia_total = sum(c.get("potencia_calculo_w", 0) for c in circuitos)
        ib_total = sum(c.get("corriente_ib_a", 0) for c in circuitos)
        return {
            "potencia_instalada_total_w": potencia_total,
            "maxima_demanda_adoptada_w": round(potencia_total * 0.7, 0),
            "corriente_empleo_ib_total_a": round(ib_total, 2),
            "alimentador_seccion_mm2": 10.0,
            "alimentador_itm_sugerido": f"2P {max(40, round(ib_total * 1.25 / 5) * 5)}A",
            "alimentador_caida_tension_porc": 0.0,
            "alimentador_longitud_m": config.get("longitud_alimentador_m", 10),
        }

    def _etapa_cad(self) -> EtapaResultado:
        from electra.aplicacion.orquestador.casos_uso import generar_cad

        return generar_cad.ejecutar(
            self.config.proyecto_id,
            self.config.datos_config,
            self._calculo_json,
            self.config.output_dir,
        )

    def _etapa_bom(self) -> EtapaResultado:
        from electra.aplicacion.orquestador.casos_uso import generar_bom

        return generar_bom.ejecutar(
            self.config.proyecto_id,
            self.config.datos_config,
            self._calculo_json,
            self.config.output_dir,
        )

    def _etapa_cotizacion(self) -> EtapaResultado:
        from electra.aplicacion.orquestador.casos_uso import generar_cotizacion

        return generar_cotizacion.ejecutar(
            self.config.proyecto_id,
            self.config.datos_config,
            self._calculo_json,
            self.config.output_dir,
        )


def ejecutar_pipeline_desde_cli(args: Any) -> int:
    if getattr(args, "generar_ejemplo", False):
        _generar_config_ejemplo(args.output_dir)
        return 0

    skip_cad = getattr(args, "skip_cad", False)
    skip_bom = getattr(args, "skip_bom", False)

    if args.proyecto:
        try:
            orch = Orquestador.desde_proyecto(
                args.proyecto,
                output_dir=Path(args.output_dir) if args.output_dir else None,
                skip_cad=skip_cad,
                skip_bom=skip_bom,
            )
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
    else:
        print("ERROR: Especifica --proyecto <id>", file=sys.stderr)
        return 1

    resultado = orch.ejecutar()

    for etapa in resultado.etapas:
        status = "OK" if etapa.exitoso else "FAIL"
        print(f"  [{status}] {etapa.nombre}: {etapa.mensaje}")
        if not etapa.exitoso and etapa.error:
            print(f"         Error: {etapa.error}")

    return 0 if resultado.exitoso else 1


def _generar_config_ejemplo(output_dir: Optional[str] = None) -> None:
    out = Path(output_dir or REPO_ROOT / "build" / "ejemplo")
    out.mkdir(parents=True, exist_ok=True)
    ejemplo_path = out / "proyecto_ejemplo.yaml"
    ejemplo = _ejemplo_yaml()
    with open(ejemplo_path, "w", encoding="utf-8") as f:
        f.write(ejemplo)
    print(f"Configuracion de ejemplo: {ejemplo_path}")
    print(f"Ejecuta: python -m electra.aplicacion.cli.pipeline --proyecto ejemplo")


def _ejemplo_yaml() -> str:
    return """proyecto: "Vivienda Unifamiliar - Ejemplo"
propietario: "Juan Perez"
distrito: "San Miguel"
provincia: "San Roman"
departamento: "Puno"

tension_v: 220
fases: 1
factor_potencia: 0.90
factor_diseno: 1.25

longitud_alimentador_m: 12.0

tablero_general:
  x: 2.0
  y: 2.0
medidor:
  x: 0.5
  y: 0.5

pisos:
  - nombre: "Primer Piso"
    circuitos:
      - id: C1
        uso: "Alumbrado 1er Piso"
        potencia_w: 120
        factor_demanda: 1.0
        longitud_m: 15.0
        seccion_mm2: 2.5
        tubo_mm: 20
      - id: C2
        uso: "Tomacorrientes 1er Piso"
        potencia_w: 1800
        factor_demanda: 0.70
        longitud_m: 20.0
        seccion_mm2: 2.5
        tubo_mm: 20
    luminarias:
      - id: L1
        x: 3.0
        y: 3.0
        circuit: C1
    interruptores:
      - id: S1
        x: 2.2
        y: 2.8
        circuit: C1
        kind: simple
    tomacorrientes:
      - id: T1
        x: 2.5
        y: 1.5
        circuit: C2
        kind: doble

  - nombre: "Segundo Piso"
    circuitos:
      - id: C4
        uso: "Alumbrado 2do Piso"
        potencia_w: 100
        factor_demanda: 1.0
        longitud_m: 12.0
        seccion_mm2: 2.5
        tubo_mm: 20
      - id: C5
        uso: "Tomacorrientes 2do Piso"
        potencia_w: 1500
        factor_demanda: 0.70
        longitud_m: 18.0
        seccion_mm2: 2.5
        tubo_mm: 20
"""
