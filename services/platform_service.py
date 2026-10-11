from abc import ABC, abstractmethod
from typing import Optional


class PlatformService(ABC):
    @abstractmethod
    def set_lid_close_action(self, state: str, action_value: int) -> None:
        pass

    @abstractmethod
    def set_mouse_speed(self, speed: int) -> None:
        pass
    
    @abstractmethod
    def switch_hidden_folders(self, value=None) -> None:
        pass

    @abstractmethod
    def get_hidden_folders_status(self) -> bool:
        pass

    @abstractmethod
    def set_screen_timeout(self, state: str, seconds: int) -> None:
        pass

    @abstractmethod
    def get_screen_timeout(self, state: str) -> Optional[int]:
        pass

    @abstractmethod
    def set_sleep_timeout(self, state: str, seconds: int) -> None:
        pass

    @abstractmethod
    def get_sleep_timeout(self, state: str) -> Optional[int]:
        pass