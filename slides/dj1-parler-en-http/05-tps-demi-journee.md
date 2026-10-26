## Les TP de la demi-journée

<p class="lead">À partir de maintenant, vous êtes en autonomie.</p>

<div class="left">

| | | |
|---|---|---|
| **TP1** | ~45′ | Mise en route : explorer l'API Docker et NetBox à la main |
| **TP2** | ~1h15 | Inventaire : un script Python robuste |
| **TP3** | ~1h30 | Le squelette de votre API, en lecture seule |

</div>

**Appelez-moi tôt** plutôt que de rester bloqué vingt minutes.

<p class="small">Le contrat complet du projet : <code>projet/sujet.html</code>. Lisez-le une fois en entier avant le TP3.</p>

---

## Mise en place : 10 minutes

```bash
mkdir adminapi && cd adminapi
git init

# Copiez ici le contenu du dossier projet/ de l'archive :
# docker-compose.yml, verifier.py, contrat-openapi.yaml, .env.example, surveillant.py, sujet.html,
# AGENTS.md et CLAUDE.md (règles pour les assistants IA)

cp .env.example .env
printf '.env\n.venv/\n__pycache__/\ninventaire.json\n' > .gitignore

docker compose up -d
docker pull nginx:alpine && docker pull redis:alpine && docker pull httpd:alpine
docker compose ps
```

<div class="memo">

**NetBox met 2 à 5 minutes à démarrer la première fois.** Il est prêt quand `docker compose ps`
affiche `healthy` et que <http://127.0.0.1:8080> montre la page de connexion (`admin` / `admin`).
Commencez le TP1 par l'API Docker en attendant.

**Le `.gitignore` avant le premier commit**, pas après : un secret commité une fois reste dans
l'historique pour toujours.

</div>

---

## TP1 : Mise en route <span class="small">(~45′)</span>

**Objectif** : parler aux deux API à la main, avant d'écrire une ligne de Python.

<div class="left">

1. Lancez deux conteneurs, l'un étiqueté, l'autre non :
   `docker run -d --name web1 --label adminapi.managed=true nginx:alpine`
   `docker run -d --name intrus nginx:alpine`
2. Avec **cURL**, sur l'API Docker : lisez la version, listez tous les conteneurs, puis
   seulement ceux qui portent le label, lisez le détail de `web1`.
3. Arrêtez `web1` par l'API, **deux fois de suite**. Demandez un conteneur qui n'existe pas.
   Notez les trois codes de statut.
4. Dans NetBox : ouvrez l'interface et la documentation Swagger, obtenez un **token** par
   l'API, rangez-le dans `.env`.
5. Par l'API NetBox, créez un **type de cluster** `Docker`, puis un **cluster** `docker-local`.
6. Créez votre dépôt **GitHub**, premier commit, `push`, et **transmettez l'URL**.

</div>

<div class="valid">
✅ <strong>Validation</strong> : un fichier <code>tp1-exploration.md</code> commité, avec vos commandes cURL
et le code obtenu pour chacune. Le cluster <code>docker-local</code> est visible dans NetBox. URL du dépôt transmise.
</div>

--

## TP1 : mémo API Docker

<div class="memo">

```bash
D=http://127.0.0.1:2375

curl -s $D/version
curl -s "$D/containers/json?all=true"
curl -s --get $D/containers/json --data-urlencode 'all=true' \
     --data-urlencode 'filters={"label":["adminapi.managed=true"]}'
curl -s $D/containers/web1/json

curl -i -X POST $D/containers/web1/stop
curl -i -X POST $D/containers/web1/start
```

Mettre en forme le JSON : ajoutez `| python -m json.tool` (ou `| jq`).

N'afficher que le code : `-s -o /dev/null -w "%{http_code}\n"`.

Sous Windows : **Git Bash**, pas PowerShell.

</div>

--

## TP1 : mémo API NetBox

<div class="memo">

```bash
N=http://127.0.0.1:8080/api

# 1. Un token : dans la réponse, relevez "key" et "token"
curl -s -X POST $N/users/tokens/provision/ \
     -H "Content-Type: application/json" -H "Accept: application/json" \
     -d '{"username": "admin", "password": "admin"}'

# 2. Le token complet s'écrit nbt_<key>.<token>
export NETBOX_TOKEN="nbt_xxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
A="Authorization: Bearer $NETBOX_TOKEN"

# 3. Créer le type de cluster : relevez son "id" dans la réponse
curl -s -X POST $N/virtualization/cluster-types/ -H "$A" \
     -H "Content-Type: application/json" -H "Accept: application/json" \
     -d '{"name": "Docker", "slug": "docker"}'

# 4. Créer le cluster, en remplaçant 1 par l'id obtenu
curl -s -X POST $N/virtualization/clusters/ -H "$A" \
     -H "Content-Type: application/json" -H "Accept: application/json" \
     -d '{"name": "docker-local", "type": 1}'
```

