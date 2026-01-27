#!/usr/bin/env python3
"""
Script para probar microservicios
"""

import os
import time
import subprocess
import sys

def check_docker_compose():
    """Verifica si docker-compose está instalado"""
    try:
        result = subprocess.run("docker-compose --version", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"docker-compose: {result.stdout.strip()}")
            return True
        else:
            print("docker-compose no encontrado")
            return False
    except:
        return False

def install_docker_compose_linux():
    """Instala docker-compose en Linux (simplificado)"""
    print("Instalando docker-compose...")
    
    # Opción 1: Usar apt (recomendado para Ubuntu/Debian)
    print("Intentando con apt...")
    result = subprocess.run("sudo apt update && sudo apt install -y docker-compose", 
                          shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("docker-compose instalado con apt")
        return True
    
    # Opción 2: Descargar binario directamente
    print("Descargando binario...")
    commands = [
        "sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose",
        "sudo chmod +x /usr/local/bin/docker-compose",
        "docker-compose --version"
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
    
    print("docker-compose instalado")
    return True

def run(cmd):
    """Ejecuta un comando"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
    
    return result

def limpiar():
    """Limpia contenedores"""
    print("Limpiando contenedores...")
    if os.path.exists("docker-compose.micro.yml"):
        run("docker-compose -f docker-compose.micro.yml down")
    else:
        print("Archivo docker-compose.micro.yml no encontrado")

def build():
    """Construye todas las imágenes"""
    print("Construyendo imágenes...")
    
    # Construir servicios básicos
    servicios = [
        ("productpage", "cdps-productpage:g29"),
        ("details", "cdps-details:g29"),
        ("ratings", "cdps-ratings:g29"),
    ]
    
    for carpeta, tag in servicios:
        if os.path.exists(f"./{carpeta}/Dockerfile"):
            print(f"Construyendo {carpeta}...")
            run(f"docker build -t {tag} ./{carpeta}")
    
    # Construir reviews
    for v in ["v1", "v2", "v3"]:
        print(f"Construyendo reviews {v}...")
        run(f"docker build --build-arg SERVICE_VERSION={v} -t cdps-reviews:{v}-g29 ./reviews")

def probar(version):
    """Prueba una versión específica"""
    if not os.path.exists("docker-compose.micro.yml"):
        print("ERROR: No encuentro docker-compose.micro.yml")
        return
    
    limpiar()
    print(f"Iniciando versión {version}...")
    
    result = run(f"REVIEWS_VERSION={version} docker-compose -f docker-compose.micro.yml up -d")
    
    if result.returncode == 0:
        time.sleep(3)
        print("Contenedores corriendo:")
        run("docker ps --format 'table {{.Names}}\t{{.Status}}' | grep cdps")
        print(f"\nURL: http://localhost:9080/productpage (versión {version})")
        input("\nPresiona ENTER para continuar...")

def main():
    """Función principal"""
    print("Script de prueba de microservicios - Grupo 29")
    print("=" * 50)
    
    # Verificar docker-compose
    if not check_docker_compose():
        print("\nDocker-compose no está instalado.")
        respuesta = input("¿Quieres instalarlo automáticamente? (s/n): ").lower()
        
        if respuesta == 's':
            # Detectar sistema
            import platform
            if platform.system().lower() == "linux":
                if install_docker_compose_linux():
                    print("docker-compose instalado correctamente")
                else:
                    print("No se pudo instalar docker-compose")
                    print("Instala manualmente: sudo apt install docker-compose")
                    return
            else:
                print("Para Windows/Mac: instala Docker Desktop")
                return
        else:
            print("Instala docker-compose manualmente y vuelve a ejecutar")
            return
    
    # Menú principal
    while True:
        print("\nMENU:")
        print("1. Construir todo")
        print("2. Probar v1, v2, v3")
        print("3. Limpiar")
        print("0. Salir")
        
        op = input("\nOpción: ").strip()
        
        if op == "1":
            build()
            print("Construcción completada")
            
        elif op == "2":
            for v in ["v1", "v2", "v3"]:
                probar(v)
            print("Pruebas completadas")
            
        elif op == "3":
            limpiar()
            print("Limpiado")
            
        elif op == "0":
            limpiar()
            print("Saliendo...")
            break
            
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()
