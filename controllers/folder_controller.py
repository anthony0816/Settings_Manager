import sys

from controllers.platform_handler import platform_handler
from modules.logger.logger import log
from services.folder_service import FolderService


USAGE = """Uso: wst folder <comando> [args...]

Comandos:
  status             Muestra el estado actual (no modifica nada)
  show               Muestra las carpetas/archivos ocultos
  hide               Oculta las carpetas/archivos ocultos
  toggle [true|false] Alterna el estado; true=mostrar, false=ocultar
                     (sin args = alternar)

Ejemplos:
  wst folder status
  wst folder toggle"""

SHOW_ALIASES = ("true", "1", "on", "yes", "show")
HIDE_ALIASES = ("false", "0", "off", "no", "hide")


class FolderController:
    def __init__(self, service_factory):
        self._service_factory = service_factory

    def _service(self) -> FolderService:
        return FolderService(self._service_factory())

    def show_status(self, args):
        if args:
            log.error("El comando 'status' no acepta argumentos")
            log.info(USAGE)
            sys.exit(1)

        self._report(self._service().get_status())

    def switch_hidden_status(self, args):
        value = None

        if len(args) > 1:
            log.error("Demasiados argumentos")
            log.info(USAGE)
            sys.exit(1)

        if args:
            arg = args[0].lower()
            if arg in SHOW_ALIASES:
                value = True
            elif arg in HIDE_ALIASES:
                value = False
            else:
                log.error(f"Valor invalido: '{args[0]}'. Use: true, false, o nada para toggle")
                log.info(USAGE)
                sys.exit(1)

        self._service().switch_hidden_status(value)
        self._report(self._service().get_status())

    def _report(self, visible: bool):
        estado = "visibles" if visible else "ocultas"
        log.success(f"Carpetas ocultas: {estado}")


folderController = FolderController(platform_handler.get_platform_service)


def handle_folder(args):
    if not args:
        log.error("Uso: wst folder <comando> [args...]")
        log.info(USAGE)
        sys.exit(1)

    command = args[0].lower()
    args = args[1:]

    handlers = {
        "status": folderController.show_status,
        "get": folderController.show_status,
        "show": folderController.switch_hidden_status,
        "hide": folderController.switch_hidden_status,
        "toggle": folderController.switch_hidden_status,
    }

    handler = handlers.get(command)

    if not handler:
        log.error(f"Comando no soportado: '{command}'")
        log.info(USAGE)
        sys.exit(1)

    try:
        handler(args)
    except OSError as e:
        log.error(f"No se pudo completar la operacion: {e}")
        sys.exit(1)