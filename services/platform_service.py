from abc import ABC, abstractmethod


class PlatformService(ABC):
    @abstractmethod
    def set_lid_close_action(self, state: str, action_value: int) -> None:
        pass

    @abstractmethod
    def set_mouse_speed(self, speed: int) -> None:
        pass