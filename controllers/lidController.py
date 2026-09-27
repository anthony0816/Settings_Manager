#!/usr/bin/env python3
"""
Controlador para acciones de tapa (lid).
"""

import sys

from modules.logger.logger import log
from controllers.platform_handler import platform_handler

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


def set_lid_close_action(state, action_value):
    """
    Cambia la acción al cerrar la tapa.
    state: 'ac', 'dc' o 'both'
    action_value: 0=nada, 1=suspender, 2=hibernar, 3=apagar
    """
    service = platform_handler.get_platform_service()
    service.set_lid_close_action(state, action_value)


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