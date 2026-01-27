#!/bin/bash
# Entrypoint script para procesar variables de entorno en tiempo de ejecución

# Reemplazar variables en el HTML ANTES de ejecutar la aplicación
if [ -f /app/templates/productpage.html ]; then
    # Crear copia temporal
    cp /app/templates/productpage.html /app/templates/productpage.html.template
    
    # Reemplazar variables
    sed -i "s|<title>.*</title>|<title>Grupo ${TEAM_ID} - BookInfo - ${APP_OWNER}</title>|" /app/templates/productpage.html
fi

# Ejecutar el comando original
exec "$@"
