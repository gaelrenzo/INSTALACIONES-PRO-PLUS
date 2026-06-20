"""Orquestador de pipeline — casos de uso y coordinación del flujo de diseño eléctrico."""

from __future__ import annotations

from .dto import EtapaResultado, PipelineConfig, PipelineResultado
from .pipeline import Orquestador, ejecutar_pipeline_desde_cli

__all__ = [
    "Orquestador",
    "ejecutar_pipeline_desde_cli",
    "PipelineConfig",
    "PipelineResultado",
    "EtapaResultado",
]
