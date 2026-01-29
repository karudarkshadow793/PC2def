#!/usr/bin/env python3
import subprocess
import os
import sys

COMPOSE_FILE = "docker-compose.micro.yml"

def run_shell(command, env=None, cwd=None):
    """Auxiliary function to run system commands."""
    subprocess.run(command, shell=True, env=env, cwd=cwd)

def perform_build():
    """Performs the initial setup and build of images."""
    print("--- Inciando construcción de imágenes y entorno ---")
    setup_cmds = [
        "export DEBIAN_FRONTEND=noninteractive && sudo apt-get update -y",
        "export DEBIAN_FRONTEND=noninteractive && sudo apt install -y docker.io docker-compose",
        "sudo systemctl enable docker",
        "sudo systemctl restart docker || true"
    ]
    for cmd in setup_cmds:
        run_shell(cmd)

    # Compile Java Reviews
    reviews_dir = "bookinfo/src/reviews"
    print(f"Compilando reviews en: {reviews_dir}")
    build_reviews_cmd = f"sudo docker run --rm -u root -v {os.getcwd()}/{reviews_dir}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build"
    run_shell(build_reviews_cmd)

    # Build Compose images
    run_shell(f"sudo docker-compose -f {COMPOSE_FILE} build")

def launch_app(version_tag):
    """Starts the application with a specific version of reviews."""
    version_map = {
        "1": "v1", "v1": "v1",
        "2": "v2", "v2": "v2",
        "3": "v3", "v3": "v3"
    }
    
    target_version = version_map.get(version_tag.lower())
    if not target_version:
        print(f"Error: Versión '{version_tag}' no válida. Use v1, v2 o v3.")
        sys.exit(1)

    print(f"--- Desplegando versión: {target_version} ---")
    
    # Configure variables
    ctx_env = os.environ.copy()
    ctx_env["REVIEWS_APP_VERSION"] = target_version
    
    if target_version == "v1":
        ctx_env["REVIEWS_ENABLE_RATINGS"] = "false"
        ctx_env["REVIEWS_STAR_COLOR"] = ""
    else:
        ctx_env["REVIEWS_ENABLE_RATINGS"] = "true"
        ctx_env["REVIEWS_STAR_COLOR"] = "black" if target_version == "v2" else "red"

    run_shell(f"sudo docker-compose -f {COMPOSE_FILE} down")
    run_shell(f"sudo -E docker-compose -f {COMPOSE_FILE} up -d", env=ctx_env)

def main():
    if len(sys.argv) < 2:
        print("Uso: python script_3.py [build|run [v1|v2|v3]|stop|debug|delete]")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "build":
        perform_build()
    elif action == "run":
        v_arg = sys.argv[2] if len(sys.argv) >= 3 else "v1"
        launch_app(v_arg)
    elif action == "stop":
        run_shell(f"sudo docker-compose -f {COMPOSE_FILE} down")
    elif action == "debug":
        run_shell(f"sudo docker-compose -f {COMPOSE_FILE} up")
    elif action == "delete":
        run_shell(f"sudo docker-compose -f {COMPOSE_FILE} down --rmi all")
    else:
        print(f"Acción '{action}' no reconocida.")
        sys.exit(1)

if __name__ == "__main__":
    main()

