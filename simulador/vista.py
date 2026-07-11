"""Funciones de presentacion para la interfaz de terminal.

Se usan codigos ANSI para color y caracteres de caja para dibujar la memoria.
"""

from __future__ import annotations

import os

from .memoria.gestor import GestorMemoria
from .traduccion.paginacion import MMU, ResultadoTraduccion

# ---------------------------------------------------------------------- #
# Utilidades de estilo
# ---------------------------------------------------------------------- #
RESET = "\033[0m"
BOLD = "\033[1m"
VERDE = "\033[92m"
ROJO = "\033[91m"
AZUL = "\033[94m"
AMARILLO = "\033[93m"
CIAN = "\033[96m"
GRIS = "\033[90m"

ANCHO = 60


def limpiar() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def titulo(texto: str) -> None:
    linea = "=" * ANCHO
    print(f"{BOLD}{CIAN}{linea}{RESET}")
    print(f"{BOLD}{CIAN}{texto.center(ANCHO)}{RESET}")
    print(f"{BOLD}{CIAN}{linea}{RESET}")


def subtitulo(texto: str) -> None:
    print(f"\n{BOLD}{AMARILLO}--- {texto} ---{RESET}")


def barra_memoria(gestor: GestorMemoria, ancho: int = ANCHO) -> None:
    """Dibuja una barra proporcional del uso de la memoria."""
    total = gestor.tamano_total
    print()
    for bloque in gestor.bloques:
        # Cantidad de celdas proporcional al tamano del bloque (minimo 1).
        celdas = max(1, round(bloque.tamano / total * ancho))
        if bloque.libre:
            color, etiqueta = GRIS, "libre"
        else:
            color, etiqueta = VERDE, str(bloque.pid)
        barra = color + "#" * celdas + RESET
        print(
            f"  [{bloque.inicio:>6}-{bloque.fin:>6}) {barra} "
            f"{etiqueta} ({bloque.tamano})"
        )


def mostrar_estado_memoria(gestor: GestorMemoria) -> None:
    subtitulo("Estado de la memoria")
    barra_memoria(gestor)

    subtitulo("Bloques ocupados")
    ocupados = gestor.bloques_ocupados()
    if not ocupados:
        print(f"  {GRIS}(ninguno){RESET}")
    for b in ocupados:
        print(
            f"  {VERDE}{b.pid}{RESET}: [{b.inicio}-{b.fin}) tam={b.tamano} "
            f"usado={b.tamano_usado} frag.interna={b.fragmentacion_interna}"
        )

    subtitulo("Bloques libres")
    libres = gestor.bloques_libres()
    if not libres:
        print(f"  {GRIS}(ninguno){RESET}")
    for b in libres:
        print(f"  {GRIS}hueco{RESET}: [{b.inicio}-{b.fin}) tam={b.tamano}")

    subtitulo("Metricas")
    print(f"  Memoria total .............. {gestor.tamano_total}")
    print(f"  Memoria ocupada ............ {gestor.memoria_ocupada_total()}")
    print(f"  Memoria libre .............. {gestor.memoria_libre_total()}")
    print(f"  {ROJO}Fragmentacion externa .....{RESET} "
          f"{gestor.fragmentacion_externa()}")
    print(f"  {ROJO}Fragmentacion interna .....{RESET} "
          f"{gestor.fragmentacion_interna()}")


def mostrar_config_mmu(mmu: MMU) -> None:
    subtitulo("Configuracion de la MMU (paginacion de un nivel)")
    print(f"  Memoria virtual ............ {mmu.tam_memoria_virtual} "
          f"({mmu.num_paginas} paginas)")
    print(f"  Memoria fisica ............. {mmu.tam_memoria_fisica} "
          f"({mmu.num_marcos} marcos)")
    print(f"  Tamano de pagina/marco ..... {mmu.tam_pagina}")

    subtitulo("Tabla de paginas")
    print(f"  {BOLD}{'Pagina':>8} | {'Marco':>6}{RESET}")
    for pagina in sorted(mmu.tabla_paginas):
        print(f"  {pagina:>8} | {mmu.tabla_paginas[pagina]:>6}")

    disponibles = mmu.marcos_disponibles()
    subtitulo("Marcos disponibles")
    if disponibles:
        print("  " + ", ".join(str(m) for m in disponibles))
    else:
        print(f"  {GRIS}(ninguno){RESET}")


def mostrar_traduccion(res: ResultadoTraduccion) -> None:
    if res.exito:
        print(
            f"  {VERDE}VA {res.direccion_virtual}{RESET} = "
            f"(pagina {res.numero_pagina}, offset {res.desplazamiento}) "
            f"-> marco {res.numero_marco} => "
            f"{BOLD}PA {res.direccion_fisica}{RESET}"
        )
    else:
        print(
            f"  {ROJO}VA {res.direccion_virtual}{RESET} = "
            f"(pagina {res.numero_pagina}, offset {res.desplazamiento}) "
            f"-> {ROJO}{res.mensaje}{RESET}"
        )
