#!/usr/bin/env python3
"""
Script de Reorganización y Refactorización del Repositorio
Ajusta la estructura del proyecto al estándar profesional de consultoría (10/10).
"""

import os
import shutil
from pathlib import Path

# Directorio base del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def log(msg):
    print(f"[reorganize] {msg}")

def safe_move(src, dest):
    src_path = PROJECT_ROOT / src
    dest_path = PROJECT_ROOT / dest
    if src_path.exists():
        os.makedirs(dest_path.parent, exist_ok=True)
        shutil.move(str(src_path), str(dest_path))
        log(f"Movido: {src} -> {dest}")
    else:
        log(f"Omitido (no existe): {src}")

def main():
    log("Iniciando la reorganización del repositorio...")

    # 1. Crear directorios nuevos
    dirs_to_create = [
        "01_memoria_descriptiva",
        "04_metrados",
        "05_presupuesto",
        "06_planos/fuentes",
        "06_planos/entregables/dwg",
        "06_planos/entregables/dxf",
        "06_planos/entregables/pdf",
        "06_planos/entregables/png",
        "06_planos/diagramas",
        "07_anexos/fichas_tecnicas",
        "07_anexos/catastro",
        "07_anexos/normativa",
        "07_anexos/evidencias",
        "docs/revisiones/pisos",
        "docs/revisiones/circuitos",
        "tests"
    ]
    for d in dirs_to_create:
        os.makedirs(PROJECT_ROOT / d, exist_ok=True)
        log(f"Creado directorio: {d}")

    # 2. Mover archivos de documentación y memorias
    safe_move("docs/reportes/memoria-tecnica/memoria_descriptiva.md", "01_memoria_descriptiva/memoria_descriptiva.md")
    
    # 3. Separar metrados y presupuesto
    safe_move("04_metrados_y_presupuesto/metrados.xlsx", "04_metrados/metrados.xlsx")
    safe_move("04_metrados_y_presupuesto/presupuesto.xlsx", "05_presupuesto/presupuesto.xlsx")
    
    # Eliminar directorio anterior
    old_metrados_dir = PROJECT_ROOT / "04_metrados_y_presupuesto"
    if old_metrados_dir.exists() and not os.listdir(old_metrados_dir):
        old_metrados_dir.rmdir()
        log("Eliminado directorio vacío: 04_metrados_y_presupuesto")

    # 4. Reorganizar Revisiones
    # Buscar archivos md de pisos y circuitos
    revisiones_dir = PROJECT_ROOT / "docs" / "revisiones"
    if revisiones_dir.exists():
        for item in os.listdir(revisiones_dir):
            if item.startswith("revision_piso") and item.endswith(".md"):
                safe_move(f"docs/revisiones/{item}", f"docs/revisiones/pisos/{item}")
        
        # Mover carpeta interna revisiones/ a circuitos/
        old_rev_sub = revisiones_dir / "revisiones"
        if old_rev_sub.exists():
            for item in os.listdir(old_rev_sub):
                if item.endswith(".md"):
                    safe_move(f"docs/revisiones/revisiones/{item}", f"docs/revisiones/circuitos/{item}")
            try:
                old_rev_sub.rmdir()
                log("Eliminado directorio redundante: docs/revisiones/revisiones")
            except Exception as e:
                log(f"Error al eliminar docs/revisiones/revisiones: {e}")

    # 5. Mover diagramas a planos/diagramas
    diag_dir = PROJECT_ROOT / "diagramas"
    if diag_dir.exists():
        for item in os.listdir(diag_dir):
            safe_move(f"diagramas/{item}", f"06_planos/diagramas/{item}")
        try:
            diag_dir.rmdir()
            log("Eliminado directorio diagramas/")
        except Exception as e:
            log(f"Error al eliminar diagramas/: {e}")

    # 6. Mover planos a 06_planos
    old_planos_dir = PROJECT_ROOT / "planos"
    if old_planos_dir.exists():
        # Fuentes
        old_fuentes = old_planos_dir / "fuentes"
        if old_fuentes.exists():
            for item in os.listdir(old_fuentes):
                safe_move(f"planos/fuentes/{item}", f"06_planos/fuentes/{item}")
        # Entregables
        old_entregables = old_planos_dir / "entregables"
        if old_entregables.exists():
            for fmt in ["dwg", "dxf", "pdf", "png"]:
                fmt_dir = old_entregables / fmt
                if fmt_dir.exists():
                    for item in os.listdir(fmt_dir):
                        safe_move(f"planos/entregables/{fmt}/{item}", f"06_planos/entregables/{fmt}/{item}")
                    try:
                        fmt_dir.rmdir()
                    except:
                        pass
            try:
                old_entregables.rmdir()
            except:
                pass
        
        # Copiar cualquier archivo directo en planos/
        for item in os.listdir(old_planos_dir):
            item_path = old_planos_dir / item
            if item_path.is_file():
                safe_move(f"planos/{item}", f"06_planos/{item}")
        
        try:
            shutil.rmtree(str(old_planos_dir))
            log("Eliminada carpeta anterior planos/")
        except Exception as e:
            log(f"Error al limpiar planos/: {e}")

    # 7. Reorganizar figuras a Anexos
    fig_dir = PROJECT_ROOT / "figuras"
    if fig_dir.exists():
        safe_move("figuras/plano_catastral.png", "07_anexos/catastro/plano_catastral.png")
        safe_move("figuras/ubicacion_satelital.png", "07_anexos/evidencias/ubicacion_satelital.png")
        # Eliminar figuras/
        try:
            shutil.rmtree(str(fig_dir))
            log("Eliminada carpeta figuras/")
        except Exception as e:
            log(f"Error al eliminar figuras/: {e}")

    # 8. Editar LaTeX para usar nuevas rutas de figuras y planos
    memoria_tex = PROJECT_ROOT / "capitulos" / "01-memoria-descriptiva.tex"
    if memoria_tex.exists():
        with open(memoria_tex, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("figuras/plano_catastral.png", "07_anexos/catastro/plano_catastral.png")
        content = content.replace("figuras/ubicacion_satelital.png", "07_anexos/evidencias/ubicacion_satelital.png")
        with open(memoria_tex, "w", encoding="utf-8") as f:
            f.write(content)
        log("Actualizadas rutas de figuras en capitulos/01-memoria-descriptiva.tex")

    planos_tex = PROJECT_ROOT / "capitulos" / "07-planos.tex"
    if planos_tex.exists():
        with open(planos_tex, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("planos/entregables/", "06_planos/entregables/")
        with open(planos_tex, "w", encoding="utf-8") as f:
            f.write(content)
        log("Actualizadas rutas de planos en capitulos/07-planos.tex")

    log("Reorganización completada con éxito.")

if __name__ == "__main__":
    main()
