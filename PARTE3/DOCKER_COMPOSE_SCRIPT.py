#!/usr/bin/env python3
import subprocess
import os
import sys
import time

def construir():
    print("Construyendo todo...")
    print("-" * 40)
    
    print("1. Instalando Docker...")
    subprocess.run("sudo apt-get update -y", shell=True)
    subprocess.run("sudo apt install -y docker.io docker-compose", shell=True)
    subprocess.run("sudo systemctl enable docker", shell=True)
    subprocess.run("sudo systemctl restart docker", shell=True)
    
    print("\n2. Construyendo reviews...")
    os.chdir("bookinfo/src/reviews")
    pwd = os.getcwd()
    subprocess.run(
        f"docker run --rm -u root -v {pwd}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build", 
        shell=True
    )
    os.chdir("../../..")
    
    print("\n3. Construyendo imagenes Docker...")
    subprocess.run("docker-compose -f docker-compose.micro.yml build", shell=True)
    
    print("\nConstruccion completada")

def ejecutar(version):
    print(f"Ejecutando version: {version}")
    print("-" * 40)
    
    env = os.environ.copy()
    if version == "v1":
        env["REVIEWS_APP_VERSION"] = "v1"
        env["REVIEWS_ENABLE_RATINGS"] = "false"
        env["TEAM_ID"] = "29"
    elif version == "v2":
        env["REVIEWS_APP_VERSION"] = "v2"
        env["REVIEWS_ENABLE_RATINGS"] = "true"
        env["REVIEWS_STAR_COLOR"] = "black"
        env["TEAM_ID"] = "29"
    elif version == "v3":
        env["REVIEWS_APP_VERSION"] = "v3"
        env["REVIEWS_ENABLE_RATINGS"] = "true"
        env["REVIEWS_STAR_COLOR"] = "red"
        env["TEAM_ID"] = "29"
    
    print("Deteniendo servicios previos...")
    subprocess.run("docker-compose -f docker-compose.micro.yml down", shell=True)
    
    print("Iniciando servicios...")
    subprocess.run(f"REVIEWS_VERSION={version} docker-compose -f docker-compose.micro.yml up -d", 
                   shell=True, env=env)
    
    time.sleep(3)
    
    print("\nContenedores en ejecucion:")
    subprocess.run("docker-compose -f docker-compose.micro.yml ps", shell=True)
    
    print(f"\nURL: http://localhost:9080/productpage")
    print(f"Version: {version} | Grupo: 29")

def detener():
    print("Deteniendo servicios...")
    subprocess.run("docker-compose -f docker-compose.micro.yml down", shell=True)
    print("Servicios detenidos")

def debug():
    print("Modo debug - Mostrando logs")
    print("Presiona Ctrl+C para salir")
    subprocess.run("docker-compose -f docker-compose.micro.yml up", shell=True)

def eliminar():
    print("Eliminando todo...")
    subprocess.run("docker-compose -f docker-compose.micro.yml down --rmi all", shell=True)
    print("Eliminacion completada")

def ver_estado():
    print("Estado actual:")
    print("-" * 40)
    
    print("Imagenes disponibles:")
    subprocess.run("docker images | grep cdps", shell=True)
    
    print("\nContenedores en ejecucion:")
    subprocess.run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", shell=True)
    
    if os.path.exists("docker-compose.micro.yml"):
        print("\nServicios docker-compose:")
        subprocess.run("docker-compose -f docker-compose.micro.yml ps", shell=True)

def mostrar_menu():
    print("\n" + "="*50)
    print("PRACTICA CDPS - GRUPO 29")
    print("="*50)
    print("\n1. Construir todo")
    print("2. Ejecutar version v1")
    print("3. Ejecutar version v2")
    print("4. Ejecutar version v3")
    print("5. Detener servicios")
    print("6. Debug (ver logs)")
    print("7. Eliminar todo")
    print("8. Ver estado")
    print("0. Salir")
    print("-"*50)
    
    return input("Seleccion (0-8): ").strip()

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        
        if cmd == "build":
            construir()
        elif cmd == "run":
            version = sys.argv[2] if len(sys.argv) > 2 else "v1"
            if version not in ["v1", "v2", "v3"]:
                print("Version no valida. Usar: v1, v2 o v3")
                sys.exit(1)
            ejecutar(version)
        elif cmd == "stop":
            detener()
        elif cmd == "debug":
            debug()
        elif cmd == "delete":
            eliminar()
        else:
            print("Comando no valido")
            print("Uso: build, run [v1|v2|v3], stop, debug, delete")
            sys.exit(1)
    else:
        while True:
            opcion = mostrar_menu()
            
            if opcion == "1":
                construir()
            elif opcion == "2":
                ejecutar("v1")
            elif opcion == "3":
                ejecutar("v2")
            elif opcion == "4":
                ejecutar("v3")
            elif opcion == "5":
                detener()
            elif opcion == "6":
                debug()
            elif opcion == "7":
                eliminar()
            elif opcion == "8":
                ver_estado()
            elif opcion == "0":
                print("Saliendo...")
                break
            else:
                print("Opcion no valida")
            
            if opcion != "0":
                input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido")
        sys.exit(0)
