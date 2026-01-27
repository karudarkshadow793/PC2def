FROM python:3.9-slim

# Instalar dependencias del sistema si son necesarias
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     curl     && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de la aplicación
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip &&     pip install --no-cache-dir -r requirements.txt

# Variables de entorno (valores por defecto)
ENV TEAM_ID=29
ENV APP_OWNER=Ingelmo-et-al

# Exponer puerto
EXPOSE 8080

# Crear script de entrypoint que procesa variables en tiempo de ejecución
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Usar entrypoint para procesar variables
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "productpage_monolith.py", "8080"]
