CREATE SCHEMA IF NOT EXISTS bi_schema;

-- 1. Dimension Temporelle
DROP TABLE IF EXISTS bi_schema.dim_temps CASCADE;
CREATE TABLE bi_schema.dim_temps (
    date_key DATE PRIMARY KEY,
    annee INT NOT NULL,
    trimestre INT NOT NULL,
    mois INT NOT NULL
);

-- 2. Dimension Localisation
DROP TABLE IF EXISTS bi_schema.dim_localisation CASCADE;
CREATE TABLE bi_schema.dim_localisation (
    localisation_key SERIAL PRIMARY KEY,
    ville VARCHAR(100) NOT NULL,
    quartier VARCHAR(150) NOT NULL
);

-- 3. Dimension Caracteristiques du Bien
DROP TABLE IF EXISTS bi_schema.dim_caracteristiques CASCADE;
CREATE TABLE bi_schema.dim_caracteristiques (
    caracteristique_key SERIAL PRIMARY KEY,
    type_bien VARCHAR(50),
    transaction VARCHAR(50),
    categorie_prix VARCHAR(50),
    categorie_surface VARCHAR(50),
    annee_construction INT
);

-- 4. Table de Faits (Centrale)
DROP TABLE IF EXISTS bi_schema.fact_annonces CASCADE;
CREATE TABLE bi_schema.fact_annonces (
    fact_key SERIAL PRIMARY KEY,
    annonce_id VARCHAR(50) UNIQUE,
    date_key DATE REFERENCES bi_schema.dim_temps(date_key),
    localisation_key INT REFERENCES bi_schema.dim_localisation(localisation_key),
    caracteristique_key INT REFERENCES bi_schema.dim_caracteristiques(caracteristique_key),
    prix_mad NUMERIC(12, 2),
    surface_m2 INT,
    prix_m2 NUMERIC(12, 2),
    nb_chambres INT,
    nb_salles_bain INT,
    etage INT,
    age_bien INT
);

-- Indexation des colonnes cles pour Power BI
CREATE INDEX idx_fact_date ON bi_schema.fact_annonces(date_key);
CREATE INDEX idx_fact_loc ON bi_schema.fact_annonces(localisation_key);
CREATE INDEX idx_fact_carac ON bi_schema.fact_annonces(caracteristique_key);