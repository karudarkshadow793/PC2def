#!/usr/bin/env python

import subprocess, os, sys

if len(sys.argv) < 2:
    print("Usage: python script_1.py [build|run]")
    sys.exit(1)

cmd = sys.argv[1].lower()

if cmd == "build":
    subprocess.run("sudo apt update", shell=True)
    subprocess.run("sudo apt install software-properties-common", shell=True)
    subprocess.run("sudo add-apt-repository -y ppa:deadsnakes/ppa", shell=True)
    subprocess.run("sudo apt install -y python3.9 python3.9-venv python3.9-distutils", shell=True)
    
    # Navegar al directorio de productpage
    os.chdir("bookinfo/src/productpage/")

    # Crear entorno virtual y instalar dependencias
    subprocess.run("python3.9 -m venv venv", shell=True)
    subprocess.run("./venv/bin/pip install -r requirements.txt", shell=True)

    # Establecer variable de entorno TEAM_ID para el grupo 29
    os.environ['TEAM_ID'] = '29'
    print("Build completado. TEAM_ID establecido a '29'")
    
elif cmd == "run":
    # Cambiar al directorio y ejecutar en puerto 9090 como indica el enunciado
    os.chdir("bookinfo/src/productpage/")
    
    # Usar el puerto 9090 mencionado en el enunciado
    # También podemos usar otro puerto
    port = "6050"  
    
    # Ejecutar con la variable de entorno TEAM_ID=29
    subprocess.run(f"TEAM_ID=29 ./venv/bin/python3.9 productpage_monolith.py {port}", shell=True)
    
else:
    print("Invalid command. Use: build or run")
    sys.exit(1)