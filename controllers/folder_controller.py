import sys

from controllers.platform_handler import platform_handler
from modules.logger.logger import log
from services.folder_service import FolderService


USAGE = """Uso: wst folder <comando> [args...]

Comandos:
  status      Muestra el estado actual (no modifica nada)
  show        Muestra las carpetas/archivos ocultos
  hide        Oculta las carpetas/archivos ocultos
  toggle      Alterna el estado (unico comando que alterna)
  toggle [true|false]
              Fuerza mostrar u ocultar sin alternar

Ejemplos:
  wst folder status
  wst folder show
  wst folder hide
  wst folder toggle
  wst folder toggle true"""

SHOW_ALIASES = ("true", "1", "on", "yes", "show")
HIDE_ALIASES = ("false", "0", "off", "no", "hide")


class FolderController:
    def __init__(self, service_factory):
        self._service_factory = service_factory

    def _service(self) -> FolderService:
        return FolderService(self._service_factory())

    def _no_args(self, args, command):
        if args:
            log.error(f"El comando '{command}' no acepta argumentos")
            log.info(USAGE)
            sys.exit(1)

    def show_status(self, args):
        self._no_args(args, "status")
        self._report(self._service().get_status())

    def show_hidden(self, args):
        self._no_args(args, "show")
        self._apply(True, "show")

    def hide_hidden(self, args):
        self._no_args(args, "hide")
        self._apply(False, "hide")

    def toggle_hidden(self, args):
        if len(args) > 1:
            log.error("Demasiados argumentos")
            log.info(USAGE)
            sys.exit(1)

        value = None

        if args:
            arg = args[0].lower()
            if arg in SHOW_ALIASES:
                value = True
            elif arg in HIDE_ALIASES:
                value = False
            else:
                log.error(f"Valor invalido: '{args[0]}'. Use: true, false, o nada para alternar")
                log.info(USAGE)
                sys.exit(1)

        self._apply(value, "toggle")

    def _apply(self, value, command):
        service = self._service()
        anterior = service.get_status()
        service.switch_hidden_status(value)
        actual = service.get_status()
        estado = self._estado(actual)

        if value is None:
            if actual != anterior:
                log.success(f"Carpetas ocultas alternadas: ahora {estado}")
            else:
                log.warn("No se pudo alternar el estado de carpetas ocultas")
            return

        if actual == anterior:
            log.info(f"Sin cambios: las carpetas ocultas ya estaban {estado} ('{command}')")
        else:
            log.success(f"Carpetas ocultas: {estado} ('{command}')")

    @staticmethod
    def _estado(visible: bool) -> str:
        return "visibles" if visible else "ocultas"

    def _report(self, visible: bool):
        log.success(f"Carpetas ocultas: {self._estado(visible)}")


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
        "show": folderController.show_hidden,
        "hide": folderController.hide_hidden,
        "toggle": folderController.toggle_hidden,
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