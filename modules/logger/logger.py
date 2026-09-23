#!/usr/bin/env python3
"""
Módulo de logging personalizado con colores.
"""

import sys


# Colores ANSI
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


class LogPrinter:
    """Clase para imprimir logs con formato y colores consistentes."""

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.stderr.isatty()

    def _colorize(self, text: str, color: str) -> str:
        if not self.use_colors:
            return text
        return f"{color}{text}{RESET}"

    def _format_message(self, level: str, level_color: str, message: str, panic: bool = False) -> str:
        """Formatea el mensaje según el nivel y modo panic."""
        colored_level = self._colorize(level, level_color)

        if panic:
            # En modo panic, todo en amarillo
            full_msg = f"{colored_level} - {message}"
            return self._colorize(full_msg, YELLOW)

        # Normal: solo el nivel coloreado, mensaje en color normal
        return f"{colored_level} - {message}"

    def error(self, message: str, *, panic: bool = False) -> None:
        """Imprime un mensaje de error (rojo)."""
        formatted = self._format_message("ERROR", RED, message, panic)
        print(formatted, file=sys.stderr)

    def warn(self, message: str, *, panic: bool = False) -> None:
        """Imprime un mensaje de advertencia (amarillo)."""
        formatted = self._format_message("WARNING", YELLOW, message, panic)
        print(formatted, file=sys.stderr)

    def info(self, message: str, *, panic: bool = False) -> None:
        """Imprime un mensaje informativo (azul)."""
        formatted = self._format_message("INFO", BLUE, message, panic)
        print(formatted, file=sys.stdout)

    def success(self, message: str, *, panic: bool = False) -> None:
        """Imprime un mensaje de éxito (verde)."""
        formatted = self._format_message("OK", GREEN, message, panic)
        print(formatted, file=sys.stdout)

    def debug(self, message: str, *, panic: bool = False) -> None:
        """Imprime un mensaje de debug (cyan)."""
        formatted = self._format_message("DEBUG", CYAN, message, panic)
        print(formatted, file=sys.stdout)


# Instancia global por defecto
log = LogPrinter()


def get_logger(use_colors: bool = True) -> LogPrinter:
    """Retorna una instancia de LogPrinter."""
    return LogPrinter(use_colors=use_colors)