#!/usr/bin/env python3
"""
Uso:
    python wst.py lid {plug|unplug|both} {nothing|sleep|hibernate|off}

Ejemplos:
    python wst.py lid unplug sleep       # Con batería, al cerrar tapa -> suspender
    python wst.py lid plug hibernate     # Enchufado, al cerrar tapa -> hibernar
    python wst.py lid both nothing       # Ambos, al cerrar tapa -> no hacer nada
    python wst.py lid unplug off         # Con batería, al cerrar tapa -> apagar

Se auto-eleva con gsudo si no tiene privilegios de administrador.
Requiere tener gsudo instalado y en el PATH.
"""

import sys
import subprocess

try:
    import gsudo
except ImportError:
    gsudo = None

from controllers.lidController import handle_lid
from modules.logger.logger import log
from modules.shortcut.shorcut import handle_shorcut, get_sortcut_if_exist
from controllers.mause_controller import handle_mouse


def elevate_if_needed():
    """Re-ejecuta el script a través de gsudo si no somos administrador."""
    if gsudo is None:
        log.warn("gsudo no instalado, ejecutando sin elevacion")
        return
    if not gsudo.is_admin():
        result = subprocess.run(["gsudo", sys.executable, *sys.argv])
        sys.exit(result.returncode)


def main():
    if len(sys.argv) < 2:
        log.error("Uso: python wst.py <comando> [args...]")
        log.info("Comandos disponibles: lid")
        sys.exit(1)

    command = sys.argv[1].lower()
    args = sys.argv[2:]
    entry(command, args)


def entry(command, args):
    if command == "lid":
        handle_lid(args)
    elif command == 'sc':
        handle_shorcut(args)
    elif command == 'mouse':
        handle_mouse(args)
    else:
        sc = get_sortcut_if_exist(command)
        if sc:
            new_args = sc['script'].split()
            entry(new_args[0], new_args[1:])
            return
        log.error(f"Comando no soportado: '{command}'. Comandos disponibles: lid")
        sys.exit(1)


if __name__ == "__main__":
    elevate_if_needed()
    main()