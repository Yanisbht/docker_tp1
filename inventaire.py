import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement
load_dotenv()

DOCKER_URL = os.getenv("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX_URL = os.getenv("NETBOX_URL", "http://localhost:8080")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN", "")

def main():
    session = requests.Session()
    
    try:
        response = session.get(f"{DOCKER_URL}/containers/json", timeout=3)
        response.raise_for_status()
        containers = response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERREUR] Impossible de joindre l'API Docker : {e}", file=sys.stderr)
        sys.exit(1) 

    inventaire_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "containers": [],
        "netbox": {}
    }

    
    for c in containers:
        c_id = c.get("Id")
        c_name = c.get("Names", ["unknown"])[0].lstrip("/")
        c_image = c.get("Image")
        c_state = c.get("State")

        container_info = {
            "id": c_id,
            "name": c_name,
            "image": c_image,
            "state": c_state,
            "cpu_percent": 0.0,
            "memory_mb": 0.0
        }

        if c_state == "running":
            try:
                stats_res = session.get(f"{DOCKER_URL}/containers/{c_id}/stats?stream=false", timeout=3)
                if stats_res.status_code == 200:
                    stats = stats_res.json()
                    
                    cpu_stats = stats.get("cpu_stats", {})
                    prec_cpu_stats = stats.get("precpu_stats", {})
                    
                    cpu_delta = cpu_stats.get("cpu_usage", {}).get("total_usage", 0) - prec_cpu_stats.get("cpu_usage", {}).get("total_usage", 0)
                    system_delta = cpu_stats.get("system_cpu_usage", 0) - prec_cpu_stats.get("system_cpu_usage", 0)
                    online_cpus = cpu_stats.get("online_cpus", len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", [1])))

                    if system_delta > 0 and cpu_delta > 0:
                        container_info["cpu_percent"] = round((cpu_delta / system_delta) * online_cpus * 100.0, 2)

                    mem_stats = stats.get("memory_stats", {})
                    mem_usage = mem_stats.get("usage", 0) - mem_stats.get("stats", {}).get("cache", 0)
                    container_info["memory_mb"] = round(mem_usage / (1024 * 1024), 2)
            except Exception:
                pass 

        inventaire_data["containers"].append(container_info)

    headers = {"Authorization": f"Token {NETBOX_TOKEN}"} if NETBOX_TOKEN else {}
    try:
        # Statut NetBox
        status_res = session.get(f"{NETBOX_URL}/api/status/", headers=headers, timeout=3)
        status_res.raise_for_status()
        netbox_version = status_res.json().get("netbox-version", "unknown")

        object_types = []
        url = f"{NETBOX_URL}/api/core/object-types/?limit=50"
        total_count = 0

        while url:
            res = session.get(url, headers=headers, timeout=3)
            res.raise_for_status()
            data = res.json()
            total_count = data.get("count", 0)
            object_types.extend(data.get("results", []))
            url = data.get("next") 

        inventaire_data["netbox"] = {
            "version": netbox_version,
            "object_types_count": len(object_types),
            "netbox_reported_count": total_count
        }

    except requests.exceptions.RequestException as e:
        print(f"[AVERTISSEMENT] Impossible de joindre NetBox : {e}", file=sys.stderr)
        inventaire_data["netbox"] = {"error": str(e)}

    import json
    with open("inventaire.json", "w", encoding="utf-8") as f:
        json.dump(inventaire_data, f, indent=2, ensure_ascii=False)


    print("=== RAPPORT D'INVENTAIRE ===")
    print(f"Date : {inventaire_data['timestamp']}")
    print(f"Conteneurs gérés/visibles : {len(inventaire_data['containers'])}")
    for c in inventaire_data['containers']:
        print(f" - [{c['state']}] {c['name']} ({c['image']}) | CPU: {c['cpu_percent']}% | RAM: {c['memory_mb']} Mo")
    print(f"NetBox Version : {inventaire_data['netbox'].get('version', 'N/A')}")
    print(f"NetBox Object Types : {inventaire_data['netbox'].get('object_types_count', 0)} (Total attendu: {inventaire_data['netbox'].get('netbox_reported_count', 0)})")

if __name__ == "__main__":
    main()