Documentation interactive : <http://127.0.0.1:8080/api/schema/swagger-ui/>

</div>

--

## TP1 : le dépôt GitHub

<div class="memo">

```bash
git add -A
git status                 # vérifiez que .env n'apparaît PAS dans la liste
git commit -m "Met en place l'environnement du projet"

git branch -M main
git remote add origin https://github.com/<votre-compte>/adminapi.git
git push -u origin main
```

Dépôt **public**, ou privé en m'invitant comme collaborateur.

**L'historique compte.** Un commit par étape qui fonctionne, avec un message qui dit ce que
vous avez fait : « Ajoute la liste des conteneurs », pas « wip » ni « modifs ».

</div>

---

## TP2 : Inventaire <span class="small">(~1h15)</span>

**Objectif** : un script `inventaire.py` qui interroge les deux API et ne casse pas à la première panne.

<div class="left">

1. Créez un environnement virtuel, installez `requests`, notez-le dans `requirements.txt`.
2. Avec une **`Session`** et un **`timeout`**, listez **tous** les conteneurs de la machine :
   nom, image, état.
3. Pour chaque conteneur **démarré**, appelez `/containers/{id}/stats?stream=false` et
   calculez son **pourcentage de CPU** et sa **mémoire en Mo**.
4. Écrivez le tout dans `inventaire.json`, avec la date du relevé, et affichez un résumé lisible.
5. Ajoutez un relevé NetBox : sa **version** (`/api/status/`), et le **nombre de types d'objets**
   obtenu en suivant la **pagination** de `/api/core/object-types/?limit=50` jusqu'au bout.
6. Rendez-le robuste : arrêtez l'API Docker (`docker compose stop docker-api`) et relancez.
   Le script doit afficher un **message clair** et sortir avec un **code de retour non nul**.

</div>

<div class="valid">
✅ <strong>Validation</strong> : <code>python inventaire.py</code> produit <code>inventaire.json</code> ;
le nombre de types d'objets est égal au champ <code>count</code> de NetBox ;
avec l'API Docker arrêtée, un message explicite et <code>echo $?</code> différent de 0. Script commité.
</div>

--

## TP2 : mémo

<div class="memo">

**Les adresses et le token viennent de l'environnement**

```python
import os
DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
JETON = os.environ["NETBOX_TOKEN"]        # pas de valeur par défaut pour un secret
```

Charger le `.env` dans le terminal : `set -a; source .env; set +a` (Git Bash, Linux, macOS).

**Calcul du CPU à partir de `/stats`**

```python
cpu, avant = stats["cpu_stats"], stats["precpu_stats"]
delta_cpu = cpu["cpu_usage"]["total_usage"] - avant["cpu_usage"]["total_usage"]
delta_systeme = cpu["system_cpu_usage"] - avant.get("system_cpu_usage", 0)
pourcent = delta_cpu / delta_systeme * cpu["online_cpus"] * 100 if delta_systeme else 0.0

memoire_mo = stats["memory_stats"]["usage"] / 1024 / 1024
```

**Sortir en erreur** : `sys.exit("message")` affiche le message et renvoie le code 1.

</div>

--

## TP2 : si vous bloquez

<div class="left">

- **« `KeyError: 'NETBOX_TOKEN'` »** → la variable n'est pas chargée dans ce terminal.
  Rechargez le `.env`, ou vérifiez avec `echo $NETBOX_TOKEN`.
- **« NetBox répond 403 »** → le token est mal formé. Il s'écrit `nbt_<key>.<token>`,
  précédé de `Bearer ` dans le header.
- **« Mon script est très lent »** → vous avez écrit `localhost`. Mettez `127.0.0.1`.
- **« Je compte 50 types d'objets, NetBox en annonce 163 »** → vous n'avez lu que la première
  page. Suivez le champ `next` tant qu'il n'est pas `None`.
- **« `stats` met une seconde par conteneur »** → c'est normal : Docker mesure sur une seconde
  pour calculer un delta.

</div>

---

## TP3 : Le squelette de l'API <span class="small">(~1h30)</span>

**Objectif** : la première version de votre API, en lecture seule, livrée en conteneur.

