# 🕐 Watch Price Comparator — Web Scraping Pipeline with Docker

> Projet personnel de Data Engineering — pipeline de collecte, transformation et visualisation de données produits en temps réel

---

## 🎯 Objectif

Ce projet implémente un **comparateur de prix de montres** en agrégeant automatiquement les données de 4 sites e-commerce français. Il couvre l'ensemble du cycle de la donnée : extraction web → nettoyage → stockage en base → exposition via interface web — le tout orchestré dans un environnement **Docker multi-conteneurs**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐ │
│  │   Scrapy     │───▶│  MySQL 8     │◀───│  Flask App    │ │
│  │  (4 spiders) │    │  (scrapy_db) │    │  (port 5000)  │ │
│  └──────────────┘    └──────────────┘    └───────────────┘ │
│                             │                               │
│                      ┌──────────────┐                       │
│                      │ phpMyAdmin   │                       │
│                      │  (port 8084) │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**Flux de données :**
1. `auto_run_scripts.py` lance les conteneurs Docker et attend que MySQL soit prêt
2. Les 4 spiders Scrapy crawlent en parallèle les sites cibles
3. Le pipeline nettoie les données (prix, références) et les insère dans MySQL
4. L'application Flask interroge la base et affiche un comparatif trié par prix

---

## 🔍 Sites ciblés (4 sources)

| Spider | Site | Données extraites |
|---|---|---|
| `spider_1` | [maty.com](https://www.maty.com) | Nom, prix, URL, référence produit |
| `spider_2` | [bijouteriehaubois.fr](https://www.bijouteriehaubois.fr) | Nom, prix, URL, référence produit |
| `spider_3` | [cleor.com](https://www.cleor.com) | Nom, prix, URL, référence produit |
| `spider_4` | [ocarat.com](https://www.ocarat.com) | Nom, prix, URL, référence produit |

Chaque spider gère la **pagination automatique** et effectue une **requête secondaire** sur la page produit pour extraire la référence fabricant.

---

## ⚙️ Stack technique

| Catégorie | Technologie |
|---|---|
| Web scraping | Python · Scrapy (XPath) |
| Conteneurisation | Docker · Docker Compose |
| Base de données | MySQL 8 · phpMyAdmin |
| Exposition des données | Flask · Jinja2 |
| Connecteur Python/MySQL | PyMySQL |
| Automatisation | Script Python (`subprocess`, boucle de retry MySQL) |

---

## 🧪 Pipeline de traitement des données

La classe `WatchCompPipeline` effectue les transformations suivantes avant insertion :

- **Nettoyage du prix** : extraction des chiffres via regex, remplacement de la virgule par un point, cast en `float`
- **Nettoyage de la référence** : suppression des espaces superflus (`strip` + `re.sub`)
- **Gestion des erreurs** : les items invalides sont exclus via `DropItem`

```python
# Exemple : "1 299,00 €" → 1299.0
cleaned_price = re.sub(r'[^\d,\.]', '', price_str).replace(',', '.')
item['price'] = float(cleaned_price)
```

---

## 📊 Interface de comparaison

L'application Flask expose un tableau HTML dynamique (`localhost:5000`) qui :
- Regroupe les montres **par référence fabricant** (identifiant commun entre sites)
- Trie les offres **par prix croissant** au sein de chaque groupe
- Met en **évidence le meilleur prix** (en vert)
- Affiche le nom du site marchand déduit depuis l'URL

---

## 🚀 Lancement du projet

### Prérequis
- Docker & Docker Compose installés
- Python 3.x + `pymysql` (`pip install pymysql`)

### Démarrage en une commande

```bash
python auto_run_scripts.py
```

Ce script :
1. Lance `docker compose up --build -d`
2. Attend que MySQL soit disponible (retry loop, 10 tentatives × 5s)
3. Exécute `run_spiders.py` pour lancer les 4 crawlers en parallèle

### Accès aux interfaces

| Service | URL |
|---|---|
| Comparateur de prix | http://localhost:5000 |
| phpMyAdmin | http://localhost:8084 |

---

## 📁 Structure du projet

```
├── auto_run_scripts.py          # Orchestrateur : Docker + attente MySQL + spiders
├── docker-compose.yml           # Services : MySQL, phpMyAdmin, Flask
├── init.sql                     # Schéma initial de la base (table products)
├── watch_comp/                  # Projet Scrapy
│   ├── run_spiders.py           # Lancement parallèle des 4 crawlers
│   └── watch_comp/
│       ├── spiders/
│       │   ├── spider_1.py      # Crawler maty.com
│       │   ├── spider_2.py      # Crawler bijouteriehaubois.fr
│       │   ├── spider_3.py      # Crawler cleor.com
│       │   └── spider_4.py      # Crawler ocarat.com
│       ├── pipelines.py         # Nettoyage + export JSON + insertion MySQL
│       ├── items.py             # Définition du modèle de données
│       └── settings.py          # Configuration Scrapy (pipelines, robots.txt)
└── web/
    ├── app.py                   # Application Flask
    ├── requirements.txt
    ├── Dockerfile
    └── templates/
        └── index.html           # Tableau comparatif
```

---

## 💡 Points techniques notables

- **Crawling multi-sources en parallèle** via `CrawlerProcess` de Scrapy
- **Requêtes en cascade** : chaque spider suit les liens produits pour récupérer la référence (2 niveaux de parsing XPath)
- **Retry loop sur MySQL** : le script d'orchestration attend la disponibilité du service avant de lancer les spiders, évitant les race conditions au démarrage Docker
- **Isolation complète** : l'environnement est 100% reproductible via Docker, sans dépendance à l'installation locale

---

## 👤 Auteur

**Igor Laminsi**  
Ingénieur Data en recherche d'un CDI
[GitHub](https://github.com/igorlam00237) · [LinkedIn](https://www.linkedin.com/in/igor-laminsi/)
