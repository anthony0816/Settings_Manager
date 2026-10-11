import re
import subprocess
import sys

from controllers.platform_handler import platform_handler
from modules.logger.logger import log
from services.screen_service import ScreenService


DEFAULT_SECONDS = 3 * 60
MAX_SECONDS = 24 * 60 * 60

NEVER_ALIASES = ("never", "unlimited", "infinite", "nunca", "ilimitado", "inf")

UNIT_SECONDS = {
    "s": 1, "seg": 1, "segundo": 1, "segundos": 1,
    "m": 60, "min": 60, "minuto": 60, "minutos": 60,
    "h": 3600, "hora": 3600, "horas": 3600,
}

TIME_RE = re.compile(r"(\d+)\s*([a-z]*)")

OFFSCREEN = "offscreen"
SLEEP = "sleep"

STATE_MAP = {
    "plug": "ac",
    "ac": "ac",
    "enchufado": "ac",
    "unplug": "dc",
    "dc": "dc",
    "bateria": "dc",
    "both": "both",
    "ambos": "both",
}

ACTION_MAP = {
    "offscreen": OFFSCREEN,
    "off": OFFSCREEN,
    "apagar": OFFSCREEN,
    "screen": OFFSCREEN,
    "sleep": SLEEP,
    "dormir": SLEEP,
    "suspender": SLEEP,
}

ACTIONS = (OFFSCREEN, SLEEP)

STATE_LABEL = {
    "ac": "con cargador",
    "dc": "con bateria",
    "both": "con cargador y con bateria",
}

ACTION_LABEL = {
    OFFSCREEN: "apagar la pantalla",
    SLEEP: "dormir",
}

USAGE = """Uso: wst screen <comando> [args...]

Comandos:
  plug   <accion> <tiempo>   Con cargador
  unplug <accion> <tiempo>   Con bateria
  both   <accion> <tiempo>   Con cargador y con bateria
  default                     3 min para los 4 tiempos
  status                     Muestra los tiempos (no modifica nada)

Acciones:
  offscreen   Apagar la pantalla
  sleep       Dormir / suspender

Tiempos:
  3 | 5 | 10         Minutos (sin unidad = minutos)
  30s | 5m | 2h      Con unidad: segundos, minutos u horas
  never | unlimited | infinite | nunca
                    Nunca

Ejemplos:
  wst screen both offscreen 5
  wst screen plug sleep 20
  wst screen unplug offscreen never
  wst screen both sleep never
  wst screen default"""


def parse_time(raw: str):
    """Convierte el texto de tiempo a segundos. Retorna None si es invalido."""
    text = raw.strip().lower()

    if text in NEVER_ALIASES:
        return 0

    match = TIME_RE.fullmatch(text)
    if not match:
        return None

    number, unit = match.groups()
    number = int(number)

    if not unit:
        # Sin unidad se asume minutos, pero 0 es ambiguo.
        if number == 0:
            return None
        seconds = number * 60
    else:
        if unit not in UNIT_SECONDS:
            return None
        seconds = number * UNIT_SECONDS[unit]

    if seconds <= 0 or seconds > MAX_SECONDS:
        return None

    return seconds


def format_time(seconds) -> str:
    if seconds is None:
        return "desconocido"
    if seconds == 0:
        return "nunca"
    if seconds % 3600 == 0:
        return f"{seconds // 3600} h"
    if seconds % 60 == 0:
        return f"{seconds // 60} min"
    return f"{seconds} s"


class ScreenController:
    def __init__(self, service_factory):
        self._service_factory = service_factory

    def _service(self) -> ScreenService:
        return ScreenService(self._service_factory())

    def set_timeout(self, args):
        if len(args) != 3:
            log.error("Uso: wst screen {plug|unplug|both} <offscreen|sleep> <tiempo>")
            log.info(USAGE)
            sys.exit(1)

        state_arg, action_arg, raw_time = args[0].lower(), args[1].lower(), args[2]

        if state_arg not in STATE_MAP:
            log.error(f"Estado no valido: '{args[0]}'. Use: plug, unplug, both.")
            log.info(USAGE)
            sys.exit(1)

        if action_arg not in ACTION_MAP:
            log.error(f"Accion no valida: '{args[1]}'. Use: offscreen, sleep.")
            log.info(USAGE)
            sys.exit(1)

        seconds = parse_time(raw_time)
        if seconds is None:
            log.error(f"Tiempo no valido: '{raw_time}'")
            log.info(USAGE)
            sys.exit(1)

        action = ACTION_MAP[action_arg]
        state = STATE_MAP[state_arg]
        self._service().set_timeout(state, seconds, action)

        if seconds == 0:
            detalle = "nunca"
        else:
            detalle = format_time(seconds)

        log.success(
            f"{ACTION_LABEL[action]} {STATE_LABEL[state]}: {detalle}"
        )

    def set_default(self, args):
        if args:
            log.error("El comando 'default' no acepta argumentos")
            log.info(USAGE)
            sys.exit(1)

        service = self._service()
        for action in ACTIONS:
            service.set_timeout("both", DEFAULT_SECONDS, action)

        log.success(
            f"Default {DEFAULT_SECONDS // 60} min para apagar la pantalla y dormir, "
            f"con cargador y con bateria"
        )

    def show_status(self, args):
        if args:
            log.error("El comando 'status' no acepta argumentos")
            log.info(USAGE)
            sys.exit(1)

        service = self._service()
        valores = {}
        for action in ACTIONS:
            for state in ("ac", "dc"):
                valores[(action, state)] = service.get_timeout(state, action)

        if all(v is None for v in valores.values()):
            log.error("No se pudo leer la configuracion de energia de Windows.")
            log.info("Verifica que el plan de energia sea Balanced o Ultimate.")
            sys.exit(1)

        for action in ACTIONS:
            log.info(f"{ACTION_LABEL[action].capitalize()}:")
            for state in ("ac", "dc"):
                log.info(f"   {STATE_LABEL[state]}: {format_time(valores[(action, state)])}")


screenController = ScreenController(platform_handler.get_platform_service)


def handle_screen(args):
    if not args:
        log.error("Uso: wst screen <comando> [args...]")
        log.info(USAGE)
        sys.exit(1)

    command = args[0].lower()
    args = args[1:]

    try:
        if command == "default":
            screenController.set_default(args)
        elif command == "status":
            screenController.show_status(args)
        elif command in STATE_MAP:
            screenController.set_timeout([command, *args])
        else:
            log.error(f"Comando no soportado: '{command}'")
            log.info(USAGE)
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        detalle = (e.stderr or "").strip() or f"powercfg termino con codigo {e.returncode}"
        log.error(f"Windows rechazo el cambio de energia: {detalle}")
        sys.exit(1)
    except (OSError, ValueError) as e:
        log.error(f"No se pudo completar la operacion: {e}")
        sys.exit(1)