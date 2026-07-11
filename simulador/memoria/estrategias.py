"""Estrategias de asignacion de memoria (patron Strategy).

Cada estrategia recibe la lista de bloques y el tamano requerido, y devuelve
el indice del bloque libre elegido, o None si no hay ninguno adecuado.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .bloque import Bloque


class EstrategiaAsignacion(ABC):
    """Interfaz comun para las estrategias de asignacion."""

    nombre: str = "Generica"

    @abstractmethod
    def elegir_bloque(self, bloques: list[Bloque], requerido: int) -> int | None:
        """Devuelve el indice del bloque a usar o None si no cabe."""
        raise NotImplementedError


class FirstFit(EstrategiaAsignacion):
    """Primer bloque libre donde quepa el proceso."""

    nombre = "First Fit"

    def elegir_bloque(self, bloques: list[Bloque], requerido: int) -> int | None:
        for i, bloque in enumerate(bloques):
            if bloque.libre and bloque.tamano >= requerido:
                return i
        return None


class BestFit(EstrategiaAsignacion):
    """Bloque libre mas pequeno donde quepa (minimiza el sobrante)."""

    nombre = "Best Fit"

    def elegir_bloque(self, bloques: list[Bloque], requerido: int) -> int | None:
        mejor_idx = None
        mejor_tam = None
        for i, bloque in enumerate(bloques):
            if bloque.libre and bloque.tamano >= requerido:
                if mejor_tam is None or bloque.tamano < mejor_tam:
                    mejor_tam = bloque.tamano
                    mejor_idx = i
        return mejor_idx


class WorstFit(EstrategiaAsignacion):
    """Bloque libre mas grande donde quepa (maximiza el sobrante)."""

    nombre = "Worst Fit"

    def elegir_bloque(self, bloques: list[Bloque], requerido: int) -> int | None:
        peor_idx = None
        peor_tam = None
        for i, bloque in enumerate(bloques):
            if bloque.libre and bloque.tamano >= requerido:
                if peor_tam is None or bloque.tamano > peor_tam:
                    peor_tam = bloque.tamano
                    peor_idx = i
        return peor_idx


ESTRATEGIAS: dict[str, type[EstrategiaAsignacion]] = {
    "FIRST_FIT": FirstFit,
    "BEST_FIT": BestFit,
    "WORST_FIT": WorstFit,
}


def crear_estrategia(clave: str) -> EstrategiaAsignacion:
    """Fabrica una estrategia a partir de su clave textual."""
    clave = clave.strip().upper()
    if clave not in ESTRATEGIAS:
        raise ValueError(
            f"Estrategia desconocida '{clave}'. "
            f"Opciones: {', '.join(ESTRATEGIAS)}"
        )
    return ESTRATEGIAS[clave]()
