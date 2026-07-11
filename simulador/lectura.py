"""Lectura y parseo de los archivos de entrada de ambos simuladores.

Formato memoria (asignacion):
    MEMORIA <tamano_total>
    UNIDAD <tamano_unidad>          # opcional (por defecto 1)
    ESTRATEGIA <FIRST_FIT|BEST_FIT|WORST_FIT>
    CREAR <pid> <tamano>
    LIBERAR <pid>
    # las lineas que empiezan con '#' o vacias se ignoran

Formato traduccion (paginacion):
    MEMORIA_VIRTUAL <tamano>
    MEMORIA_FISICA <tamano>
    TAM_PAGINA <tamano>
    TABLA <pagina> <marco>
    TRADUCIR <direccion_virtual>
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConfiguracionMemoria:
    tamano_total: int = 0
    unidad: int = 1
    estrategia: str = "FIRST_FIT"
    # Lista de operaciones: ("CREAR", pid, tam) o ("LIBERAR", pid, None)
    operaciones: list[tuple[str, str, int | None]] = field(default_factory=list)


@dataclass
class ConfiguracionTraduccion:
    memoria_virtual: int = 0
    memoria_fisica: int = 0
    tam_pagina: int = 0
    tabla: list[tuple[int, int]] = field(default_factory=list)
    direcciones: list[int] = field(default_factory=list)


def _lineas_utiles(ruta: str):
    with open(ruta, "r", encoding="utf-8") as archivo:
        for numero, cruda in enumerate(archivo, start=1):
            linea = cruda.strip()
            if not linea or linea.startswith("#"):
                continue
            yield numero, linea


def leer_config_memoria(ruta: str) -> ConfiguracionMemoria:
    cfg = ConfiguracionMemoria()
    for numero, linea in _lineas_utiles(ruta):
        partes = linea.split()
        clave = partes[0].upper()
        try:
            if clave == "MEMORIA":
                cfg.tamano_total = int(partes[1])
            elif clave == "UNIDAD":
                cfg.unidad = int(partes[1])
            elif clave == "ESTRATEGIA":
                cfg.estrategia = partes[1].upper()
            elif clave == "CREAR":
                cfg.operaciones.append(("CREAR", partes[1], int(partes[2])))
            elif clave == "LIBERAR":
                cfg.operaciones.append(("LIBERAR", partes[1], None))
            else:
                print(f"  [!] Linea {numero} ignorada (clave '{clave}').")
        except (IndexError, ValueError) as err:
            raise ValueError(f"Error en linea {numero}: '{linea}' ({err})")
    if cfg.tamano_total <= 0:
        raise ValueError("El archivo no define un tamano de MEMORIA valido.")
    return cfg


def leer_config_traduccion(ruta: str) -> ConfiguracionTraduccion:
    cfg = ConfiguracionTraduccion()
    for numero, linea in _lineas_utiles(ruta):
        partes = linea.split()
        clave = partes[0].upper()
        try:
            if clave == "MEMORIA_VIRTUAL":
                cfg.memoria_virtual = int(partes[1])
            elif clave == "MEMORIA_FISICA":
                cfg.memoria_fisica = int(partes[1])
            elif clave == "TAM_PAGINA":
                cfg.tam_pagina = int(partes[1])
            elif clave == "TABLA":
                cfg.tabla.append((int(partes[1]), int(partes[2])))
            elif clave == "TRADUCIR":
                cfg.direcciones.append(int(partes[1]))
            else:
                print(f"  [!] Linea {numero} ignorada (clave '{clave}').")
        except (IndexError, ValueError) as err:
            raise ValueError(f"Error en linea {numero}: '{linea}' ({err})")
    if cfg.tam_pagina <= 0:
        raise ValueError("El archivo no define un TAM_PAGINA valido.")
    return cfg
