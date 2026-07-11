"""Modelo de un bloque (particion) de memoria."""

from __future__ import annotations


class Bloque:
    """Representa una particion contigua de memoria.

    Un bloque puede estar libre u ocupado por un proceso. La memoria completa
    se modela como una lista ordenada de bloques adyacentes.

    Attributes:
        inicio: Direccion base del bloque.
        tamano: Tamano total del bloque en unidades logicas.
        pid: Identificador del proceso que lo ocupa, o None si esta libre.
        tamano_usado: Cantidad realmente solicitada por el proceso. Permite
            calcular la fragmentacion interna (tamano - tamano_usado).
    """

    def __init__(self, inicio: int, tamano: int, pid: str | None = None,
                 tamano_usado: int = 0):
        self.inicio = inicio
        self.tamano = tamano
        self.pid = pid
        self.tamano_usado = tamano_usado

    @property
    def libre(self) -> bool:
        return self.pid is None

    @property
    def fin(self) -> int:
        """Ultima direccion (exclusiva) del bloque."""
        return self.inicio + self.tamano

    @property
    def fragmentacion_interna(self) -> int:
        if self.libre:
            return 0
        return max(0, self.tamano - self.tamano_usado)

    def __repr__(self) -> str:
        estado = "LIBRE" if self.libre else f"OCUPADO({self.pid})"
        return f"Bloque[{self.inicio}-{self.fin}) {estado} tam={self.tamano}"
