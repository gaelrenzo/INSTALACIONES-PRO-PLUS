"""Entry point para python -m electra.aplicacion.cli <subcomando> [opciones]."""

from __future__ import annotations

import sys

COMMANDS = {}


def _register():
    from electra.aplicacion.cli.pipeline import build_parser as pp, run as pr
    COMMANDS["pipeline"] = (pp, pr)
    from electra.aplicacion.cli.calculos import build_parser as cp, run as cr
    COMMANDS["calculos"] = (cp, cr)
    from electra.aplicacion.cli.cad import build_parser as cadp, run as cadr
    COMMANDS["cad"] = (cadp, cadr)
    from electra.aplicacion.cli.bom import build_parser as bp, run as br
    COMMANDS["bom"] = (bp, br)
    from electra.aplicacion.cli.cotizar import build_parser as cotp, run as cotr
    COMMANDS["cotizar"] = (cotp, cotr)
    from electra.aplicacion.cli.expediente import build_parser as expp, run as expr
    COMMANDS["expediente"] = (expp, expr)


def main():
    _register()

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Uso: python -m electra.aplicacion.cli <subcomando> [opciones]")
        print("")
        print("Subcomandos disponibles:")
        for name in sorted(COMMANDS):
            print(f"  {name}")
        print("")
        print("Ayuda: python -m electra.aplicacion.cli <subcomando> --help")
        sys.exit(0 if len(sys.argv) < 2 else 1)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Comando desconocido: {cmd}")
        print(f"Usa: python -m electra.aplicacion.cli pipeline --proyecto <id>")
        sys.exit(1)

    build_parser, run_func = COMMANDS[cmd]
    parser = build_parser()
    args = parser.parse_args(sys.argv[2:])
    sys.exit(run_func(args))


if __name__ == "__main__":
    main()
