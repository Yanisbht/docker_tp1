# API Rest pour l'administration système

<p class="lead">Demi-journée 1 : parler à une infrastructure en HTTP</p>

<p class="small">Maximilien CRUZ</p>

---

## Ce que vous saurez faire à la fin du cours

<div class="left">

- **Lire** la documentation d'une API et l'explorer sans interface graphique
- **Consommer** une API d'infrastructure depuis un script Python robuste
- **Concevoir et écrire** votre propre API d'administration
- **La sécuriser** : authentification, validation des entrées, secrets
- **La faire réagir** à des événements, et **l'observer** avec des métriques

</div>

<p class="lead">Le fil conducteur : arrêter de cliquer et de se connecter en SSH pour faire ce qu'une requête HTTP fait mieux.</p>

---

## Trois demi-journées, un seul projet

| | Thème | Ce que vous construisez |
|---|---|---|
| **1** | Parler à une infrastructure en HTTP | Un script d'inventaire, puis le squelette de votre API |
| **2** | Écrire, sécuriser, réagir | Création et suppression, authentification, inventaire NetBox, webhook |
| **3** | Observer, documenter, rendre | Métriques, documentation, puis quiz et rendu |

<p class="small">Entre deux demi-journées, vous avez plusieurs semaines : le projet avance aussi chez vous.</p>

---

## Le projet

<p class="lead">Une <strong>micro-API d'administration</strong> qui pilote les conteneurs Docker de votre machine et tient l'inventaire à jour dans NetBox.</p>

<div class="left">

- Il n'y a **pas de sujet séparé** : chaque TP ajoute une brique au projet.
- **Individuel**, dans **votre dépôt GitHub**.
- Un **contrat** précis : routes, codes de statut, format JSON. Voir `projet/sujet.html`.
- Un **vérificateur** fourni : il vous dit à tout moment ce qui passe.

</div>

<div class="valid">
La correction est automatique. Elle lance votre API sans vous et lui parle en HTTP,
exactement comme le fait le vérificateur, avec en plus des cas que vous ne connaissez pas.
</div>

---

## La note

<div class="left">

| Composante | Poids |
|---|---|
| **Projet**, dans son état à la fin de la troisième demi-journée | **2/3** |
| **Quiz** de 20 questions, sur feuille, à la troisième demi-journée | **1/3** |

</div>

<div class="left">

- Les TP ne sont pas notés un par un : seul le résultat final compte.
- L'**historique de commits** est regardé. Commitez à chaque étape qui fonctionne.
- **Aucun secret** dans le dépôt, ni dans le code, ni dans l'historique.
- Le quiz porte sur les **concepts**, jamais sur la syntaxe d'un outil.
- Une IA peut vous **expliquer**, pas écrire à votre place : vous pouvez être **interrogé sur votre code**.

</div>

---

## Le format de chaque demi-journée

<div class="left">

1. **Une heure de théorie au maximum**, tout de suite, d'une traite.
2. **Tout le reste en TP**, en autonomie, à votre rythme.

</div>

<div class="memo">

Il n'y a pas de reprise magistrale ensuite. Ces slides sont donc **votre documentation** :
elles contiennent les commandes réelles et des exemples complets. Gardez-les ouvertes.
Recherche dans les slides : <kbd>Ctrl</kbd>+<kbd>Maj</kbd>+<kbd>F</kbd>. Vue d'ensemble : <kbd>O</kbd>.

</div>

**Appelez-moi tôt** plutôt que de rester bloqué vingt minutes.

---

## Au programme de cette demi-journée

<div class="left">

| Durée | |
|---|---|
| 5′ | Du CLI à l'API : pourquoi |
| 25′ | REST et HTTP : ressources, verbes, codes de statut, idempotence |
| 15′ | Consommer une API : OpenAPI, cURL, `requests` |
| 10′ | Écrire une API : FastAPI en dix minutes |
| ~45′ | **TP1** : mise en route et exploration |
| ~1h15 | **TP2** : script d'inventaire |
| ~1h30 | **TP3** : squelette de votre API |

</div>
