# Imagen ligera de Python para el simulador de administracion de memoria.
FROM python:3.12-slim

# Evita que Python genere archivos .pyc y usa salida sin buffer (util en TTY).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TERM=xterm-256color

WORKDIR /app

# El proyecto solo usa la libreria estandar, no hay dependencias externas.
COPY simulador/ ./simulador/
COPY entradas/ ./entradas/
COPY main.py ./

# Ejecuta la interfaz de terminal interactiva.
# Se debe correr con: docker run -it <imagen>
CMD ["python3", "main.py"]
