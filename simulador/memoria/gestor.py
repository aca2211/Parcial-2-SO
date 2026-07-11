"""Gestor de memoria con particionamiento dinamico."""

from __future__ import annotations

import math

from .bloque import Bloque
from .estrategias import EstrategiaAsignacion
from .proceso import Proceso


class GestorMemoria:
    """Administra la memoria fisica como una lista de bloques contiguos.

    Soporta asignacion con First/Best/Worst Fit y liberacion de procesos.
    La 'unidad de asignacion' permite modelar fragmentacion interna: la
    memoria se reserva en multiplos de esa unidad, por lo que un proceso que
    pide 10 con unidad 4 recibe 12 (2 unidades desperdiciadas internamente).
    """

    def __init__(self, tamano_total: int, estrategia: EstrategiaAsignacion,
                 unidad: int = 1):
        if tamano_total <= 0:
            raise ValueError("El tamano total debe ser positivo.")
        if unidad <= 0:
            raise ValueError("La unidad de asignacion debe ser positiva.")
        self.tamano_total = tamano_total
        self.unidad = unidad
        self.estrategia = estrategia
        # Al inicio toda la memoria es un unico bloque libre.
        self.bloques: list[Bloque] = [Bloque(inicio=0, tamano=tamano_total)]
        self.procesos: dict[str, Proceso] = {}

    # ------------------------------------------------------------------ #
    # Operaciones principales
    # ------------------------------------------------------------------ #
    def asignar(self, proceso: Proceso) -> bool:
        """Intenta asignar memoria a un proceso. Devuelve True si tuvo exito."""
        if proceso.pid in self.procesos:
            print(f"  [!] El proceso {proceso.pid} ya existe. Se ignora.")
            return False

        # Redondeo hacia arriba al multiplo de la unidad de asignacion.
        requerido = math.ceil(proceso.tamano_solicitado / self.unidad) * self.unidad

        idx = self.estrategia.elegir_bloque(self.bloques, requerido)
        if idx is None:
            print(
                f"  [!] No hay bloque para {proceso.pid} "
                f"(requiere {requerido}). Asignacion fallida."
            )
            return False

        bloque = self.bloques[idx]
        proceso.tamano_asignado = requerido
        sobrante = bloque.tamano - requerido

        # Bloque ocupado por el proceso.
        ocupado = Bloque(
            inicio=bloque.inicio,
            tamano=requerido,
            pid=proceso.pid,
            tamano_usado=proceso.tamano_solicitado,
        )
        nuevos = [ocupado]
        # Si sobra espacio, queda como bloque libre adyacente.
        if sobrante > 0:
            nuevos.append(Bloque(inicio=bloque.inicio + requerido, tamano=sobrante))

        self.bloques[idx:idx + 1] = nuevos
        self.procesos[proceso.pid] = proceso
        print(
            f"  [OK] {proceso.pid} asignado en [{ocupado.inicio}-{ocupado.fin}) "
            f"({self.estrategia.nombre}), frag. interna={proceso.fragmentacion_interna}"
        )
        return True

    def liberar(self, pid: str) -> bool:
        """Libera la memoria ocupada por un proceso y fusiona huecos."""
        if pid not in self.procesos:
            print(f"  [!] No existe el proceso {pid}. Nada que liberar.")
            return False
        for bloque in self.bloques:
            if bloque.pid == pid:
                bloque.pid = None
                bloque.tamano_usado = 0
        del self.procesos[pid]
        self._fusionar_libres()
        print(f"  [OK] Memoria del proceso {pid} liberada.")
        return True

    def _fusionar_libres(self) -> None:
        """Une bloques libres contiguos (coalescing) para reducir huecos."""
        fusionados: list[Bloque] = []
        for bloque in self.bloques:
            if fusionados and fusionados[-1].libre and bloque.libre:
                fusionados[-1].tamano += bloque.tamano
            else:
                fusionados.append(bloque)
        self.bloques = fusionados

    # ------------------------------------------------------------------ #
    # Metricas
    # ------------------------------------------------------------------ #
    def bloques_libres(self) -> list[Bloque]:
        return [b for b in self.bloques if b.libre]

    def bloques_ocupados(self) -> list[Bloque]:
        return [b for b in self.bloques if not b.libre]

    def memoria_libre_total(self) -> int:
        return sum(b.tamano for b in self.bloques_libres())

    def memoria_ocupada_total(self) -> int:
        return sum(b.tamano for b in self.bloques_ocupados())

    def fragmentacion_externa(self) -> int:
        """Memoria libre que NO esta en el hueco libre mas grande.

        Representa el espacio libre que no podria satisfacer una peticion del
        tamano del total libre por estar disperso en varios huecos.
        """
        libres = self.bloques_libres()
        if not libres:
            return 0
        mayor = max(b.tamano for b in libres)
        return self.memoria_libre_total() - mayor

    def fragmentacion_interna(self) -> int:
        """Suma del espacio desperdiciado dentro de los bloques ocupados."""
        return sum(b.fragmentacion_interna for b in self.bloques_ocupados())
