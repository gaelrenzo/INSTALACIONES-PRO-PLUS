"""DTOs para el orquestador de pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class EtapaResultado:
    nombre: str
    exitoso: bool
    mensaje: str = ""
    archivos_generados: Dict[str, Path] = field(default_factory=dict)
    datos: Any = None
    error: Optional[str] = None


@dataclass
class PipelineConfig:
    proyecto_id: str
    config_path: Path
    output_dir: Path
    proyecto_nombre: str = ""
    propietario: str = ""
    skip_cad: bool = False
    skip_bom: bool = False
    datos_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResultado:
    exitoso: bool
    proyecto_id: str
    etapas: List[EtapaResultado] = field(default_factory=list)
    datos: Dict[str, Any] = field(default_factory=dict)

    def agregar(self, etapa: EtapaResultado) -> None:
        self.etapas.append(etapa)
        if not etapa.exitoso:
            self.exitoso = False
