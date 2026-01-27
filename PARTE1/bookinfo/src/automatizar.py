#!/usr/bin/env python3
"""
Script SIMPLE para probar microservicios
Ejecuta: python3 test-app.py
"""

import os
import time
import subprocess
import sys

def run(cmd):
    """Ejecuta un comando"""
    print(f"$ {cmd}")
    subprocess.run(cmd, shell=True)

def limpiar():
    """Limpia contenedores"""
    print("\n1. Limpiando contenedores viejos...")
    run("docker-compose -f docker-compose.micro.yml down")

def construir():
    """Construye todas las imágenes"""
    print("\n2. Construyendo imágenes...")
    
    # Compilar reviews
    print("\n   Compilando reviews...")
    run('cd reviews && docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build')
    
    # Construir imágenes
    servicios = [
        ("productpage", "cdps-productpage:g29"),
        ("details", "cdps-details:g29"),
        ("ratings", "cdps-ratings:g29"),
    ]
    
    for carpeta, tag in servicios:
        print(f"\n   Construyendo {carpeta}...")
        run(f"docker build -t {tag} ./{carpeta}")
    
    # 3 versiones de reviews
    for v in ["v1", "v2", "v3"]:
        print(f"\n   Construyendo reviews {v}...")
        run(f"docker build --build-arg SERVICE_VERSION={v} -t cdps-reviews:{v}-g29 ./reviews")

def probar(version):
   
    # Limpiar
    limpiar()
    
    # Iniciar con versión específica
    print(f"\n3. Iniciando versión {version}...")
    run(f"REVIEWS_VERSION={version} docker-compose -f docker-compose.micro.yml up -d")
    
    # Esperar
    time.sleep(5)
    
    # Mostrar contenedores
    print("\n5. Contenedores corriendo:")
    run("docker ps --format 'table {{.Names}}\t{{.Status}}' | grep cdps")
    
    print(f"\nListo! Abre: http://localhost:9080")
    print(f"   Versión: {version}")
    
    input("\nPresiona ENTER para pasar a siguiente versión...")
    
    # Limpiar para siguiente
    limpiar()

def main():

    # Verificar docker-compose
    if not os.path.exists("docker-compose.micro.yml"):
        print("ERROR: No encuentro docker-compose.micro.yml")
        sys.exit(1)
    
    print("\nOpciones:")
    print("1. Construir todo (primera vez)")
    print("2. Probar las 3 versiones")
    print("3. Solo v1")
    print("4. Solo v2")
    print("5. Solo v3")
    print("6. Limpiar todo")
    print("0. Salir")
    
    op = input("\nElige: ").strip()
    
    if op == "1":
        construir()
        print("\Todo construido!")
    elif op == "2":
        for v in ["v1", "v2", "v3"]:
            probar(v)
    elif op == "3":
        probar("v1")
    elif op == "4":
        probar("v2")
    elif op == "5":
        probar("v3")
    elif op == "6":
        limpiar()
        print("\nTodo limpiado!")
    else:
        print("\ Adiós!")

if __name__ == "__main__":
    main()