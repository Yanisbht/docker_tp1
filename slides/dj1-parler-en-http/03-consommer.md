## 3. Consommer une API

<p class="lead">Lire la documentation, essayer à la main, puis seulement écrire le script.</p>

Dans cet ordre. Un script écrit sans avoir essayé l'appel à la main se débogue deux fois.

---

## OpenAPI : le contrat lisible par une machine

**OpenAPI** (anciennement Swagger) est un format, JSON ou YAML, qui décrit une API :
ses chemins, ses méthodes, ses paramètres, ses corps, ses codes de réponse.

```yaml
paths:
  /containers/{identifiant}:
    get:
      summary: Détail d'un conteneur géré
      responses:
        '200':
          description: Le conteneur
        '404':
          description: Conteneur inconnu ou non géré par l'API
```

<div class="left">

À partir de ce seul fichier, des outils produisent : une **documentation interactive**
(Swagger UI), des **clients** dans n'importe quel langage, des **tests de conformité**.

</div>

---

## Lire une documentation Swagger UI

<div class="left">

Ouvrez celle de NetBox : <http://127.0.0.1:8080/api/schema/swagger-ui/>

Pour chaque opération, cherchez **quatre choses**, dans cet ordre :

1. la **méthode** et le **chemin** ;
2. les **paramètres** : lesquels sont obligatoires, lesquels sont des filtres ;
3. le **corps attendu** (onglet *Schema*, pas seulement l'exemple) ;
4. les **codes de réponse** possibles, et la forme du corps pour chacun.

</div>

<div class="memo">
Le bouton <strong>Try it out</strong> envoie une vraie requête et affiche la commande cURL équivalente. C'est le moyen le plus rapide de passer de la documentation à une commande qui marche.
</div>

<p class="small">Votre propre API aura la sienne, générée automatiquement, sur <code>/docs</code>.</p>

---

## cURL : l'outil de référence

```bash
curl -i http://127.0.0.1:2375/containers/web1/json
```

| Option | Effet |
|---|---|
| `-i` | affiche le code de statut et les headers de la réponse |
| `-s` | silencieux (pas de barre de progression) |
| `-X POST` | choisit la méthode (GET par défaut) |
| `-H "Nom: valeur"` | ajoute un header |
| `-d '{"a": 1}'` | envoie un corps (et passe en POST) |
| `-d @corps.json` | envoie le contenu d'un fichier |
| `--get --data-urlencode 'cle=valeur'` | encode proprement un paramètre d'URL |
| `-o /dev/null -w "%{http_code}\n"` | n'affiche que le code de statut |

<p class="small">Postman, Bruno ou l'extension REST Client de VS Code font la même chose avec une interface. cURL a un avantage : il se colle dans un ticket, un script ou une documentation.</p>

--

## cURL : les pièges

<div class="memo">

**Sous Windows PowerShell**, `curl` est un alias d'une autre commande. Utilisez **Git Bash**,
ou écrivez `curl.exe`. Les guillemets du JSON se passent mal dans PowerShell : mettez le
corps dans un fichier et envoyez-le avec `-d @corps.json`.

**`127.0.0.1` plutôt que `localhost`** : sous Windows, `localhost` tente d'abord l'IPv6 et
chaque appel depuis Python perd 2 secondes. Dans tout le cours, écrivez `127.0.0.1`.

**N'oubliez pas `Content-Type`** quand vous envoyez du JSON :
`-H "Content-Type: application/json"`. Sans lui, beaucoup d'API répondent 415 ou 422.

**`jq`** met en forme et filtre le JSON : `curl -s … | jq '.[].Names'`.
Sans `jq` : `curl -s … | python -m json.tool`.

</div>

---

## L'API Docker Engine, à la main

```bash
# Lister tous les conteneurs, y compris arrêtés
curl -s "http://127.0.0.1:2375/containers/json?all=true"

# Seulement ceux qui portent un label
curl -s --get http://127.0.0.1:2375/containers/json \
     --data-urlencode 'all=true' \
     --data-urlencode 'filters={"label":["adminapi.managed=true"]}'

# Le détail d'un conteneur, par nom ou par identifiant
curl -s http://127.0.0.1:2375/containers/web1/json

# L'arrêter, et ne regarder que le code
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:2375/containers/web1/stop
```

| Réponse à `stop` | Sens |
|---|---|
| **204** | arrêté |
| **304** | il était déjà arrêté |
| **404** | ce conteneur n'existe pas |

<p class="small">Documentation complète : <a href="https://docs.docker.com/reference/api/engine/">docs.docker.com/reference/api/engine</a></p>

---

## L'API NetBox, à la main

```bash
# Obtenir un token (une seule fois) : notez "key" et "token" dans la réponse
curl -s -X POST http://127.0.0.1:8080/api/users/tokens/provision/ \
     -H "Content-Type: application/json" -H "Accept: application/json" \
     -d '{"username": "admin", "password": "admin"}'
```

Le token à utiliser s'écrit **`nbt_<key>.<token>`**. Placez-le dans une variable :

```bash
export NETBOX_TOKEN="nbt_LoFu2abUVH8J.YvctifOzVjGX…"

curl -s http://127.0.0.1:8080/api/status/ \
     -H "Authorization: Bearer $NETBOX_TOKEN" -H "Accept: application/json"
```

<div class="memo">
Sans token, NetBox répond <strong>403</strong> là où la règle voudrait un 401. Les API réelles ne respectent pas toutes les conventions : <strong>lisez toujours leur documentation</strong>, ne devinez pas.
</div>

---

## De cURL à Python : `requests`

```bash
pip install requests
```

```python
import requests

reponse = requests.get(
    "http://127.0.0.1:2375/containers/json",
    params={"all": "true"},        # devient ?all=true, correctement encodé
    timeout=10,
)

print(reponse.status_code)         # 200
conteneurs = reponse.json()        # le corps JSON, déjà converti en liste Python

for conteneur in conteneurs:
    print(conteneur["Names"][0], conteneur["State"])
```

<p class="small"><code>params=</code> pour l'URL, <code>json=</code> pour le corps, <code>headers=</code> pour les headers. Ne construisez jamais une URL avec des <code>+</code> ou des f-strings pour y glisser des paramètres.</p>

---

## Règle 1 : toujours un `timeout`

<div class="cols">
<div>
<h4 class="ko">✗ Peut bloquer pour toujours</h4>
<pre><code class="language-python">reponse = requests.get(url)</code></pre>
<p class="small">Par défaut, <code>requests</code> attend <strong>indéfiniment</strong>. Un serveur qui ne répond plus fige votre script, votre tâche planifiée, puis la suivante.</p>
</div>
<div>
<h4 class="ok">✓ Échoue vite et clairement</h4>
<pre><code class="language-python">reponse = requests.get(url, timeout=10)</code></pre>
<p class="small">Au bout de 10 secondes, une exception <code>requests.Timeout</code> est levée. Vous savez quoi faire.</p>
</div>
</div>

<p class="lead">Un script d'administration sans timeout est une panne qui attend son heure.</p>

---

## Règle 2 : vérifier le code de statut

`requests` **ne lève pas d'erreur** sur un 404 ou un 500. Si vous ne vérifiez rien, votre
script continue avec un corps d'erreur qu'il prend pour des données.

```python
reponse = requests.get(f"{DOCKER}/containers/{nom}/json", timeout=10)

if reponse.status_code == 404:
    print(f"{nom} : conteneur inconnu")      # cas prévu, traité explicitement
else:
    reponse.raise_for_status()               # tout autre 4xx ou 5xx lève une exception
    detail = reponse.json()
```

<div class="left">

- Les codes que vous **attendez** (404, 409) : traitez-les un par un.
- Tout le reste : `raise_for_status()`, et le script s'arrête avec un message clair.

</div>

---

## Règle 3 : une `Session` pour tout ce qui se répète

```python
import os
import requests

netbox = requests.Session()
netbox.headers["Authorization"] = f"Bearer {os.environ['NETBOX_TOKEN']}"
netbox.headers["Accept"] = "application/json"

reponse = netbox.get("http://127.0.0.1:8080/api/virtualization/clusters/", timeout=10)
```

<div class="left">

- Les headers communs (token, format) sont écrits **une seule fois**.
- La connexion TCP est **réutilisée** d'un appel à l'autre : nettement plus rapide.
- Le token vient d'une **variable d'environnement**, jamais du code source.

</div>

---

## Règle 4 : suivre la pagination

Une API ne renvoie jamais 10 000 objets d'un coup. Elle renvoie une **page** et dit où est la suivante.

```json
{ "count": 163,
  "next": "http://127.0.0.1:8080/api/core/object-types/?limit=50&offset=50",
  "previous": null,
  "results": [ … 50 objets … ] }
```

```python
def tout_lire(session, url):
    resultats = []
    while url:                                   # tant qu'il reste une page
        reponse = session.get(url, timeout=10)
        reponse.raise_for_status()
        page = reponse.json()
        resultats.extend(page["results"])
        url = page["next"]                       # None sur la dernière page
    return resultats
```

<p class="small">Le piège classique : un script qui « marche » sur l'environnement de test (30 objets) et ignore silencieusement les 4 950 autres en production.</p>

---

## Règle 5 : distinguer les pannes

```python
try:
    reponse = session.get(url, timeout=10)
    reponse.raise_for_status()
except requests.ConnectionError:
    sys.exit("Service injoignable : est-il démarré ? L'adresse est-elle bonne ?")
except requests.Timeout:
    sys.exit("Aucune réponse en 10 s : service surchargé ou réseau coupé.")
except requests.HTTPError as erreur:
    sys.exit(f"Le service a refusé : {erreur.response.status_code} {erreur.response.text[:200]}")
```

| Famille | Réessayer ? |
|---|---|
| Connexion refusée, timeout, **5xx**, **429** | oui, après une pause, et seulement si l'opération est idempotente |
| **4xx** (sauf 429) | non : la requête est fausse, elle le restera |

---

## Ce qu'il faut retenir

<div class="left">

1. **Lire** la documentation OpenAPI, **essayer** avec cURL, **puis** scripter.
2. Toujours un **`timeout`**.
3. Toujours **vérifier le code** : traiter ceux qu'on attend, `raise_for_status()` pour les autres.
4. Une **`Session`** pour les headers communs et la réutilisation des connexions.
5. Suivre la **pagination** jusqu'au bout.
6. Les secrets viennent de l'**environnement**, jamais du code.

</div>
