# API Rest pour l'administration système : demi-journée 1

Support de la **première demi-journée** : parler à une infrastructure en HTTP.

## Avant de commencer

Il te faut, installés et fonctionnels :

- **Docker** (Docker Desktop sous Windows et macOS), avec `docker compose` ;
- **Python 3.10 ou plus récent** ;
- **git**, et un compte **GitHub** ;
- un éditeur de code (VS Code convient très bien) ;
- sous Windows : **Git Bash** (installé avec Git pour Windows) pour les commandes cURL.

Vérifie tout de suite :

```bash
docker run --rm hello-world
docker compose version
python --version
```

## Lancer les slides

Les slides chargent des fichiers Markdown : il faut un serveur HTTP local (`file://` ne marche pas).

```bash
cd slides
python -m http.server 8001
```

Puis ouvre <http://127.0.0.1:8001>. Le port 8000 est réservé à ton API.

> Les slides sont ta **documentation** pendant les TP : commandes réelles, exemples complets,
> mémos. Navigation : flèches / espace, vue d'ensemble avec `O`, recherche avec `Ctrl+Maj+F`.

## Le projet

Le dossier `projet/` contient tout ce dont tu as besoin :

| Fichier | Rôle |
|---|---|
| `sujet.html` | le contrat complet de l'API à construire, les règles de rendu, le barème |
| `docker-compose.yml` | l'environnement : API Docker Engine et NetBox |
| `contrat-openapi.yaml` | le contrat formel, à ouvrir dans <https://editor.swagger.io> |
| `verifier.py` | le vérificateur : ce qui passe, ce qui manque |
| `.env.example` | les variables de configuration |
| `surveillant.py` | l'émetteur d'alertes, utilisé à la deuxième demi-journée |
| `AGENTS.md`, `CLAUDE.md` | les règles d'usage de l'IA, lues automatiquement par les assistants de code |

Copie son contenu à la racine de **ton dépôt git** (voir la slide « Mise en place »).
Attention : `.env.example` est un fichier caché, vérifie qu'il a bien été copié.

## Programme de la demi-journée

| Théorie (une heure) | TP en autonomie |
|---|---|
| Du CLI à l'API, REST et HTTP, cURL, OpenAPI, `requests`, FastAPI | TP1 exploration (~45′) · TP2 script d'inventaire (~1h15) · TP3 squelette de l'API (~1h30) |

## Évaluation

`note finale = projet × 2/3 + quiz × 1/3`

Le projet est le résultat des TP. Il est noté dans son état à la fin de la troisième
demi-journée, par un programme qui lance ton API et lui parle en HTTP. Lis `projet/sujet.html`
dès aujourd'hui : il n'y a aucune surprise, tout y est écrit.

## Arborescence

```
.
├── slides/    supports Reveal.js de la demi-journée
└── projet/    sujet, environnement, contrat, vérificateur
```
