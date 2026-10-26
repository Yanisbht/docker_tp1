import os
import re
from fastapi import FastAPI, HTTPException, status
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Admin API Docker",
    version="1.0.0"
)

DOCKER_URL = os.getenv("DOCKER_API_URL", "http://127.0.0.1:2375")

# Constraints from the requirements
ALLOWED_IMAGES = ["nginx:alpine", "redis:alpine", "httpd:alpine"]
NAME_REGEX = re.compile(r"^[a-z][a-z0-9-]{1,30}$")


# --- READ ROUTES ---

@app.get("/health", summary="Vérification de l'état de l'API")
def health_check():
    return {"status": "ok"}

@app.get("/containers", summary="Lister les conteneurs gérés")
def list_containers():
    try:
        filters = '{"label":["adminapi.managed=true"]}'
        response = requests.get(f"{DOCKER_URL}/containers/json", params={"filters": filters}, timeout=3)
        response.raise_for_status()
        raw_containers = response.json()
        
        containers = []
        for c in raw_containers:
            containers.append({
                "id": c.get("Id"),
                "name": c.get("Names", [""])[0].lstrip("/"),
                "image": c.get("Image"),
                "state": c.get("State")
            })
        return containers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/containers/{id}", summary="Afficher un conteneur géré par son ID")
def get_container(id: str):
    try:
        response = requests.get(f"{DOCKER_URL}/containers/{id}/json", timeout=3)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Conteneur inconnu")
        response.raise_for_status()
        c = response.json()
        
        labels = c.get("Config", {}).get("Labels") or {}
        if labels.get("adminapi.managed") != "true":
            raise HTTPException(status_code=404, detail="Conteneur non géré (label absent)")
            
        return {
            "id": c.get("Id"),
            "name": c.get("Name", "").lstrip("/"),
            "image": c.get("Config", {}).get("Image"),
            "state": c.get("State", {}).get("Status")
        }
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")


# --- WRITE ROUTES ---

@app.post("/containers", status_code=status.HTTP_201_CREATED, summary="Créer et démarrer un conteneur géré")
def create_container(payload: dict):
    name = payload.get("name")
    image = payload.get("image")

    # Validation du nom (regex : ^[a-z][a-z0-9-]{1,30}$)
    if not name or not NAME_REGEX.match(name):
        raise HTTPException(status_code=422, detail="Nom invalide (doit respecter ^[a-z][a-z0-9-]{1,30}$)")
    
    # Validation de l'image (allowlist)
    if image not in ALLOWED_IMAGES:
        raise HTTPException(status_code=422, detail=f"Image non autorisée. Choisissez parmi : {ALLOWED_IMAGES}")

    # Vérification de l'existence préalable du nom
    try:
        check_res = requests.get(f"{DOCKER_URL}/containers/json?all=1", timeout=3)
        if check_res.status_code == 200:
            for c in check_res.json():
                names = [n.lstrip("/") for n in c.get("Names", [])]
                if name in names:
                    raise HTTPException(status_code=409, detail="Le nom du conteneur est déjà pris")
    except requests.exceptions.RequestException:
        pass

    # Création du conteneur avec l'étiquette adminapi.managed=true
    container_config = {
        "Image": image,
        "Labels": {"adminapi.managed": "true"}
    }
    
    try:
        create_res = requests.post(f"{DOCKER_URL}/containers/create", params={"name": name}, json=container_config, timeout=5)
        if create_res.status_code == 409:
            raise HTTPException(status_code=409, detail="Conflit : ce nom existe déjà")
        create_res.raise_for_status()
        container_id = create_res.json().get("Id")

        # Démarrage immédiat
        start_res = requests.post(f"{DOCKER_URL}/containers/{container_id}/start", timeout=5)
        start_res.raise_for_status()

        return {
            "id": container_id,
            "name": name,
            "image": image,
            "state": "running"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/containers/{id}/stop", summary="Arrêter un conteneur géré")
def stop_container(id: str):
    try:
        inspect_res = requests.get(f"{DOCKER_URL}/containers/{id}/json", timeout=3)
        if inspect_res.status_code == 404:
            raise HTTPException(status_code=404, detail="Conteneur inconnu")
        
        c_data = inspect_res.json()
        labels = c_data.get("Config", {}).get("Labels") or {}
        if labels.get("adminapi.managed") != "true":
            raise HTTPException(status_code=404, detail="Conteneur non géré")

        state = c_data.get("State", {})
        if not state.get("Running", False):
            raise HTTPException(status_code=409, detail="Le conteneur est déjà arrêté")

        stop_res = requests.post(f"{DOCKER_URL}/containers/{id}/stop", timeout=5)
        stop_res.raise_for_status()

        return {
            "id": c_data.get("Id"),
            "name": c_data.get("Name", "").lstrip("/"),
            "image": c_data.get("Config", {}).get("Image"),
            "state": "exited"
        }
    except HTTPException:
        raise
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")

@app.post("/containers/{id}/start", summary="Démarrer un conteneur géré")
def start_container(id: str):
    try:
        inspect_res = requests.get(f"{DOCKER_URL}/containers/{id}/json", timeout=3)
        if inspect_res.status_code == 404:
            raise HTTPException(status_code=404, detail="Conteneur inconnu")
        
        c_data = inspect_res.json()
        labels = c_data.get("Config", {}).get("Labels") or {}
        if labels.get("adminapi.managed") != "true":
            raise HTTPException(status_code=404, detail="Conteneur non géré")

        state = c_data.get("State", {})
        if state.get("Running", False):
            raise HTTPException(status_code=409, detail="Le conteneur tourne déjà")

        start_res = requests.post(f"{DOCKER_URL}/containers/{id}/start", timeout=5)
        start_res.raise_for_status()

        return {
            "id": c_data.get("Id"),
            "name": c_data.get("Name", "").lstrip("/"),
            "image": c_data.get("Config", {}).get("Image"),
            "state": "running"
        }
    except HTTPException:
        raise
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")

@app.delete("/containers/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer un conteneur géré")
def delete_container(id: str):
    try:
        inspect_res = requests.get(f"{DOCKER_URL}/containers/{id}/json", timeout=3)
        if inspect_res.status_code == 404:
            raise HTTPException(status_code=404, detail="Conteneur inconnu")
        
        c_data = inspect_res.json()
        labels = c_data.get("Config", {}).get("Labels") or {}
        if labels.get("adminapi.managed") != "true":
            raise HTTPException(status_code=404, detail="Conteneur non géré")

        del_res = requests.delete(f"{DOCKER_URL}/containers/{id}", params={"force": "true"}, timeout=5)
        del_res.raise_for_status()
        return
    except HTTPException:
        raise
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")