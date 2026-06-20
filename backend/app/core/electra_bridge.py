import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class ElectraBridge:
    def __init__(self):
        self._root = Path(__file__).resolve().parent.parent.parent.parent
        self._electra_pkg = self._root / "src" / "electra"

    def _import_electra(self):
        import sys
        sys.path.insert(0, str(self._root / "src"))

    def ejecutar_calculos(self, proyecto: Dict, pisos: List[Dict]) -> Dict:
        self._import_electra()
        from electra.aplicacion.cli.calculos import ejecutar_calculos
        with tempfile.TemporaryDirectory() as tmp:
            build_dir = Path(tmp)
            resultados = ejecutar_calculos(
                proyecto_data=proyecto,
                pisos_data=pisos,
                build_dir=build_dir,
            )
        return resultados

    def ejecutar_cad(self, proyecto: Dict, pisos: List[Dict], formato: str = "dxf") -> Dict:
        self._import_electra()
        from electra.aplicacion.cli.cad import ejecutar_cad
        with tempfile.TemporaryDirectory() as tmp:
            build_dir = Path(tmp)
            archivos = ejecutar_cad(
                proyecto_data=proyecto,
                pisos_data=pisos,
                build_dir=build_dir,
                formato=formato,
            )
        return archivos

    def ejecutar_cotizacion(self, proyecto: Dict, proveedores: Optional[List[str]] = None) -> Dict:
        self._import_electra()
        from electra.aplicacion.cli.cotizar import ejecutar_cotizacion
        with tempfile.TemporaryDirectory() as tmp:
            build_dir = Path(tmp)
            resultado = ejecutar_cotizacion(
                proyecto_data=proyecto,
                build_dir=build_dir,
                proveedores=proveedores,
            )
        return resultado

    def ejecutar_expediente(self, proyecto: Dict, compilar_pdf: bool = True) -> Dict:
        self._import_electra()
        from electra.infraestructura.reportes.expediente import generar_expediente
        with tempfile.TemporaryDirectory() as tmp:
            build_dir = Path(tmp)
            tex_path = generar_expediente(
                proyecto_id=proyecto["id"],
                build_dir=build_dir,
                output_path=str(build_dir / "expediente.tex"),
                compilar_pdf=compilar_pdf,
            )
            archivos = {"tex": tex_path}
            pdf_path = tex_path.replace(".tex", ".pdf")
            if os.path.exists(pdf_path):
                archivos["pdf"] = pdf_path
            return archivos
