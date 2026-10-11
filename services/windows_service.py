import re
import subprocess
import ctypes
import winreg
from typing import Optional

from services.platform_service import PlatformService


LID_CLOSE_ACTION_GUID = "5ca83367-6e45-459f-a27b-476b1d01c936"
SUB_BUTTONS = "SUB_BUTTONS"
SCHEME_CURRENT = "SCHEME_CURRENT"

SUB_SLEEP = "SUB_SLEEP"
STANDBYIDLE = "STANDBYIDLE"
SUB_VIDEO = "SUB_VIDEO"
VIDEOIDLE = "VIDEOIDLE"

# Cada ajuste de powercfg necesita su subgrupo + su setting. VIDEOIDLE y
# STANDBYIDLE solos no son validos, por eso van siempre juntos.
POWER_SETTINGS = {
    "offscreen": (SUB_VIDEO, VIDEOIDLE),
    "sleep": (SUB_SLEEP, STANDBYIDLE),
}

# Ajusta los valores hexadecimales que imprime powercfg (Minimum/Maximum/increment
# y los Current). No se usan los nombres de las lineas porque powercfg los traduce
# segun el idioma del sistema.
CURRENT_INDEX_RE = re.compile(r":\s*(0x[0-9a-fA-F]+)\s*$", re.MULTILINE)

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
    def _powercfg(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["powercfg", *args], check=True, capture_output=True, text=True
        )

    def set_lid_close_action(self, state: str, action_value: int) -> None:
        if state in ("ac", "both"):
            self._powercfg("/setacvalueindex", SCHEME_CURRENT, SUB_BUTTONS,
                           LID_CLOSE_ACTION_GUID, str(action_value))
        if state in ("dc", "both"):
            self._powercfg("/setdcvalueindex", SCHEME_CURRENT, SUB_BUTTONS,
                           LID_CLOSE_ACTION_GUID, str(action_value))
        self._powercfg("/setactive", SCHEME_CURRENT)

    def set_screen_timeout(self, state: str, seconds: int) -> None:
        """Define cuando se apaga la pantalla sola."""
        self._set_power_timeout(state, seconds, "offscreen")

    def set_sleep_timeout(self, state: str, seconds: int) -> None:
        """Define cuando el equipo entra en suspension solo."""
        self._set_power_timeout(state, seconds, "sleep")

    def get_screen_timeout(self, state: str) -> Optional[int]:
        """Segundos para apagar la pantalla, o None si no se pudo leer."""
        return self._get_power_timeout(state, "offscreen")

    def get_sleep_timeout(self, state: str) -> Optional[int]:
        """Segundos para dormir, o None si no se pudo leer."""
        return self._get_power_timeout(state, "sleep")

    def _set_power_timeout(self, state: str, seconds: int, action: str) -> None:
        """
        Args:
            state: 'ac' (con cargador), 'dc' (con bateria) o 'both'
            seconds: segundos de espera. 0 = nunca
            action: 'offscreen' o 'sleep'
        """
        if seconds < 0:
            raise ValueError(f"Segundos invalidos: {seconds}. Use 0 para nunca.")

        subgroup, setting = POWER_SETTINGS[action]

        if state in ("ac", "both"):
            self._powercfg("/setacvalueindex", SCHEME_CURRENT, subgroup, setting, str(seconds))
        if state in ("dc", "both"):
            self._powercfg("/setdcvalueindex", SCHEME_CURRENT, subgroup, setting, str(seconds))
        self._powercfg("/setactive", SCHEME_CURRENT)

    def _get_power_timeout(self, state: str, action: str) -> Optional[int]:
        """
        Retorna los segundos configurados, o None si no se pudo leer.
        Acepta 'ac' o 'dc'.
        """
        if state not in ("ac", "dc"):
            return None

        subgroup, setting = POWER_SETTINGS[action]
        result = self._powercfg("/query", SCHEME_CURRENT, subgroup, setting)
        indices = [int(value, 16) for value in CURRENT_INDEX_RE.findall(result.stdout)]

        # El query tambien imprime Minimum/Maximum/increment en hexadecimal, y
        # siempre antes de los valores actuales. Los dos ultimos son AC y DC.
        if len(indices) < 2:
            return None

        ac, dc = indices[-2], indices[-1]
        return ac if state == "ac" else dc

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