
# Utilizar Python como base
FROM python:3.14-slim

# Crear la carpeta de trabajo
WORKDIR /proyecto

# Instalar herramientas necesarias para algunas librerías
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar la lista de dependencias
COPY requirements-docker.txt .

# Instalar las librerías del proyecto
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copiar el código del proyecto
COPY . .

# El inicio de los servicios se configura en Docker Compose
