"""Conectores de proveedores — wrapper legacy.

DEPRECATED: Usa electra.infraestructura.presupuestos.proveedores en su lugar.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "herramientas/cotizacion/proveedores esta obsoleto. "
    "Usa electra.infraestructura.presupuestos.proveedores",
    DeprecationWarning, stacklevel=2,
)

from electra.infraestructura.presupuestos.proveedores import (  # noqa: F401
    PROVEEDORES_DISPONIBLES,
    MaestroProveedor,
    MercadoLibreProveedor,
    PromartProveedor,
    SodimacProveedor,
    VentasPeruProveedor,
)

