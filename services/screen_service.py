from typing import Optional

from services.platform_service import PlatformService


OFFSCREEN = "offscreen"
SLEEP = "sleep"


class ScreenService:
    """Fachada de dominio para los tiempos de energia (apagar pantalla / dormir).

    Recibe la implementacion de plataforma por inyeccion para no depender
    de un sistema operativo concreto.
    """

    def __init__(self, platform_service: PlatformService):
        self._platform_service = platform_service

    def set_timeout(self, state: str, seconds: int, action: str = OFFSCREEN) -> None:
        if action == OFFSCREEN:
            self._platform_service.set_screen_timeout(state, seconds)
        else:
            self._platform_service.set_sleep_timeout(state, seconds)

    def get_timeout(self, state: str, action: str = OFFSCREEN) -> Optional[int]:
        if action == OFFSCREEN:
            return self._platform_service.get_screen_timeout(state)
        return self._platform_service.get_sleep_timeout(state)