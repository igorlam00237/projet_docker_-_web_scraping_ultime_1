# 🕐 Watch Price Comparator — Web Scraping Pipeline with Docker

> **Pipeline de Data Engineering complet** : collecte multi-sources · nettoyage · stockage MySQL · visualisation Flask — orchestré via Docker Compose

<br>

## 📌 Objectif

Ce projet implémente un **comparateur de prix de montres** en agrégeant automatiquement les données de **4 sites e-commerce français**. Il couvre l'ensemble du cycle de la donnée :

```
Extraction web  →  Nettoyage  →  Stockage BDD  →  Interface web
   (Scrapy)       (Pipeline)      (MySQL)           (Flask)
```

<br>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                           │
│                                                                 │
│   ┌───────────────┐     ┌──────────────┐     ┌─────────────┐   │
│   │    Scrapy     │────▶│   MySQL 8    │◀────│  Flask App  │   │
│   │  (4 spiders)  │     │  scrapy_db   │     │  port 5000  │   │
│   └───────────────┘     └──────────────┘     └─────────────┘   │
│                                │                                │
│                         ┌──────────────┐                        │
│                         │  phpMyAdmin  │                        │
│                         │  port 8084   │                        │
│                         └──────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

**Flux d'exécution :**
1. `auto_run_scripts.py` démarre les conteneurs Docker et attend la disponibilité de MySQL
2. Les **4 spiders Scrapy** crawlent les sites en parallèle (pagination + requête produit)
3. Le **pipeline de nettoyage** normalise les prix et références puis insère en base
4. L'**application Flask** interroge MySQL et affiche le comparatif trié par prix

<br>

## 🔍 Sources de données (4 sites ciblés)

| Spider | Site | Technique de scraping |
|:---:|:---|:---|
| `spider_1` | [maty.com](https://www.maty.com/montres.html) | XPath · pagination `data-href` · follow URL produit |
| `spider_2` | [bijouteriehaubois.fr](https://www.bijouteriehaubois.fr/fr/montres) | XPath · pagination `aria-label` · follow URL produit |
| `spider_3` | [cleor.com](https://www.cleor.com/montres-C10.htm) | XPath · pagination `title="Next page"` · follow URL produit |
| `spider_4` | [ocarat.com](https://ocarat.com/montre/) | XPath · pagination `link[rel=next]` · follow URL produit |

> Chaque spider effectue **2 niveaux de parsing** : listing (nom + prix) puis page produit (référence fabricant), via `response.follow()` et `meta`.

<br>

## ⚙️ Stack technique

| Couche | Technologie |
|:---|:---|
| Web scraping | Python · **Scrapy** · XPath |
| Conteneurisation | **Docker** · **Docker Compose** |
| Base de données | **MySQL 8** · PyMySQL |
| Administration BDD | **phpMyAdmin** |
| Interface web | **Flask** · Jinja2 |
| Automatisation | Python (`subprocess` · retry loop) |

<br>

## 🧪 Pipeline de traitement des données

Le module `pipelines.py` enchaîne **3 étapes** avant chaque insertion :

### 1. Nettoyage du prix — `WatchCompPipeline`
```python
# "1 299,00 €"  →  1299.0
cleaned_price = re.sub(r'[^\d,\.]', '', price_str)
item['price'] = float(cleaned_price.replace(',', '.'))
```

### 2. Nettoyage de la référence
```python
# "  ABC 123  "  →  "ABC123"
item['ref'] = re.sub(r'\s+', '', item['ref'].strip())
```

### 3. Insertion MySQL — `MySQLPipeline`
```python
cursor.execute("""
    INSERT INTO products (name, price, url, reference)
    VALUES (%s, %s, %s, %s)
""", (item['name'], item['price'], item['url'], item['ref']))
```
> Les items invalides sont écartés via `DropItem` pour garantir l'intégrité des données.

<br>

## 📊 Interface de comparaison

L'application Flask expose un **tableau comparatif** sur `localhost:5000` :

- 🔗 Regroupement des montres **par référence fabricant** (clé commune entre sites)
- 📈 Tri des offres **par prix croissant** au sein de chaque groupe
- ✅ **Mise en évidence du meilleur prix** (affiché en vert)
- 🏪 Identification du site marchand déduit depuis l'URL du produit

<br>

## 🚀 Lancement

### Prérequis
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- Python 3.x + dépendance : `pip install pymysql`

### Démarrage en une commande

```bash
python auto_run_scripts.py
```

Ce script orchestre automatiquement :

| Étape | Action |
|:---:|:---|
| 1 | `docker compose up --build -d` — build et démarrage des conteneurs |
| 2 | Retry loop (10 × 5s) — attend la disponibilité de MySQL |
| 3 | `python run_spiders.py` — lancement des 4 crawlers en parallèle |

### Accès aux services

| Service | URL |
|:---|:---|
| 🌐 Comparateur de prix | http://localhost:5000 |
| 🛢️ phpMyAdmin | http://localhost:8084 |

<br>

## 📁 Structure du projet

```
📦 watch-price-comparator
├── 🐍 auto_run_scripts.py          # Orchestrateur : Docker + attente MySQL + spiders
├── 🐳 docker-compose.yml           # Services : MySQL, phpMyAdmin, Flask
├── 🗄️  init.sql                     # Schéma initial de la base (table products)
│
├── 📂 watch_comp/                   # Projet Scrapy
│   ├── 🐍 run_spiders.py            # Lancement parallèle des 4 crawlers
│   └── watch_comp/
│       ├── spiders/
│       │   ├── 🕷️  spider_1.py      # Crawler — maty.com
│       │   ├── 🕷️  spider_2.py      # Crawler — bijouteriehaubois.fr
│       │   ├── 🕷️  spider_3.py      # Crawler — cleor.com
│       │   └── 🕷️  spider_4.py      # Crawler — ocarat.com
│       ├── 🐍 pipelines.py          # Nettoyage + export JSON + insertion MySQL
│       ├── 🐍 items.py              # Modèle de données Scrapy
│       └── 🐍 settings.py           # Configuration (pipelines, robots.txt, encoding)
│
└── 📂 web/                          # Application Flask
    ├── 🐍 app.py                    # Routes et logique de regroupement/tri
    ├── 🐳 Dockerfile
    ├── 📋 requirements.txt
    └── templates/
        └── 🌐 index.html            # Tableau comparatif Jinja2
```

<br>

## 💡 Points techniques notables

- **Crawling parallèle multi-sources** via `CrawlerProcess` de Scrapy — les 4 spiders s'exécutent simultanément dans le même processus
- **Scraping en 2 niveaux** : chaque spider suit les liens produits pour extraire la référence fabricant, permettant le croisement des données entre sites
- **Retry loop robuste sur MySQL** : l'orchestrateur attend la disponibilité effective de la base avant de lancer les spiders, évitant les race conditions au démarrage Docker
- **Environnement 100% reproductible** : aucune dépendance locale requise au-delà de Docker

<br>

---

<div align="center">

**Igor Laminsi**
- Ingénieur Big Data & IA
[![GitHub](https://img.shields.io/badge/GitHub-igorlam00237-181717?style=flat&logo=github)](https://github.com/igorlam00237) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Igor%20Lam-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/igor-laminsi/)

&

**Kenfack Gabrisson**  
Ingénieur Big Data & IA
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Gabrisson%20Kenfack-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/gabrisson-kenfack-bb3b2223a/)

</div>
