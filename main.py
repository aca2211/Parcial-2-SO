#!/usr/bin/env python3
"""Interfaz de terminal del Simulador de Administracion de Memoria.

Menu interactivo desde el cual se pueden ejecutar los dos simuladores,
cargar archivos de entrada y ver los resultados en pantalla.

Uso:
    python3 main.py
"""

from __future__ import annotations

import os
import sys

from simulador import vista
from simulador.lectura import (
    ConfiguracionMemoria,
    ConfiguracionTraduccion,
    leer_config_memoria,
    leer_config_traduccion,
)
from simulador.memoria.estrategias import crear_estrategia
from simulador.memoria.gestor import GestorMemoria
from simulador.memoria.proceso import Proceso
from simulador.traduccion.paginacion import MMU

DIR_ENTRADAS = os.path.join(os.path.dirname(__file__), "entradas")
DIR_SALIDAS = os.path.join(os.path.dirname(__file__), "salidas")


# ---------------------------------------------------------------------- #
# Helpers de entrada del usuario
# ---------------------------------------------------------------------- #
def pausar() -> None:
    input(f"\n{vista.GRIS}Presione ENTER para continuar...{vista.RESET}")


def elegir_archivo(prefijo: str) -> str | None:
    """Lista los archivos de 'entradas/' que empiezan por 'prefijo'."""
    if not os.path.isdir(DIR_ENTRADAS):
        print(f"  {vista.ROJO}No existe la carpeta 'entradas/'.{vista.RESET}")
        return None
    archivos = sorted(
        f for f in os.listdir(DIR_ENTRADAS)
        if f.startswith(prefijo) and f.endswith(".txt")
    )
    if not archivos:
        print(f"  {vista.ROJO}No hay archivos '{prefijo}*.txt'.{vista.RESET}")
        return None

    vista.subtitulo("Archivos de entrada disponibles")
    for i, nombre in enumerate(archivos, start=1):
        print(f"  {i}) {nombre}")
    print("  0) Escribir una ruta manualmente")

    opcion = input("\n  Seleccione un archivo: ").strip()
    if opcion == "0":
        ruta = input("  Ruta del archivo: ").strip()
        return ruta or None
    try:
        idx = int(opcion) - 1
        if 0 <= idx < len(archivos):
            return os.path.join(DIR_ENTRADAS, archivos[idx])
    except ValueError:
        pass
    print(f"  {vista.ROJO}Opcion invalida.{vista.RESET}")
    return None


def guardar_salida(nombre: str, lineas: list[str]) -> None:
    os.makedirs(DIR_SALIDAS, exist_ok=True)
    ruta = os.path.join(DIR_SALIDAS, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"\n  {vista.VERDE}Resultados guardados en:{vista.RESET} {ruta}")


# ---------------------------------------------------------------------- #
# Simulador 1: Asignacion de memoria
# ---------------------------------------------------------------------- #
def ejecutar_asignacion(cfg: ConfiguracionMemoria) -> GestorMemoria:
    estrategia = crear_estrategia(cfg.estrategia)
    gestor = GestorMemoria(cfg.tamano_total, estrategia, unidad=cfg.unidad)

    vista.subtitulo("Estado inicial de la memoria")
    vista.barra_memoria(gestor)

    vista.subtitulo(f"Ejecutando operaciones ({estrategia.nombre}, "
                    f"unidad={cfg.unidad})")
    for tipo, pid, tam in cfg.operaciones:
        if tipo == "CREAR":
            gestor.asignar(Proceso(pid, int(tam)))
        elif tipo == "LIBERAR":
            gestor.liberar(pid)
    return gestor


