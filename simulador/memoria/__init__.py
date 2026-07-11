"""Paquete del simulador de asignacion de memoria."""

from .bloque import Bloque
from .estrategias import BestFit, FirstFit, WorstFit, crear_estrategia
from .gestor import GestorMemoria
from .proceso import Proceso

__all__ = [
    "Bloque",
    "Proceso",
    "GestorMemoria",
    "FirstFit",
    "BestFit",
    "WorstFit",
    "crear_estrategia",
]
