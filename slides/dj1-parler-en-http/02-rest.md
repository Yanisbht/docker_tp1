## 2. REST et HTTP

<p class="lead">REST n'est ni un protocole ni une norme : c'est une <strong>façon d'utiliser HTTP</strong> pour manipuler des ressources.</p>

Ce bloc donne le vocabulaire que vous retrouverez dans toutes les API du cours, et dans le quiz.

---

## Une requête HTTP, en entier

```http
POST /containers HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer 3fK9…
Content-Type: application/json

{"name": "web1", "image": "nginx:alpine"}
```

| Élément | Ici | Rôle |
|---|---|---|
| **Méthode** (verbe) | `POST` | ce qu'on veut faire |
| **Chemin** (URI) | `/containers` | sur quoi |
| **Headers** | `Authorization`, `Content-Type` | qui parle, dans quel format |
| **Corps** | le JSON | les données envoyées |

---

## Une réponse HTTP, en entier

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /containers/4f1c9a…

{"id": "4f1c9a…", "name": "web1", "image": "nginx:alpine", "state": "running"}
```

| Élément | Ici | Rôle |
|---|---|---|
| **Code de statut** | `201` | ce qui s'est passé, lisible par une machine |
| **Headers** | `Content-Type`, `Location` | le format, l'adresse de ce qui a été créé |
| **Corps** | le JSON | la représentation de la ressource |

<p class="lead">Un client bien écrit lit <strong>d'abord le code de statut</strong>, ensuite seulement le corps.</p>

---

## La ressource

<div class="left">

Une **ressource** est une chose que l'API expose : un conteneur, une machine virtuelle,
un sous-réseau, une alerte. Chaque ressource a une **adresse** (URI) qui l'identifie.

| URI | Désigne |
|---|---|
| `/containers` | la **collection** des conteneurs |
| `/containers/4f1c9a` | **un** conteneur précis |
| `/containers/4f1c9a/logs` | une sous-ressource de ce conteneur |

</div>

<div class="memo">

**Des noms, pas des verbes.** L'URI dit *sur quoi* on agit, la méthode HTTP dit *quoi faire*.

<span class="ko">✗</span> `GET /getContainers` · `POST /deleteContainer?id=4f1c` · `GET /containers/4f1c/delete`

<span class="ok">✓</span> `GET /containers` · `DELETE /containers/4f1c`

</div>

---

## Les verbes

| Méthode | Sur une collection `/containers` | Sur un élément `/containers/4f1c` |
|---|---|---|
| **GET** | lister | lire |
| **POST** | créer un nouvel élément | (déclencher une action, voir plus loin) |
| **PUT** | | remplacer **entièrement** |
| **PATCH** | | modifier **partiellement** |
| **DELETE** | | supprimer |

<div class="left">

- `PUT` envoie la ressource complète : un champ oublié est un champ effacé.
- `PATCH` n'envoie que ce qui change : `{"status": "offline"}`.

</div>

<p class="small">Vous utiliserez <code>PATCH</code> dès le projet, pour changer le statut d'une machine virtuelle dans NetBox.</p>

---

## Sûr, idempotent : deux mots à connaître

<div class="left">

- **Sûre** : la méthode ne modifie rien. On peut l'appeler sans crainte.
- **Idempotente** : l'appeler **une fois ou dix fois** laisse le système dans le **même état**.

</div>

| Méthode | Sûre | Idempotente | Pourquoi |
|---|---|---|---|
| GET | ✓ | ✓ | lire ne change rien |
| PUT | ✗ | ✓ | remplacer deux fois par la même valeur donne la même valeur |
| DELETE | ✗ | ✓ | après le premier appel, la ressource n'existe plus, et après le dixième non plus |
| PATCH | ✗ | pas garantie | dépend de ce qu'on envoie |
| POST | ✗ | ✗ | deux `POST /containers` créent deux conteneurs |

<p class="small">L'idempotence porte sur l'<strong>état du serveur</strong>, pas sur le code renvoyé : le second <code>DELETE</code> peut très bien répondre 404.</p>

---

## Pourquoi l'idempotence vous concerne

<p class="lead">Le réseau coupe. Votre script ne reçoit pas de réponse. A-t-il le droit de recommencer ?</p>

<div class="left">

| La requête perdue était | Recommencer est |
|---|---|
| `GET /containers` | sans risque |
| `DELETE /containers/4f1c` | sans risque : au pire, un 404 |
| `POST /containers` | **dangereux** : peut-être deux conteneurs, peut-être un conflit de nom |

</div>

<div class="valid">
Un outil d'automatisation rejoue ses actions en permanence (nouvelle tentative, exécution planifiée, relance après une panne). Une opération idempotente peut être rejouée les yeux fermés. C'est la propriété la plus précieuse en administration système.
</div>

---

## Et les actions qui ne sont pas du CRUD ?

Arrêter un conteneur, ce n'est ni le créer, ni le lire, ni le supprimer.

<div class="cols">
<div>
<h4>Option 1 : une sous-ressource d'action</h4>
<pre><code class="language-http">POST /containers/4f1c/stop</code></pre>
<p class="small">Choix de l'API Docker Engine, et du contrat de votre projet. Simple et lisible, au prix d'un verbe dans l'URI.</p>
</div>
<div>
<h4>Option 2 : modifier l'état souhaité</h4>
<pre><code class="language-http">PATCH /containers/4f1c
&#32;
{"state": "exited"}</code></pre>
<p class="small">Plus fidèle à REST : on déclare l'état voulu. Choix de Kubernetes et de NetBox.</p>
</div>
</div>

<p class="small">Les deux se rencontrent. L'important est d'être cohérent dans toute l'API, et de ne jamais déclencher une action avec un <code>GET</code>.</p>

---

## Les codes de statut : cinq familles

| Famille | Sens | Qui doit agir |
|---|---|---|
| **1xx** | information | personne |
| **2xx** | **succès** | personne |
| **3xx** | redirection, « rien de neuf » | le client suit |
| **4xx** | **erreur du client** : la requête est mauvaise | le client corrige **avant** de réessayer |
| **5xx** | **erreur du serveur** : la requête était peut-être bonne | le client peut réessayer plus tard |

<p class="lead">4xx : « c'est de ta faute ». 5xx : « c'est de la mienne ».</p>

<p class="small">Cette distinction pilote toute la logique de nouvelle tentative d'un script.</p>

---

## Les codes que vous allez produire et recevoir

| Code | Nom | Quand |
|---|---|---|
| **200** | OK | lecture ou action réussie, avec un corps |
| **201** | Created | ressource créée |
| **202** | Accepted | demande acceptée, traitement en cours ou différé |
| **204** | No Content | réussi, rien à renvoyer (suppression) |
| **400** / **422** | Bad Request / Unprocessable | corps illisible / corps lisible mais invalide |
| **401** | Unauthorized | je ne sais pas **qui** tu es |
| **403** | Forbidden | je sais qui tu es, tu n'as **pas le droit** |
| **404** | Not Found | cette ressource n'existe pas |
| **409** | Conflict | incompatible avec l'état actuel (nom déjà pris, déjà arrêté) |
| **429** | Too Many Requests | ralentis |
| **500** / **502** / **503** | | bug du serveur / un service en amont a échoué / indisponible |

--

## 401 ou 403 ?

<div class="left">

C'est la confusion la plus fréquente, et elle a des conséquences.

| | 401 Unauthorized | 403 Forbidden |
|---|---|---|
| Le serveur sait qui appelle ? | **non** : token absent, expiré ou inconnu | **oui** |
| Que doit faire le client ? | s'authentifier, puis réessayer | **rien** : réessayer ne servira à rien |
| Exemple | pas de header `Authorization` | token lecteur sur une suppression |

</div>

<div class="memo">
Le nom « Unauthorized » est trompeur : 401 parle d'<strong>authentification</strong> (qui es-tu ?), 403 parle d'<strong>autorisation</strong> (qu'as-tu le droit de faire ?).
</div>

--

## 404 ou 409 ? 400 ou 422 ?

<div class="left">

| Situation | Code | Raison |
|---|---|---|
| `GET /containers/inconnu` | **404** | la ressource n'existe pas |
| `POST /containers` avec un nom déjà pris | **409** | la requête est valide, c'est l'**état** qui s'y oppose |
| `POST /containers/4f1c/stop`, déjà arrêté | **409** | même logique |
| Corps qui n'est pas du JSON | **400** ou 422 | illisible |
| JSON correct mais champ manquant ou valeur interdite | **422** | lisible, mais invalide |

</div>

<p class="small">FastAPI répond 422 dans les deux derniers cas : c'est le comportement attendu par le contrat du projet.</p>

---

## Le piège du « 200 avec une erreur dedans »

<div class="cols">
<div>
<h4 class="ko">✗ À ne jamais faire</h4>
<pre><code class="language-http">HTTP/1.1 200 OK
&#32;
{"success": false,
 "error": "conteneur introuvable"}</code></pre>
<p class="small">Le client doit lire le corps pour savoir si ça a marché. Les outils de supervision voient un succès.</p>
</div>
<div>
<h4 class="ok">✓ Le code dit la vérité</h4>
<pre><code class="language-http">HTTP/1.1 404 Not Found
&#32;
{"detail": "Conteneur introuvable"}</code></pre>
<p class="small">Le code suffit pour décider. Le corps explique à l'humain.</p>
</div>
</div>

<p class="lead">Le code de statut est pour la machine, le corps est pour l'humain.</p>

---

## Stateless

<div class="left">

**Chaque requête se suffit à elle-même.** Le serveur ne garde aucun souvenir de la
précédente : pas de « session ouverte », pas de « répertoire courant ».

Conséquences pratiques :

- le token d'authentification est renvoyé **à chaque requête** ;
- n'importe quel serveur d'une ferme peut traiter n'importe quelle requête ;
- une requête peut être rejouée, mise en cache, tracée isolément.

</div>

<p class="small">C'est l'inverse d'une session SSH, où chaque commande dépend de ce qu'on a tapé avant.</p>

---

## Ce qui fait qu'une API est « REST »

<div class="left">

| Contrainte | En clair |
|---|---|
| **Client-serveur** | le client ne connaît que l'interface, pas l'implémentation |
| **Stateless** | chaque requête porte tout son contexte |
| **Interface uniforme** | des ressources adressées par URI, manipulées par les verbes HTTP, via des représentations (JSON) |
| **Cache** | une réponse dit si elle peut être réutilisée |
| **Système en couches** | un proxy ou un load balancer peut s'intercaler sans que le client le sache |

</div>

<p class="small">Formulées par Roy Fielding en 2000. Dans la pratique, on dit « REST » pour toute API HTTP + JSON organisée en ressources.</p>

---

## Ce qu'il faut retenir

<div class="left">

1. Une **ressource** a une URI. L'URI est un **nom**, la méthode est le **verbe**.
2. **GET** ne modifie jamais rien.
3. **GET, PUT, DELETE** sont idempotents, **POST** ne l'est pas : c'est ce qui autorise ou interdit de réessayer.
4. Le **code de statut** dit la vérité : 2xx réussi, 4xx le client corrige, 5xx le client peut réessayer.
5. **401** : qui es-tu ? **403** : tu n'as pas le droit.
6. Le serveur est **stateless** : chaque requête porte tout ce qu'il faut.

</div>
