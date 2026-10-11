from services.platform_service import PlatformService


class FolderService:
    """Fachada de dominio para la visibilidad de carpetas ocultas.

    Recibe la implementacion de plataforma por inyeccion para no depender
    de un sistema operativo concreto.
    """

    def __init__(self, platform_service: PlatformService):
        self._platform_service = platform_service

    def switch_hidden_status(self, value=None) -> None:
        self._platform_service.switch_hidden_folders(value)

    def get_status(self) -> bool:
        return self._platform_service.get_hidden_folders_status()