def menu_asignacion() -> None:
    vista.limpiar()
    vista.titulo("SIMULADOR 1: ASIGNACION DE MEMORIA")
    ruta = elegir_archivo("memoria")
    if not ruta:
        pausar()
        return
    try:
        cfg = leer_config_memoria(ruta)
        gestor = ejecutar_asignacion(cfg)
    except (OSError, ValueError) as err:
        print(f"\n  {vista.ROJO}Error: {err}{vista.RESET}")
        pausar()
        return

    vista.mostrar_estado_memoria(gestor)

    # Genera archivo de salida con el resumen final.
    salida = [
        f"Estrategia: {gestor.estrategia.nombre}",
        f"Memoria total: {gestor.tamano_total}",
        f"Unidad de asignacion: {gestor.unidad}",
        "",
        "Bloques ocupados:",
    ]
    for b in gestor.bloques_ocupados():
        salida.append(
            f"  {b.pid}: [{b.inicio}-{b.fin}) tam={b.tamano} "
            f"frag_interna={b.fragmentacion_interna}"
        )
    salida.append("Bloques libres:")
    for b in gestor.bloques_libres():
        salida.append(f"  hueco: [{b.inicio}-{b.fin}) tam={b.tamano}")
    salida += [
        "",
        f"Memoria ocupada: {gestor.memoria_ocupada_total()}",
        f"Memoria libre: {gestor.memoria_libre_total()}",
        f"Fragmentacion externa: {gestor.fragmentacion_externa()}",
        f"Fragmentacion interna: {gestor.fragmentacion_interna()}",
    ]
    base = os.path.splitext(os.path.basename(ruta))[0]
    guardar_salida(f"salida_{base}.txt", salida)
    pausar()


# ---------------------------------------------------------------------- #
# Simulador 2: Traduccion de direcciones
# ---------------------------------------------------------------------- #
def ejecutar_traduccion(cfg: ConfiguracionTraduccion) -> tuple[MMU, list]:
    mmu = MMU(cfg.memoria_virtual, cfg.memoria_fisica, cfg.tam_pagina)
    for pagina, marco in cfg.tabla:
        mmu.mapear(pagina, marco)

    vista.mostrar_config_mmu(mmu)

    vista.subtitulo("Traducciones")
    resultados = []
    for direccion in cfg.direcciones:
        res = mmu.traducir(direccion)
        vista.mostrar_traduccion(res)
        resultados.append(res)
    return mmu, resultados


def menu_traduccion() -> None:
    vista.limpiar()
    vista.titulo("SIMULADOR 2: TRADUCCION DE DIRECCIONES")
    ruta = elegir_archivo("paginacion")
    if not ruta:
        pausar()
        return
    try:
        cfg = leer_config_traduccion(ruta)
        mmu, resultados = ejecutar_traduccion(cfg)
    except (OSError, ValueError) as err:
        print(f"\n  {vista.ROJO}Error: {err}{vista.RESET}")
        pausar()
        return

    salida = [
        f"Memoria virtual: {mmu.tam_memoria_virtual} ({mmu.num_paginas} paginas)",
        f"Memoria fisica: {mmu.tam_memoria_fisica} ({mmu.num_marcos} marcos)",
        f"Tamano de pagina: {mmu.tam_pagina}",
        "",
        "Traducciones:",
    ]
    for res in resultados:
        if res.exito:
            salida.append(
                f"  VA {res.direccion_virtual} -> "
                f"pagina {res.numero_pagina}, offset {res.desplazamiento} -> "
                f"marco {res.numero_marco} -> PA {res.direccion_fisica}"
            )
        else:
            salida.append(
                f"  VA {res.direccion_virtual} -> ERROR: {res.mensaje}"
            )
    base = os.path.splitext(os.path.basename(ruta))[0]
    guardar_salida(f"salida_{base}.txt", salida)
    pausar()


# ---------------------------------------------------------------------- #
# Menu principal
# ---------------------------------------------------------------------- #
def menu_principal() -> None:
    while True:
        vista.limpiar()
        vista.titulo("SIMULADOR DE ADMINISTRACION DE MEMORIA")
        print(f"\n  {vista.BOLD}Sistemas Operativos - Parcial No. 2{vista.RESET}")
        print("\n  1) Simulador de asignacion de memoria "
              "(First/Best/Worst Fit)")
        print("  2) Simulador de traduccion de direcciones (paginacion)")
        print("  3) Salir")
        opcion = input("\n  Seleccione una opcion: ").strip()

        if opcion == "1":
            menu_asignacion()
        elif opcion == "2":
            menu_traduccion()
        elif opcion == "3":
            print("\n  Hasta luego!\n")
            break
        else:
            print(f"  {vista.ROJO}Opcion invalida.{vista.RESET}")
            pausar()


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n  Interrumpido por el usuario.\n")
        sys.exit(0)
