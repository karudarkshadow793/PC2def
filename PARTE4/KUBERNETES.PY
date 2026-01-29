import subprocess
import os
import sys
import time
import yaml as pyyaml

class BookinfoClusterManager:
    def __init__(self):
        # Configuration
        self.DOCKER_USER = "karudarkshadow793"
        self.TAG = "latest"
        self.TEAM_ID = "29"
        self.NAMESPACE = f"cdps-{self.TEAM_ID}"
        self.PROJECT = "perfect-obelisk-480209-b2"
        self.ZONE = "europe-southwest1-b"
        self.CLUSTER = "bookinfo-cluster"
        self.NODES = 3
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.KUBE_YAMLS = os.path.join(self.BASE_DIR, "bookinfo", "platform", "kube")

    def execute(self, cmd, **kwargs):
        """Helper to run shell commands."""
        return subprocess.run(cmd, shell=True, check=True, **kwargs)

    def login_services(self):
        """Ensures gcloud and docker are authenticated."""
        try:
            self.execute("gcloud auth print-access-token", capture_output=True)
        except subprocess.CalledProcessError:
            print("(!) Iniciando login manual de gcloud...")
            self.execute("gcloud auth login")

        try:
            self.execute("docker login", capture_output=True)
        except subprocess.CalledProcessError:
            print("(!) Iniciando login manual de Docker...")
            self.execute("docker login")

    def create_cluster(self):
        """Provisioning the GKE cluster."""
        print(f"--- Creando Cluster GKE: {self.CLUSTER} ---")
        self.execute(f"gcloud config set project {self.PROJECT}")
        self.execute(f"gcloud config set compute/zone {self.ZONE}")
        self.execute(f"gcloud container clusters create {self.CLUSTER} --num-nodes={self.NODES} --no-enable-autoscaling")
        self.execute(f"gcloud container clusters get-credentials {self.CLUSTER}")

    def build_and_push(self):
        """Image building and registry push."""
        services = {
            "details": "Dockerfile.details",
            "productpage": "Dockerfile.productpage",
            "ratings": "Dockerfile.ratings"
        }
        
        for name, dfile in services.items():
            img_name = f"{self.DOCKER_USER}/{name}:{self.TAG}"
            print(f"Building: {img_name}")
            self.execute(f"docker build -t {img_name} -f {dfile} .", cwd=self.BASE_DIR)
            self.execute(f"docker push {img_name}")

        # Reviews special build
        rev_path = os.path.join(self.BASE_DIR, "bookinfo", "src", "reviews")
        print("Compilando Reviews (Gradle)...")
        self.execute(f'docker run --rm -u root -v "{rev_path}":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build')
        
        rev_dfile_dir = os.path.join(rev_path, "reviews-wlpcfg")
        for v in ["v1", "v2", "v3"]:
            rev_img = f"{self.DOCKER_USER}/reviews-{v}:{self.TAG}"
            print(f"Building Reviews {v}: {rev_img}")
            self.execute(f"docker build -t {rev_img} -f Dockerfile .", cwd=rev_dfile_dir)
            self.execute(f"docker push {rev_img}")

    def deploy_app(self, rev_version="v1"):
        """Deploying workloads to K8s."""
        print(f"--- Desplegando app (Reviews {rev_version}) en namespace {self.NAMESPACE} ---")
        
        # Cleanup old reviews
        selectors = ["app=reviews"]
        for sel in selectors:
            for res in ["pods", "svc", "deployment"]:
                self.execute(f"kubectl delete {res} -l {sel} -n {self.NAMESPACE} --ignore-not-found=true")

        manifests = [
            "cdps-namespace.yaml", "details.yaml", "productpage.yaml", 
            "ratings.yaml", "reviews-svc.yaml", f"reviews-{rev_version}-deployment.yaml"
        ]
        
        for m in manifests:
            path = os.path.join(self.KUBE_YAMLS, m)
            self.execute(f"kubectl apply -f {path}")

        self._wait_for_ip()

    def _wait_for_ip(self):
        """Internal helper to wait for external service IP."""
        svc_name = "productpage-service"
        print("Buscando IP externa...")
        for i in range(60):
            res = subprocess.run(f"kubectl get svc {svc_name} -n {self.NAMESPACE} -o yaml", 
                                 shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                data = pyyaml.safe_load(res.stdout)
                ingress = data.get('status', {}).get('loadBalancer', {}).get('ingress', [])
                if ingress and 'ip' in ingress[0]:
                    print(f"\n[OK] Accede aquí: http://{ingress[0]['ip']}:9080/")
                    return
            time.sleep(5)
        print("(!) Tiempo agotado esperando la IP externa.")

    def delete_all(self):
        """Full cleanup."""
        self.execute(f"gcloud container clusters delete {self.CLUSTER} --zone {self.ZONE} --quiet")

    def stop_namespace(self):
        """Namespace only cleanup."""
        self.execute(f"kubectl delete namespace {self.NAMESPACE} --ignore-not-found=true")

def main():
    manager = BookinfoClusterManager()
    
    if len(sys.argv) < 2:
        print("Modo de uso: python KUBERNETES.PY [create|build|run|delete|stop] [v1|v2|v3]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"

    # Always ensure sessions
    if cmd in ["create", "build", "run"]:
        manager.login_services()

    actions = {
        "create": lambda: manager.create_cluster(),
        "build":  lambda: manager.build_and_push(),
        "run":    lambda: manager.deploy_app(ver),
        "delete": lambda: manager.delete_all(),
        "stop":   lambda: manager.stop_namespace()
    }

    if cmd in actions:
        actions[cmd]()
    else:
        print(f"Error: Comando '{cmd}' desconocido.")

if __name__ == "__main__":
    main()
