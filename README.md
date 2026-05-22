**Markdown**

```
# Darkom — End-to-End Real Estate Data Warehouse & Analytics

## 📝 Contexte du Projet
**Darkom.ma** est une plateforme marocaine d'annonces immobilières qui permet aux particuliers et professionnels de publier des offres de vente et de location de biens immobiliers à travers le Maroc. Les données publiées contiennent une grande quantité d'informations hétérogènes qui nécessitent un traitement rigoureux avant toute analyse.

Dans ce projet, l'objectif est de couler un pipeline de données industriel complet permettant de transformer des données brutes issues d'un fichier CSV en une architecture prête pour l'analyse décisionnelle.

L'architecture du projet suit un flux moderne et standardisé :
```text
Source (CSV) ──> Staging Layer ──> Clean Data ──> Data Warehouse ──> Power BI
```

Le Data Warehouse est modélisé selon un schéma dimensionnel optimisé pour l'analyse décisionnelle, exploité via Power Query et le langage DAX pour concevoir des tableaux de bord interactifs et dynamiques.

## 🏗️ Tâches et Étapes du Projet

### 1. Préparation de l'environnement

* Installation et configuration de  **PostgreSQL** .
* Création d'une base de données dédiée nommée : `darkom_dwh`.
* Structuration du projet en couches de données clairement séparées :
  * **Staging :** Couche de réception temporaire.
  * **Clean :** Couche de traitement et de qualité.
  * **Warehouse :** Couche de stockage final (`bi_schema`).

### 2. Chargement des données brutes (Staging Layer)

* **Fichier source :** `darkom-annonces.csv`
* **Colonnes intégrées :** `annonce_id`, `date_publication`, `titre`, `ville`, `quartier`, `type_bien`, `transaction`, `prix`, `surface`, `nb_chambres`, `nb_salles_bain`, `etage`, `annee_construction`.
* **Actions :** Importation automatisée du CSV vers la table PostgreSQL de staging, vérification de l'intégrité et mise en place de logs d'audit simples pour tracer le chargement. Cette couche sert uniquement de zone temporaire.

### 3. Nettoyage des données (Clean Layer)

* **Processus de qualité appliqué :**
  * Suppression systématique des doublons.
  * Gestion des valeurs manquantes et imputation logique (`date_publication`, `quartier`, `nb_chambres`, `nb_salles_bain`, `etage`, `annee_construction`, `type_bien`, `transaction`).
  * Détection et traitement des valeurs aberrantes ( *outliers* ) sur le `prix`, la `surface` et le `nb_chambres`.
* **Standardisation & Normalisation :**
  * Uniformisation des noms de villes et harmonisation des types de biens et des transactions.
  * Correction stricte des types de données (Conversion de `date_publication` en type `DATE` et sécurisation des types numériques).

### 4. Feature Engineering (Variables Dérivées)

Création de nouvelles métriques et axes analytiques pertinents :

* **Prix par m² :** Ratio direct pour l'évaluation standardisée.
* **Âge estimé :** Âge du bien calculé à partir de son année de construction.
* **Catégories de prix :** Segmentation du marché ( *Économique* ,  *Moyen* ,  *Haut standing* ,  *Luxe* ).
* **Catégories de surface :** Segmentation de l'espace ( *Petit (< 80 m²)* ,  *Moyen (80-150 m²)* ,  *Grand (> 150 m²)* ).
* **Dimensions Temporelles :** Extraction de l'Année, Mois et Trimestre de publication.

### 5. Modélisation et Chargement du Data Warehouse

* **Choix Architectural :** Modèle en Étoile ( *Star Schema* ) stocké dans le schéma isolé `bi_schema`.
* **Structure :** * Une table de faits centrale (`fact_annonces`) contenant les clés étrangères et les métriques quantitatives.
  * Trois tables de dimensions : `dim_caracteristiques`, `dim_localisation`, et `dim_temps`.
* **Optimisation :** Indexation des colonnes clés, mise en place des contraintes d'intégrité référentielle, contrôle de cohérence et nettoyage final automatique de la zone de staging après chaque chargement réussi.

## 🛠️ Stack Technique

* **Langage & Transformation :** Python 3.x (Pandas, SQLAlchemy, Logging)
* **Base de Données (DWH) :** PostgreSQL 16+
* **Restitution BI :** Power BI Desktop (Power Query & Langage DAX)
* **Configuration :** Fichiers `.env` et `.gitignore`

## 📂 Structure du Répertoire

**Plaintext**

```
├── data/                    # Données brutes sources
│   └── darkom-annonces.csv
├── database/                # Scripts d'initialisation et structures SQL (DDL/DML)
│   ├── 01_init_db.sql               # Création de la database darkom_dwh
│   ├── 02_staging_tables.sql        # Table temporaire d'ingestion brute
│   ├── 03_clean_processing.sql      # Procédures de nettoyage et standardisation
│   └── 04_warehouse_star_schema.sql # Création du bi_schema (Faits & Dimensions)
├── etl/                     # Scripts Python d'automatisation ETL
│   ├── connection.py        # Gestion de la connexion PostgreSQL
│   ├── pipeline_clean.py    # Algorithmes de traitement et Feature Engineering
│   ├── pipeline_staging.py  # Ingestion automatisée vers la couche Staging
│   └── pipeline_warehouse.py# Chargement final et indexation du modèle en étoile
├── logs/                    # Traces, audits et logs d'exécution industriels
│   └── pipeline.log
├── .env                     # Configuration des variables d'environnement (exclu)
├── .gitignore               # Fichiers et dossiers ignorés par Git
├── README.md                # Documentation principale du projet
└── requirements.txt         # Dépendances Python du projet
```

## ⚙️ Couche Métier : Mesures DAX (Centralisées dans `_Measures_KPIs`)

* **Nombre Total d'Annonces :**
  **Extrait de code**

  ```
  Total Annonces = COUNT(fact_annonces[fact_key])
  ```
* **Prix Moyen du Marché :**
  **Extrait de code**

  ```
  Prix Moyen = AVERAGE(fact_annonces[Prix (DH)])
  ```
* **Surface Moyenne :**
  **Extrait de code**

  ```
  Surface Moyenne = AVERAGE(fact_annonces[Surface (m²)])
  ```
* **Prix Moyen au m² :**
  **Extrait de code**

  ```
  Prix Moyen au m² = AVERAGE(fact_annonces[prix_m2])
  ```
* **Taux de Croissance des Annonces (Time Intelligence N vs N-1) :**
  **Extrait de code**

  ```
  Taux Croissance Annonces = 
  VAR _AnnoncesMoisActuel = [Total Annonces]
  VAR _AnnoncesMoisPrecedent = CALCULATE([Total Annonces], PARALLELPERIOD(dim_temps[date_key], -1, MONTH))
  RETURN DIVIDE(_AnnoncesMoisActuel - _AnnoncesMoisPrecedent, _AnnoncesMoisPrecedent, 0)
  ```

## 📊 Solution Analytique & Dashboards (Power BI)

L'application décisionnelle est connectée directement à la base de données PostgreSQL (`bi_schema`), épurée via **Power Query** pour la validation finale des types, et structurée en  **4 Dashboards dynamiques** .

### 🎛️ Filtres Interactifs Globaux

Toutes les pages intègrent des segments de filtrage interactifs. Les graphiques sont 100% réactifs aux filtres suivants :

* **Ville** | **Type de bien** | **Type de transaction** | **Plage de prix** | **Surface** | **Période (Temps)**

### 📈 Spécifications des Pages du Rapport

#### Dashboard 1 — Vue Globale du Marché

* **KPIs Cards :** Nombre total d'annonces, Prix moyen du marché, Surface moyenne.
* **Analyses Graphiques :** Répartition des annonces par Ville, Évolution temporelle du nombre d'annonces (Courbe), Répartition par type de bien (Donut Chart), Répartition Vente vs Location (Pie Chart).

#### Dashboard 2 — Analyse des Prix

* **Distribution & Performance :** Analyse fine par catégorie de prix (Économique, Moyen, Haut standing, Luxe).
* **Indicateur m² :** Analyse du Prix moyen par m² croisé par axe géographique.
* **Segmentation :** Comparaison des segments immobiliers et Prix moyen par type de bien.

#### Dashboard 3 — Analyse Géographique

* **Cartographie Spatiale :** Visualisation géographique des prix sur carte interactive (Taille des bulles indexée sur le volume).
* **Classement :** Palmarès ( *Top 10* ) des zones et quartiers les plus chers.
* **Densité Locale :** Top quartiers par nombre d'annonces et Tableau Matriciel hiérarchique ( *Drill-Down* ) affichant le Prix moyen par couple Ville et Quartier.

#### Dashboard 4 — Analyse des Tendances

* **Cinétique :** Évolution conjointe des prix et du volume des annonces dans le temps.
* **Saisonnalité :** Analyse saisonnière de l'activité immobilière par trimestre et par mois.
* **Croissance Périodique :** Matrice comparative et calcul du taux de croissance de la Période N vs Période N-1.

*Développé de manière industrielle pour le suivi, l'audit et l'analyse du marché foncier national au Maroc.*
