from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from electra_core.interfaces.puertos import GeneradorDocumento
from electra_core.modelos.topologia import RedElectrica


class GeneradorPDF(GeneradorDocumento):
    def __init__(self, ruta_plantillas: str = "plantillas") -> None:
        self.env = Environment(loader=FileSystemLoader(ruta_plantillas))

    def generar_reporte(self, red: RedElectrica, plantilla: str = "reporte_tecnico.html") -> str:
        from weasyprint import HTML
        template = self.env.get_template(plantilla)
        html = template.render(red=red)
        pdf_path = f"{red.nombre_proyecto}_reporte.pdf"
        HTML(string=html).write_pdf(pdf_path)
        return pdf_path
