"""Simulador de traduccion de direcciones virtuales a fisicas (paginacion)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResultadoTraduccion:
    """Resultado del proceso de traduccion de una direccion virtual."""

    direccion_virtual: int
    numero_pagina: int
    desplazamiento: int
    numero_marco: int | None
    direccion_fisica: int | None
    exito: bool
    mensaje: str


class MMU:
    """Unidad de Manejo de Memoria con paginacion de un nivel.

    Traduce direcciones virtuales a fisicas usando una tabla de paginas.
    direccion_fisica = numero_marco * tam_pagina + desplazamiento
    """

    def __init__(self, tam_memoria_virtual: int, tam_memoria_fisica: int,
                 tam_pagina: int):
        if tam_pagina <= 0:
            raise ValueError("El tamano de pagina debe ser positivo.")
        if tam_memoria_virtual <= 0 or tam_memoria_fisica <= 0:
            raise ValueError("Los tamanos de memoria deben ser positivos.")
        self.tam_memoria_virtual = tam_memoria_virtual
        self.tam_memoria_fisica = tam_memoria_fisica
        self.tam_pagina = tam_pagina
        self.num_paginas = tam_memoria_virtual // tam_pagina
        self.num_marcos = tam_memoria_fisica // tam_pagina
        # tabla_paginas[pagina] = marco (o None si no esta mapeada).
        self.tabla_paginas: dict[int, int] = {}

    def mapear(self, pagina: int, marco: int) -> None:
        """Registra la asociacion pagina -> marco en la tabla de paginas."""
        if not 0 <= pagina < self.num_paginas:
            raise ValueError(
                f"Pagina {pagina} fuera de rango (0..{self.num_paginas - 1})."
            )
        if not 0 <= marco < self.num_marcos:
            raise ValueError(
                f"Marco {marco} fuera de rango (0..{self.num_marcos - 1})."
            )
        self.tabla_paginas[pagina] = marco

    def marcos_ocupados(self) -> set[int]:
        return set(self.tabla_paginas.values())

    def marcos_disponibles(self) -> list[int]:
        ocupados = self.marcos_ocupados()
        return [m for m in range(self.num_marcos) if m not in ocupados]

    def traducir(self, direccion_virtual: int) -> ResultadoTraduccion:
        """Traduce una direccion virtual a fisica."""
        numero_pagina = direccion_virtual // self.tam_pagina
        desplazamiento = direccion_virtual % self.tam_pagina

        if not 0 <= direccion_virtual < self.tam_memoria_virtual:
            return ResultadoTraduccion(
                direccion_virtual, numero_pagina, desplazamiento, None, None,
                False, "Direccion virtual fuera del espacio de direcciones.",
            )

        if numero_pagina not in self.tabla_paginas:
            return ResultadoTraduccion(
                direccion_virtual, numero_pagina, desplazamiento, None, None,
                False, f"Fallo de pagina: la pagina {numero_pagina} no esta "
                       f"mapeada a ningun marco.",
            )

        marco = self.tabla_paginas[numero_pagina]
        direccion_fisica = marco * self.tam_pagina + desplazamiento
        return ResultadoTraduccion(
            direccion_virtual, numero_pagina, desplazamiento, marco,
            direccion_fisica, True,
            f"pagina {numero_pagina} -> marco {marco}",
        )
