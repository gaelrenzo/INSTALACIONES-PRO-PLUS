"""Conectores de proveedores para el cotizador multi-proveedor."""

from .promart import PromartProveedor
from .sodimac import SodimacProveedor
from .maestro import MaestroProveedor
from .mercadolibre import MercadoLibreProveedor
from .ventas_peru import VentasPeruProveedor


PROVEEDORES_DISPONIBLES = {
    "promart": PromartProveedor,
    "sodimac": SodimacProveedor,
    "maestro": MaestroProveedor,
    "mercadolibre": MercadoLibreProveedor,
    "ventas_peru": VentasPeruProveedor,
}

