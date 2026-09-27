#!/usr/bin/env python3
"""
Controlador para acciones de tapa (lid).
"""

import sys
import subprocess

from modules.logger.logger import log

# GUIDs de configuración de energía de Windows
LID_CLOSE_ACTION_GUID = "5ca83367-6e45-459f-a27b-476b1d01c936"
SUB_BUTTONS = "SUB_BUTTONS"
SCHEME_CURRENT = "SCHEME_CURRENT"

# Mapeo de acciones a valores de powercfg
ACTION_MAP = {
    "nothing": 0,
    "sleep": 1,
    "hibernate": 2,
    "off": 3,
    "shutdown": 3,
    # Alias en español
    "nada": 0,
    "suspender": 1,
    "hibernar": 2,
    "apagar": 3,
}

# Mapeo de estado de energía
STATE_MAP = {
    "plug": "ac",
    "ac": "ac",
    "unplug": "dc",
    "dc": "dc",
    "both": "both",
    "ambos": "both",
}


def run_powercfg(args):
    """Ejecuta powercfg con los argumentos dados y maneja errores."""
    try:
        subprocess.run(
            ["powercfg"] + args,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        log.error(f"Error ejecutando powercfg {' '.join(args)}")
        if e.stderr:
            log.error(e.stderr.strip())
        sys.exit(1)


def set_lid_close_action(state, action_value):
    """
    Cambia la acción al cerrar la tapa.
    state: 'ac', 'dc' o 'both'
    action_value: 0=nada, 1=suspender, 2=hibernar, 3=apagar
    """
    if state in ("ac", "both"):
        run_powercfg([
            "/setacvalueindex", SCHEME_CURRENT, SUB_BUTTONS,
            LID_CLOSE_ACTION_GUID, str(action_value)
        ])
    if state in ("dc", "both"):
        run_powercfg([
            "/setdcvalueindex", SCHEME_CURRENT, SUB_BUTTONS,
            LID_CLOSE_ACTION_GUID, str(action_value)
        ])
    # Aplicar cambios al plan de energía activo
    run_powercfg(["/setactive", SCHEME_CURRENT])


def handle_lid(args):
    """
    Maneja el comando lid.
    args: lista con [state_arg, action_arg]
    """
    if len(args) != 2:
        log.error("Uso: wst lid {plug|unplug|both} {nothing|sleep|hibernate|off}")
        log.info("Ejemplo: wst lid unplug sleep")
        sys.exit(1)

    state_arg = args[0].lower()
    action_arg = args[1].lower()

    if state_arg not in STATE_MAP:
        log.error(f"Estado no válido: '{state_arg}'. Use: plug, unplug, both.")
        sys.exit(1)

    if action_arg not in ACTION_MAP:
        log.error(f"Acción no válida: '{action_arg}'. Use: nothing, sleep, hibernate, off.")
        sys.exit(1)

    state = STATE_MAP[state_arg]
    action_value = ACTION_MAP[action_arg]

    set_lid_close_action(state, action_value)
    ORANGE = "\033[38;5;208m"
    RESET = "\033[0m"
    log.success(f"Configuracion aplicada: al cerrar la tapa ({state_arg}) -> {ORANGE}{action_arg}{RESET}")