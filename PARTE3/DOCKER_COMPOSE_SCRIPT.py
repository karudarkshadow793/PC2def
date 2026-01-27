#!/usr/bin/env python3
"""
Script para probar microservicios

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
    print("1. Limpiando contenedores viejos...")
    run("sudo docker-compose -f docker-compose.micro.yml down")

def construir():
    """Construye todas las imágenes"""
    print("2. Construyendo imágenes...")
    
    print("   Compilando reviews...")
    run('sudo docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build')
    servicios = [
        ("productpage", "cdps-productpage:g29"),
        ("details", "cdps-details:g29"),
        ("ratings", "cdps-ratings:g29"),
    ]
    
    for carpeta, tag in servicios:
        print(f"   Construyendo {carpeta}...")
        run(f"sudo docker build -t {tag} ./{carpeta}")
    for v in ["v1", "v2", "v3"]:
        print(f"   Construyendo reviews {v}...")
        run(f"sudo docker build --build-arg SERVICE_VERSION={v} -t cdps-reviews:{v}-g29 ./reviews")

def probar(version):

    limpiar()
    print(f"3. Iniciando versión {version}...")
    run(f"sudo REVIEWS_VERSION={version} docker-compose -f docker-compose.micro.yml up -d")
    time.sleep(5)
    print("5. Contenedores corriendo:")
    run("sudo docker ps --format 'table {{.Names}}\t{{.Status}}' | grep cdps")
    print(f"Abre: http://localhost:9080")
    print(f"   Versión: {version}")

    input("\nPresiona ENTER para pasar a siguiente versión...")

limpiar()

def main():

    if not os.path.exists("docker-compose.micro.yml"):
        print("ERROR: No encuentro docker-compose.micro.yaml")
        sys.exit(1)
    
    print("Opciones:")
    print("1. Construir todo (primera vez)")
    print("2. Probar las 3 versiones")
    print("3. Solo v1")
    print("4. Solo v2")
    print("5. Solo v3")
    print("6. Limpiar todo")
    print("0. Salir")
    
    op = input("Elige: ").strip()
    
    if op == "1":
        construir()
        print("Todo construido!")
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
        print("Todo limpiado!")
    else:
        print("Adiós!")