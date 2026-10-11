from services.windows_service import windowsService


class PlatformHandler:
    def get_platform_service(self):
        import platform
        system = platform.system()
        if system == "Windows":
            return windowsService
        else:
            raise NotImplementedError(f"Platform not supported: {system}")


platform_handler = PlatformHandler()