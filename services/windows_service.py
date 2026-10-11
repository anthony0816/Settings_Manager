import subprocess
import ctypes
import winreg
from services.platform_service import PlatformService


LID_CLOSE_ACTION_GUID = "5ca83367-6e45-459f-a27b-476b1d01c936"
SUB_BUTTONS = "SUB_BUTTONS"
SCHEME_CURRENT = "SCHEME_CURRENT"

SPI_SETMOUSESPEED = 0x0071
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

HIDDEN_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
HIDDEN_REG_VALUE = "Hidden"
SHOW_HIDDEN = 1
HIDE_HIDDEN = 2

HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x001A
SMTO_ABORTIFHUNG = 0x0002


class WindowsService(PlatformService):
    def set_lid_close_action(self, state: str, action_value: int) -> None:
        if state in ("ac", "both"):
            subprocess.run([
                "powercfg", "/setacvalueindex", SCHEME_CURRENT, SUB_BUTTONS,
                LID_CLOSE_ACTION_GUID, str(action_value)
            ], check=True, capture_output=True, text=True)
        if state in ("dc", "both"):
            subprocess.run([
                "powercfg", "/setdcvalueindex", SCHEME_CURRENT, SUB_BUTTONS,
                LID_CLOSE_ACTION_GUID, str(action_value)
            ], check=True, capture_output=True, text=True)
        subprocess.run(["powercfg", "/setactive", SCHEME_CURRENT], check=True, capture_output=True, text=True)

    def set_mouse_speed(self, speed: int) -> None:
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETMOUSESPEED,
            0,
            ctypes.c_int(speed),
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        if not result:
            error_code = ctypes.GetLastError()
            raise OSError(f"Error al cambiar velocidad del mouse. Código: {error_code}")

    def switch_hidden_folders(self, value=None) -> None:
        """
        Cambia la visibilidad de carpetas ocultas en el Explorador de Windows.
        
        Args:
            value: None = toggle actual, True = mostrar ocultos, False = ocultar
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, HIDDEN_REG_KEY, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                current_value, _ = winreg.QueryValueEx(key, HIDDEN_REG_VALUE)
                
                if value is None:
                    new_value = HIDE_HIDDEN if current_value == SHOW_HIDDEN else SHOW_HIDDEN
                elif value is True:
                    new_value = SHOW_HIDDEN
                elif value is False:
                    new_value = HIDE_HIDDEN
                else:
                    raise ValueError(f"Valor inválido para hidden folders: {value}. Use True, False o None.")
                
                if new_value != current_value:
                    winreg.SetValueEx(key, HIDDEN_REG_VALUE, 0, winreg.REG_DWORD, new_value)
                    self._refresh_explorer()
                    
        except FileNotFoundError:
            raise OSError("No se encontró la clave de registro para carpetas ocultas")
        except OSError as e:
            raise OSError(f"Error al acceder al registro: {e}")

    def _refresh_explorer(self) -> None:
        """Notifica a las ventanas abiertas del Explorer para que se actualicen."""
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "ShellState",
            SMTO_ABORTIFHUNG,
            5000,
            None
        )

    def get_hidden_folders_status(self) -> bool:
        """Retorna True si los archivos ocultos se muestran, False si están ocultos."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, HIDDEN_REG_KEY, 0, winreg.KEY_READ) as key:
                current_value, _ = winreg.QueryValueEx(key, HIDDEN_REG_VALUE)
                return current_value == SHOW_HIDDEN
        except FileNotFoundError:
            return False
        except OSError:
            return False


windowsService = WindowsService()