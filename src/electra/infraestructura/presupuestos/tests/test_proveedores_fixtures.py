import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE.parents[1]))  # src/

from electra.infraestructura.presupuestos.proveedores import PROVEEDORES_DISPONIBLES


def test_parsea_fixtures_con_precio():
    fixtures = BASE / "tests" / "fixtures" / "html_muestras"
    for slug in ["promart", "sodimac", "maestro", "mercadolibre"]:
        provider = PROVEEDORES_DISPONIBLES[slug]()
        provider.last_url = f"fixture://{slug}.html"
        html = (fixtures / f"{slug}.html").read_text(encoding="utf-8")
        resultados = provider.parsear_resultados(html, "cable electrico thw 2.5 mm2 cobre")
        assert resultados, slug
        assert any(r.precio is not None for r in resultados), slug
        assert all(r.proveedor == provider.nombre for r in resultados)
