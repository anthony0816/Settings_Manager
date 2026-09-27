import sys
from modules.logger.logger import log
from controllers.platform_handler import platform_handler


MIN_SPEED = 1
MAX_SPEED = 20
DEFAULT_SPEED = 10


class MouseController:
    def handle_speed(self, args):
        if len(args) != 1:
            log.error("Uso: wst mouse speed <valor>")
            log.info(f"Valor entre {MIN_SPEED} y {MAX_SPEED} (default: {DEFAULT_SPEED})")
            sys.exit(1)

        value_str = args[0]

        try:
            value = int(value_str)
        except ValueError:
            log.error(f"Valor invalido: '{value_str}'. Debe ser un numero entero.")
            sys.exit(1)

        if value < MIN_SPEED or value > MAX_SPEED:
            log.error(f"Valor fuera de rango: {value}. Debe estar entre {MIN_SPEED} y {MAX_SPEED}.")
            sys.exit(1)

        service = platform_handler.get_platform_service()
        service.set_mouse_speed(value)

        log.success(f"Velocidad del mouse cambiada a {value}")


def handle_mouse(args):
    if len(args) < 1:
        log.error("Uso: wst mouse <comando> [args...]")
        log.info("Comandos disponibles: speed")
        sys.exit(1)

    mc = MouseController()
    command = args[0].lower()

    if command == 'speed':
        mc.handle_speed(args[1:])
    else:
        log.error(f"Comando no soportado: '{command}'. Comandos disponibles: speed")
        sys.exit(1)