<div class="left">

1. Installez `fastapi`, `uvicorn`, `python-dotenv`. Créez `app/__init__.py` (vide) et `app/main.py`.
2. Écrivez `GET /health`. Lancez `uvicorn app.main:app --reload --env-file .env`, ouvrez `/docs`.
3. Écrivez `GET /containers` : seulement les conteneurs **étiquetés**, au format du contrat.
4. Écrivez `GET /containers/{id}` : **404** s'il est inconnu, **404** aussi s'il n'a pas le label.
5. L'adresse de l'API Docker vient de la variable **`DOCKER_API_URL`**.
6. Lancez `python verifier.py lecture`. Corrigez jusqu'au vert.
7. Écrivez le **`Dockerfile`**, décommentez le service `api` du compose, arrêtez votre uvicorn
   local, puis `docker compose up -d --build api`. Relancez le vérificateur.

</div>

<div class="valid">
✅ <strong>Validation</strong> : <code>python verifier.py lecture</code> affiche <strong>7/7</strong>,
l'API tournant <strong>dans son conteneur</strong>. Chaque étape fait l'objet d'un commit. Tout est poussé.
</div>

--

## TP3 : mémo

<div class="memo">

**Arborescence visée**

```text
adminapi/
├── app/
│   ├── __init__.py
│   └── main.py
├── Dockerfile
├── requirements.txt        fastapi, uvicorn, requests, python-dotenv
├── docker-compose.yml
├── .env.example            versionné, sans valeur
├── .env                    PAS versionné
└── verifier.py
```

**Le cycle de travail** : uvicorn local avec `--reload` pour développer (rapide), le conteneur
pour valider (c'est lui qui sera corrigé). Les deux utilisent le port 8000 : **un seul à la fois**.

**Reconstruire après une modification** : `docker compose up -d --build api`

**Voir pourquoi le conteneur ne démarre pas** : `docker compose logs api`

</div>

--

## TP3 : si vous bloquez

<div class="left">

- **« Connection refused » depuis le conteneur** → dans le conteneur, `127.0.0.1` désigne le
  conteneur lui-même. L'API Docker s'y appelle `http://docker-api:2375` : c'est ce que fixe le
  bloc `environment` du service `api` dans le compose.
- **« Le navigateur ne joint pas l'API conteneurisée »** → il manque `--host 0.0.0.0` dans le `CMD`.
- **« Le vérificateur voit un conteneur en trop »** → votre liste ne filtre pas par label.
- **« 404 attendu, reçu 200 pour un conteneur sans label »** → dans le détail, regardez
  `detail["Config"]["Labels"]`. Attention : ce champ peut valoir `None`.
- **« 500 Internal Server Error »** → lisez la trace dans le terminal d'uvicorn, la réponse est dedans.

</div>

--

## TP3 : si vous avez fini en avance

<div class="left">

- Sortez les appels à Docker dans un module `app/docker_client.py` : `main.py` ne doit plus
  contenir aucune URL de l'API Docker. Vous vous remercierez au TP4.
- Déclarez un `response_model` sur vos deux routes et regardez ce que ça change dans `/docs`.
- Arrêtez l'API Docker et appelez `GET /containers`. Votre API répond 500 : faites-lui répondre
  **502** avec un message clair. Pourquoi 502 et pas 500 ?
- Lisez `projet/sujet.html` en entier, et repérez dans `contrat-openapi.yaml` les routes du TP4.

</div>

---

## Avant de partir

<div class="left">

- `git status` propre, `git push` fait.
- `git log --oneline` : plusieurs commits, des messages qui se comprennent.
- `git log --all --oneline -- .env` n'affiche **rien** : le `.env` n'a jamais été commité.

</div>

<div class="valid">
D'ici la prochaine demi-journée : terminez le TP3 si ce n'est pas fait. La suite s'appuie
entièrement dessus, et il n'y aura pas de temps de rattrapage en séance.
</div>

---

## La prochaine fois

<div class="left">

**Écrire, sécuriser, réagir**

- Infrastructure as Code, NetDevOps, pilotage des équipements réseau et des clouds par API
- Authentification : clés d'API, tokens, JWT, OAuth2
- Valider ce qu'on reçoit, et ne jamais se faire injecter une commande
- Les webhooks : quand c'est l'infrastructure qui vous appelle

Votre API apprendra à **créer, arrêter et supprimer** des conteneurs, à **refuser** ceux qui
n'ont pas le droit, à **tenir NetBox à jour** et à **redémarrer** un service tombé.

</div>
