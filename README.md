# Simulador de Administracion de Memoria

Parcial No. 2 - Sistemas Operativos (Universidad del Valle).

Proyecto en **Python** con paradigma **orientado a objetos** e **interfaz de
terminal**. Incluye dos simuladores:

1. **Asignacion de memoria**: estrategias First Fit, Best Fit y Worst Fit, con
   creacion/liberacion de procesos, fusion de huecos libres y calculo de
   fragmentacion interna y externa.
2. **Traduccion de direcciones**: paginacion de un nivel que traduce
   direcciones virtuales a fisicas mediante una tabla de paginas.

## Requisitos

- Python 3.10+ (solo libreria estandar, sin dependencias externas), o
- Docker.

## Estructura

```
.
├── main.py                     # Interfaz de terminal (menu principal)
├── simulador/
│   ├── memoria/
│   │   ├── proceso.py          # Clase Proceso
│   │   ├── bloque.py           # Clase Bloque (particion)
│   │   ├── estrategias.py      # First/Best/Worst Fit (patron Strategy)
│   │   └── gestor.py           # GestorMemoria (logica de asignacion)
│   ├── traduccion/
│   │   └── paginacion.py       # MMU (traduccion de direcciones)
│   ├── lectura.py              # Parseo de archivos de entrada
│   └── vista.py                # Presentacion en terminal
├── entradas/                   # Archivos de entrada de ejemplo
│   ├── memoria1.txt
│   ├── memoria2.txt
│   ├── paginacion1.txt
│   └── paginacion2.txt
├── salidas/                    # Resultados generados (se crea al ejecutar)
├── informe/
│   └── informe.tex             # Informe del parcial en LaTeX
└── Dockerfile
```

## Informe (LaTeX)

El informe se encuentra en `informe/informe.tex`. Se puede compilar en
[Overleaf](https://overleaf.com) (subiendo el archivo) o localmente con una
distribucion de LaTeX:

```bash
cd informe
pdflatex informe.tex
pdflatex informe.tex   # segunda pasada para el indice
```

## Ejecucion local

```bash
python3 main.py
```

Aparece un menu; se elige el simulador y luego un archivo de la carpeta
`entradas/`. Los resultados se muestran en pantalla y se guardan en `salidas/`.

## Ejecucion con Docker

```bash
# Construir la imagen
docker build -t simulador-memoria .

# Ejecutar la interfaz interactiva (importante el flag -it)
docker run -it --rm simulador-memoria
```

Para conservar los archivos de salida generados dentro del contenedor:

```bash
docker run -it --rm -v "$(pwd)/salidas:/app/salidas" simulador-memoria
```

## Formato de los archivos de entrada

### Asignacion de memoria (`memoria*.txt`)

```
MEMORIA <tamano_total>
UNIDAD <tamano_unidad>        # opcional (por defecto 1); >1 genera frag. interna
ESTRATEGIA <FIRST_FIT|BEST_FIT|WORST_FIT>
CREAR <pid> <tamano>
LIBERAR <pid>
```

### Traduccion de direcciones (`paginacion*.txt`)

```
MEMORIA_VIRTUAL <tamano>
MEMORIA_FISICA <tamano>
TAM_PAGINA <tamano>
TABLA <pagina> <marco>
TRADUCIR <direccion_virtual>
```

Las lineas vacias y las que empiezan con `#` se ignoran.

## Conceptos modelados

- **Fragmentacion externa**: memoria libre total menos el hueco libre mas
  grande (espacio libre disperso que no se puede aprovechar en una sola
  peticion grande).
- **Fragmentacion interna**: espacio desperdiciado dentro de un bloque cuando
  la memoria se reserva en multiplos de la unidad de asignacion.
- **Traduccion por paginacion**: `direccion_fisica = marco * tam_pagina +
  desplazamiento`, con deteccion de fallo de pagina y direcciones fuera de
  rango.
