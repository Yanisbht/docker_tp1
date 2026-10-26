## 4. Écrire une API : FastAPI

<p class="lead">Jusqu'ici vous étiez le client. Vous passez de l'autre côté.</p>

FastAPI est un framework Python : vous écrivez des fonctions, il s'occupe de HTTP, du JSON,
de la validation et de la documentation.

---

## La plus petite API possible

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install fastapi uvicorn requests python-dotenv
```

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title="API d'administration de conteneurs")


@app.get("/health", summary="Vérifie que l'API répond")
def sante():
    return {"status": "ok"}        # un dict Python devient du JSON, code 200
```

```bash
uvicorn app.main:app --reload --env-file .env
```

<p class="small"><code>app.main:app</code> = fichier <code>app/main.py</code>, variable <code>app</code>. <code>--reload</code> redémarre à chaque sauvegarde. Ouvrez <a href="http://127.0.0.1:8000/docs">127.0.0.1:8000/docs</a> : la documentation existe déjà.</p>

---

## Un paramètre dans le chemin, et une erreur propre

```python
import requests
from fastapi import FastAPI, HTTPException

DOCKER = "http://127.0.0.1:2375"   # provisoire : viendra de l'environnement


@app.get("/containers/{identifiant}", summary="Détail d'un conteneur géré")
def lire(identifiant: str):
    reponse = requests.get(f"{DOCKER}/containers/{identifiant}/json", timeout=10)
    if reponse.status_code == 404:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")
    reponse.raise_for_status()
    detail = reponse.json()
    return {
        "id": detail["Id"],
        "name": detail["Name"].lstrip("/"),
        "image": detail["Config"]["Image"],
        "state": detail["State"]["Status"],
    }
```

<p class="small"><code>{identifiant}</code> dans le chemin arrive comme argument de la fonction. <code>HTTPException</code> interrompt le traitement et renvoie le code voulu, avec <code>{"detail": "…"}</code> en corps.</p>

---

## Votre API est un traducteur

<div class="left">

Elle reçoit une requête dans **votre** vocabulaire, appelle l'API Docker dans **le sien**,
et retraduit la réponse.

| Docker Engine répond | Votre API répond |
|---|---|
| `"Id": "4f1c…"` | `"id": "4f1c…"` |
| `"Names": ["/web1"]` (liste), ou `"Name": "/web1"` (détail) | `"name": "web1"` |
| `"Image": "nginx:alpine"`, ou `"Config": {"Image": …}` | `"image": "nginx:alpine"` |
| `"State": "running"`, ou `"State": {"Status": "running"}` | `"state": "running"` |

</div>

<div class="valid">
C'est tout l'intérêt d'une API d'administration sur mesure : elle expose <strong>un vocabulaire simple et stable</strong>, limité à ce que vos utilisateurs ont le droit de faire, et cache la complexité (et les incohérences) du système en dessous.
</div>

---

## Décrire ce qu'on renvoie : un modèle pydantic

```python
from pydantic import BaseModel


class Conteneur(BaseModel):
    id: str
    name: str
    image: str
    state: str


@app.get("/containers", summary="Liste les conteneurs gérés",
         response_model=list[Conteneur])
def lister():
    ...
```

<div class="left">

`response_model` fait trois choses d'un coup :

- **vérifie** que ce que vous renvoyez a bien cette forme (sinon, erreur 500 explicite) ;
- **filtre** les champs en trop : rien ne fuit par accident ;
- **documente** la forme de la réponse dans `/docs`.

</div>

<p class="small">À la prochaine demi-journée, le même mécanisme validera ce que l'API <strong>reçoit</strong>.</p>

---

## Ne voir que ses propres conteneurs

Votre machine fait tourner d'autres conteneurs (NetBox, sa base de données…). Votre API ne doit
ni les montrer, ni permettre de les arrêter.

```python
import json

ETIQUETTE = "adminapi.managed=true"

filtres = json.dumps({"label": [ETIQUETTE]})
reponse = requests.get(
    f"{DOCKER}/containers/json",
    params={"all": "true", "filters": filtres},
    timeout=10,
)
```

<div class="left">

- La **liste** filtre par label, côté Docker.
- Le **détail** vérifie le label dans `detail["Config"]["Labels"]` : s'il manque, **404**.

</div>

<p class="small">Pour avoir un conteneur à lister : <code>docker run -d --name web1 --label adminapi.managed=true nginx:alpine</code></p>

---

## Livrer : le Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /srv

# Les dépendances d'abord : cette couche reste en cache tant que requirements.txt ne change pas.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

<div class="memo">

**`--host 0.0.0.0` est obligatoire dans un conteneur** : par défaut uvicorn n'écoute que sur
`127.0.0.1`, c'est-à-dire l'intérieur du conteneur, et personne ne peut le joindre.

Dans le réseau de compose, Docker et NetBox se joignent par leur **nom de service**
(`http://docker-api:2375`, `http://netbox:8080`), pas par `127.0.0.1`. D'où l'importance de
lire ces adresses dans des **variables d'environnement**.

</div>
