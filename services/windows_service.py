import subprocess
import ctypes
from services.platform_service import PlatformService


LID_CLOSE_ACTION_GUID = "5ca83367-6e45-459f-a27b-476b1d01c936"
SUB_BUTTONS = "SUB_BUTTONS"
SCHEME_CURRENT = "SCHEME_CURRENT"

SPI_SETMOUSESPEED = 0x0071
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


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