#!/usr/bin/env python3
"""
Gestor de ajustes de Windows desde la linea de comandos.

Uso:
    python wst_main.py lid    {plug|unplug|both} {nothing|sleep|hibernate|off}
python wst_main.py mouse speed <1-20>
    python wst_main.py folder status|show|hide|toggle [true|false]
    python wst_main.py screen {plug|unplug|both} {offscreen|sleep} <tiempo>
    python wst_main.py screen default
    python wst_main.py sc     {create|delete|ls}

Ejemplos:
    python wst_main.py lid unplug sleep       # Con bateria, al cerrar tapa -> suspender
    python wst_main.py lid plug hibernate     # Enchufado, al cerrar tapa -> hibernar
    python wst_main.py lid both nothing       # Ambos, al cerrar tapa -> no hacer nada
    python wst_main.py mouse speed 10         # Velocidad del mouse
    python wst_main.py folder toggle          # Alternar carpetas ocultas
    python wst_main.py screen both offscreen 5   # Apagar pantalla a los 5 min
    python wst_main.py screen plug sleep 20    # Dormir a los 20 min con cargador
    python wst_main.py screen unplug offscreen never  # No apagar con bateria
    python wst_main.py screen default         # 3 min para todo

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
from controllers.folder_controller import handle_folder
from controllers.screen_controller import handle_screen


GLOBAL_USAGE = """Comandos disponibles:
  lid    {plug|unplug|both} {nothing|sleep|hibernate|off}
  mouse  speed <1-20>
  folder status|show|hide|toggle [true|false]
  screen {plug|unplug|both} {offscreen|sleep} <tiempo>
  screen default | status
  sc     create <script> --name <nombre> | delete <nombre> | ls
  <nombre de shortcut definido en shortcut.json>"""


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
        log.error("Uso: python wst_main.py <comando> [args...]")
        log.info(GLOBAL_USAGE)
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
    elif command == 'folder':
        handle_folder(args)
    elif command == 'screen':
        handle_screen(args)
    else:
        sc = get_sortcut_if_exist(command)
        if sc:
            new_args = sc['script'].split()
            entry(new_args[0], new_args[1:])
            return
        log.error(f"Comando no soportado: '{command}'")
        log.info(GLOBAL_USAGE)
        sys.exit(1)


if __name__ == "__main__":
    elevate_if_needed()
    main()