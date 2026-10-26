## 1. Du CLI à l'API

<p class="lead">Un administrateur qui tape des commandes est un goulot d'étranglement. Une infrastructure qui expose une API se pilote à l'échelle.</p>

---

## Le script shell qui lit un écran

Lister les conteneurs arrêtés, à l'ancienne :

```bash
ssh admin@serveur "docker ps -a" | grep Exited | awk '{print $NF}'
```

<div class="left">

Ce script **lit une sortie faite pour des yeux humains** :

- une colonne ajoutée dans une nouvelle version, et `awk` renvoie autre chose ;
- un nom de conteneur contenant « Exited », et le filtre se trompe ;
- en cas d'erreur, il renvoie une liste vide : **impossible de distinguer « aucun » de « panne »** ;
- il exige un accès SSH complet à la machine, pour une simple lecture.

</div>

<p class="small">On appelle ça du <em>screen scraping</em>. C'est fragile par construction.</p>

---

## La même question, posée à une API

```bash
curl --get http://127.0.0.1:2375/containers/json \
     --data-urlencode 'filters={"status":["exited"]}'
```

```json
[
  { "Id": "4f1c9a…", "Names": ["/web1"], "Image": "nginx:alpine", "State": "exited" }
]
```

<div class="left">

- Une réponse **structurée** : des champs nommés, pas des colonnes à compter.
- Un **code de statut** : 200 avec une liste vide n'est pas une erreur 500.
- Un **contrat** documenté et versionné, qui ne change pas au gré de l'affichage.
- Un **droit précis** (lire les conteneurs), pas un shell sur la machine.

</div>

---

## Tout ce que vous administrez a une API

| Ce que vous pilotez | Son API |
|---|---|
| Conteneurs | Docker Engine API, API Kubernetes |
| Machines virtuelles | Proxmox VE API, vSphere, OpenStack |
| Cloud public | API AWS, Azure, GCP (la console web n'est qu'un client parmi d'autres) |
| Équipements réseau | RESTCONF, NETCONF, API constructeurs |
| Inventaire, adressage IP | NetBox |
| Supervision, tickets, DNS, dépôts git | presque toujours une API REST |

<p class="lead">Le terminal et l'interface web sont des <strong>clients</strong> de ces API. Votre script peut en être un autre.</p>

<p class="small">La commande <code>docker</code> elle-même ne fait que des appels HTTP à l'API Docker Engine.</p>

---

## Ce que ça change dans le métier

<div class="left">

| Avant | Avec des API |
|---|---|
| Une procédure Word, rejouée à la main | Un script versionné dans git, relu, rejouable |
| « Ça marchait sur le serveur de Paul » | Le même appel donne le même résultat partout |
| L'inventaire est un tableur périmé | L'inventaire est une API, interrogée et mise à jour par les outils |
| On découvre la panne quand un client appelle | Une alerte déclenche une action automatique |

</div>

<p class="small">Ces pratiques ont un nom : <em>Infrastructure as Code</em>, et côté réseau <em>NetDevOps</em>. On y revient à la prochaine demi-journée.</p>
