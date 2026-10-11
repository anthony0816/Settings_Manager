from abc import ABC, abstractmethod


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