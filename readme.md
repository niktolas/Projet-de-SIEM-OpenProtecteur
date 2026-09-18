# OpenProtecteur

> Plateforme open source légère de collecte, de détection et d’investigation d’événements de sécurité pour environnements Windows et Linux.

[!\[Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[!\[FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[!\[React](https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react\&logoColor=111827)](https://react.dev/)
[!\[PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql\&logoColor=white)](https://www.postgresql.org/)
[!\[Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker\&logoColor=white)](https://www.docker.com/)
[!\[License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Présentation

OpenProtecteur est une application de cybersécurité défensive conçue comme une plateforme SOC légère. Elle centralise des événements de sécurité, applique des règles de corrélation, génère des alertes et fournit une interface d’investigation avec contrôle des accès.

Le projet poursuit deux objectifs :

* construire un produit de cybersécurité démontrable et extensible ;
* approfondir le développement backend et frontend, PostgreSQL, Linux, les API sécurisées, Docker et les pratiques DevSecOps.

OpenProtecteur n’a pas vocation à remplacer une solution SIEM industrielle. Il constitue un environnement pédagogique et un socle technique permettant d’expérimenter la collecte, la détection et l’investigation dans un laboratoire maîtrisé.

## Aperçu

<!-- Ajoutez ici une capture réelle lorsque le dépôt sera publié. -->

!\[Aperçu du tableau de bord OpenProtecteur](docs/screenshots/dashboard.png)

## Fonctionnalités disponibles

### Collecte et stockage

* réception d’événements de sécurité au format JSON ;
* validation des données avec Pydantic ;
* stockage dans PostgreSQL via SQLAlchemy ;
* prise en charge des adresses IPv4 et IPv6 ;
* horodatage de l’événement et de son ingestion ;
* consultation, filtrage et pagination des événements ;
* récupération d’un événement par UUID ;
* suppression contrôlée réservée aux administrateurs.

### Détection

* détection de tentatives de brute force sur les authentifications ;
* corrélation par adresse IP source et utilisateur ;
* fenêtre temporelle de cinq minutes ;
* seuil configurable dans le code, fixé actuellement à cinq échecs ;
* création automatique d’une alerte de criticité élevée ;
* prévention des alertes dupliquées dans une même fenêtre.

### Investigation

* consultation paginée des alertes ;
* filtres par criticité, statut et adresse IP ;
* panneau détaillé d’investigation ;
* visualisation de la fenêtre temporelle de détection ;
* workflow de traitement :

  * `open` ;
  * `investigating` ;
  * `resolved` ;
  * `false\_positive` ;
* validation des transitions de statut par le backend.

### Authentification et autorisations

* comptes utilisateurs stockés dans PostgreSQL ;
* mots de passe hachés avec Argon2 ;
* authentification par jeton JWT temporaire ;
* comptes actifs ou désactivés ;
* contrôle d’accès fondé sur trois rôles :

  * `viewer` : consultation ;
  * `analyst` : consultation et traitement des alertes ;
  * `admin` : administration et opérations sensibles ;
* interface adaptée au rôle de l’utilisateur ;
* retour automatique à la connexion lorsque la session n’est plus valide.

### Interface

* frontend React et TypeScript ;
* page de connexion ;
* tableau des événements ;
* tableau des alertes ;
* filtres et pagination ;
* panneau latéral de détail ;
* actions d’investigation selon les permissions ;
* interface responsive ;
* communication avec l’API via un reverse proxy Nginx.

### Déploiement

* installation manuelle documentable avec PostgreSQL, systemd et Nginx ;
* images Docker séparées pour le backend et le frontend ;
* build multi-stage pour React et Nginx ;
* orchestration avec Docker Compose ;
* réseau Docker interne ;
* volume PostgreSQL persistant ;
* migrations Alembic exécutées avant le backend ;
* health checks sur PostgreSQL, FastAPI et Nginx.

## Architecture

```text
Navigateur
    |
    v
Frontend React servi par Nginx
    |
    | /api/\*
    v
Backend FastAPI / Uvicorn
    |
    +--> Authentification JWT et RBAC
    |
    +--> Services métier
    |
    +--> Moteur de détection
    |
    v
SQLAlchemy
    |
    v
PostgreSQL
```

### Organisation du backend

```text
Requête HTTP
    |
    v
Route FastAPI
    |
    v
Service métier
    |
    v
Repository SQLAlchemy
    |
    v
PostgreSQL
```

* **Routes** : gestion du protocole HTTP, des paramètres et des codes de réponse.
* **Services** : règles métier, transactions et orchestration des détections.
* **Repositories** : requêtes SQLAlchemy et accès aux données.
* **Schémas Pydantic** : validation des entrées et contrôle des sorties.
* **Modèles SQLAlchemy** : représentation des tables PostgreSQL.
* **Alembic** : versionnement du schéma de base de données.

## Technologies

### Backend

* Python 3.12 ;
* FastAPI ;
* Uvicorn ;
* Pydantic ;
* SQLAlchemy 2 ;
* Alembic ;
* Psycopg ;
* PyJWT ;
* pwdlib avec Argon2 ;
* Pytest.

### Frontend

* React ;
* TypeScript ;
* Vite ;
* CSS natif ;
* API Fetch du navigateur.

### Infrastructure

* PostgreSQL 16 ;
* Nginx ;
* systemd pour le déploiement manuel ;
* Docker Engine ;
* Docker Compose.

## Structure du dépôt

```text
OpenProtecteur/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   ├── migrations/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── deploy/
│   ├── nginx/
│   └── systemd/
├── docs/
│   └── screenshots/
├── compose.yaml
├── .env.example
├── LICENSE
├── SECURITY.md
└── README.md
```

## Démarrage rapide avec Docker Compose

### Prérequis

* Git ;
* Docker Engine ;
* plugin Docker Compose.

### 1\. Cloner le dépôt

```bash
git clone https://github.com/YOUR\_GITHUB\_USERNAME/OpenProtecteur.git
cd OpenProtecteur
```

### 2\. Créer la configuration PostgreSQL

Créez un fichier `.env.docker` à la racine :

```dotenv
POSTGRES\_DB=openprotecteurdb
POSTGRES\_USER=user\_openprotecteur\_app
POSTGRES\_PASSWORD=replace-with-a-strong-password
```

### 3\. Créer la configuration du backend

Créez un fichier `backend.env.docker` à la racine :

```dotenv
APP\_NAME=OpenProtecteur
APP\_ENV=production
APP\_HOST=0.0.0.0
APP\_PORT=8000
DEBUG=false

POSTGRES\_HOST=postgres
POSTGRES\_PORT=5432
POSTGRES\_DB=openprotecteurdb
POSTGRES\_USER=user\_openprotecteur\_app
POSTGRES\_PASSWORD=replace-with-the-same-password

TEST\_POSTGRES\_DB=openprotecteurdb\_test

JWT\_SECRET\_KEY=replace-with-a-random-secret
JWT\_ALGORITHM=HS256
ACCESS\_TOKEN\_EXPIRE\_MINUTES=30
```

Un secret JWT peut être généré avec :

```bash
openssl rand -hex 32
```

Les fichiers contenant les secrets sont ignorés par Git. Ne les publiez jamais.

### 4\. Construire et démarrer la plateforme

```bash
docker compose up -d --build
```

### 5\. Vérifier les services

```bash
docker compose ps
docker compose logs migrate
```

État attendu :

```text
postgres    healthy
migrate     exited (0)
backend     healthy
frontend    healthy
```

### 6\. Créer le premier administrateur

```bash
docker compose run --rm \\
  backend \\
  python -m scripts.create\_admin
```

### 7\. Ouvrir l’application

Par défaut, le frontend est publié sur l’interface locale de l’hôte :

```text
http://127.0.0.1:8080
```

Pour une VM distante, utilisez un tunnel SSH :

```bash
ssh -L 8080:127.0.0.1:8080 user@server
```

Puis ouvrez localement :

```text
http://127.0.0.1:8080
```

## Développement local sans Docker

Ce mode est recommandé pour comprendre chaque composant et bénéficier du rechargement automatique.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Configurez `backend/.env` à partir de l’exemple, puis appliquez les migrations :

```bash
alembic upgrade head
```

Démarrez l’API :

```bash
uvicorn app.main:app \\
  --host 127.0.0.1 \\
  --port 8000 \\
  --reload
```

Documentation interactive :

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Interface de développement :

```text
http://127.0.0.1:5173
```

Le proxy Vite transmet les requêtes `/api` au backend local.

## Tests

### Backend

Une base PostgreSQL séparée doit être utilisée pour éviter toute altération des données de développement.

```bash
cd backend
source .venv/bin/activate
pytest -v
```

Avec couverture :

```bash
pytest \\
  --cov=app \\
  --cov-report=term-missing
```

### Frontend

Vérification TypeScript et build de production :

```bash
cd frontend
npm run build
```

## Exemple de détection

La première règle détecte une tentative de brute force lorsque cinq événements remplissent les conditions suivantes :

```text
Type          authentication\_failure
Adresse IP    identique
Utilisateur   identique
Fenêtre       cinq minutes
Seuil         cinq événements
```

Exemple d’événement transmis à l’API :

```json
{
  "source": "linux\_auth",
  "hostname": "srv-linux-01",
  "event\_type": "authentication\_failure",
  "username": "admin",
  "source\_ip": "192.168.1.42",
  "severity": "medium",
  "message": "Failed SSH authentication"
}
```

Lorsque le seuil est atteint, OpenProtecteur génère une alerte similaire à :

```json
{
  "rule\_name": "authentication\_brute\_force",
  "title": "Possible authentication brute force",
  "severity": "high",
  "status": "open",
  "source\_ip": "192.168.1.42",
  "username": "admin",
  "event\_count": 5
}
```

## API principale

### Routes publiques

```text
GET  /
GET  /health
GET  /health/database
POST /auth/token
```

### Routes authentifiées

```text
GET    /auth/me
GET    /events
POST   /events
GET    /events/{event\_id}
DELETE /events/{event\_id}
GET    /alerts
GET    /alerts/{alert\_id}
PATCH  /alerts/{alert\_id}/status
GET    /users
POST   /users
```

Les autorisations exactes dépendent du rôle de l’utilisateur.

## Commandes Docker utiles

Démarrer ou reconstruire :

```bash
docker compose up -d --build
```

Consulter l’état :

```bash
docker compose ps
```

Suivre les logs :

```bash
docker compose logs -f
```

Appliquer les migrations :

```bash
docker compose run --rm migrate
```

Arrêter et supprimer les conteneurs et le réseau :

```bash
docker compose down
```

Le volume PostgreSQL est conservé avec cette commande.

> Attention : `docker compose down -v` supprime également le volume et peut effacer les données PostgreSQL.

## Sécurité

Les mesures déjà intégrées comprennent :

* hachage Argon2 des mots de passe ;
* jetons JWT signés et limités dans le temps ;
* contrôle des comptes actifs ;
* RBAC côté backend ;
* validation des entrées avec Pydantic ;
* ORM et requêtes paramétrées ;
* secrets externalisés ;
* PostgreSQL non publié par Docker Compose ;
* backend non publié directement dans l’architecture Compose ;
* utilisateur non privilégié dans l’image backend ;
* réponses d’erreur limitant l’exposition des détails SQL.

Limites actuelles :

* stockage du jeton frontend dans `sessionStorage` ;
* absence de renouvellement et de révocation de jetons ;
* absence de limitation des tentatives de connexion ;
* absence de HTTPS intégré ;
* absence de journal d’audit complet ;
* moteur de détection encore limité à une règle principale.

N’exposez pas cette version directement sur Internet sans durcissement supplémentaire, reverse proxy HTTPS, restrictions réseau et gestion adaptée des secrets.

Pour signaler une vulnérabilité, consultez [SECURITY.md](SECURITY.md). Ne publiez pas de vulnérabilité exploitable dans une issue publique.

## Roadmap

### Version 0.1

* \[x] ingestion d’événements ;
* \[x] stockage PostgreSQL ;
* \[x] détection de brute force ;
* \[x] gestion des alertes ;
* \[x] authentification JWT ;
* \[x] RBAC ;
* \[x] frontend React ;
* \[x] déploiement manuel ;
* \[ ] Docker Compose.

### Prochaines évolutions

* \[ ] relier explicitement chaque alerte à ses événements sources ;
* \[ ] afficher les événements associés dans l’investigation ;
* \[ ] ajouter un journal d’audit ;
* \[ ] conserver l’historique des changements de statut ;
* \[ ] assigner une alerte à un analyste ;
* \[ ] ajouter des commentaires d’investigation ;
* \[ ] détecter les échecs suivis d’une réussite ;
* \[ ] détecter le password spraying ;
* \[ ] rendre les règles configurables ;
* \[ ] rattacher les détections à MITRE ATT\&CK ;
* \[ ] ajouter un générateur de données de démonstration ;
* \[ ] ajouter GitHub Actions et les analyses de sécurité ;
* \[ ] développer des collecteurs Linux et Windows ;
* \[ ] étudier des actions de réponse contrôlées avec Ansible.

## Limites du projet

OpenProtecteur est un projet expérimental orienté apprentissage et démonstration. Il ne doit pas être considéré comme une solution de sécurité prête pour un environnement de production critique.

Les données de démonstration doivent rester synthétiques. N’envoyez pas de journaux réels contenant des informations personnelles, confidentielles ou appartenant à une organisation sans autorisation explicite.

## Contribution

Les contributions sont les bienvenues sous forme de :

* corrections de bugs ;
* tests supplémentaires ;
* nouvelles règles de détection documentées ;
* améliorations d’accessibilité ;
* documentation ;
* propositions d’architecture.

Avant une contribution importante, ouvrez une issue présentant le besoin, le comportement attendu et l’approche envisagée.

## Licence

Ce projet est distribué sous licence MIT. Consultez le fichier [LICENSE](LICENSE).

## Auteur

Projet personnel développé par **Nicolas Williame** dans le cadre d’un apprentissage pratique du développement, de l’administration système et de la cybersécurité défensive.

