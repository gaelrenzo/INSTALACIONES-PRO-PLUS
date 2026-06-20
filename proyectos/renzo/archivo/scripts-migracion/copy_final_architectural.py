import os
import shutil

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
planos_cad_dir = os.path.join(base_dir, "planos_cad")
planos_dir = os.path.join(base_dir, "planos")

# List of mappings: (source_filename, destination_filename_in_planos_cad, destination_filename_in_planos)
mappings = [
    ("primer_piso_v3", "plano_arquitectonico_piso1", "primer-piso"),
    ("segundo_piso_v3", "plano_arquitectonico_piso2", "segundo-piso"),
    ("tercer_piso_v3", "plano_arquitectonico_piso3", "tercer-piso")
]

for src, dest_cad, dest_planos in mappings:
    # Copy DXF
    src_dxf = os.path.join(planos_cad_dir, f"{src}.dxf")
    dest_cad_dxf = os.path.join(planos_cad_dir, f"{dest_cad}.dxf")
    dest_planos_dxf = os.path.join(planos_dir, f"{dest_planos}.dxf")
    
    shutil.copy2(src_dxf, dest_cad_dxf)
    shutil.copy2(src_dxf, dest_planos_dxf)
    print(f"Copiado DXF: {src_dxf} -> {dest_cad_dxf} & {dest_planos_dxf}")
    
    # Copy PDF
    src_pdf = os.path.join(planos_cad_dir, f"{src}.pdf")
    dest_cad_pdf = os.path.join(planos_cad_dir, f"{dest_cad}.pdf")
    dest_planos_pdf = os.path.join(planos_dir, f"{dest_planos}.pdf")
    
    shutil.copy2(src_pdf, dest_cad_pdf)
    shutil.copy2(src_pdf, dest_planos_pdf)
    print(f"Copiado PDF: {src_pdf} -> {dest_cad_pdf} & {dest_planos_pdf}")

print("Consolidación de planos arquitectónicos finalizada con éxito.")
