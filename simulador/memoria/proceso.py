"""Modelo de un proceso que solicita memoria."""


class Proceso:
    """Representa un proceso que solicita un bloque de memoria.

    Attributes:
        pid: Identificador unico del proceso (por ejemplo "P1").
        tamano_solicitado: Memoria pedida por el proceso (en unidades logicas).
        tamano_asignado: Memoria realmente reservada (puede ser mayor por
            redondeo a la unidad de asignacion -> fragmentacion interna).
    """

    def __init__(self, pid: str, tamano_solicitado: int):
        if tamano_solicitado <= 0:
            raise ValueError("El tamano solicitado debe ser positivo.")
        self.pid = pid
        self.tamano_solicitado = tamano_solicitado
        self.tamano_asignado = 0

    @property
    def fragmentacion_interna(self) -> int:
        """Memoria desperdiciada dentro del bloque asignado."""
        return max(0, self.tamano_asignado - self.tamano_solicitado)

    def __repr__(self) -> str:
        return (
            f"Proceso(pid={self.pid}, solicitado={self.tamano_solicitado}, "
            f"asignado={self.tamano_asignado})"
        )
