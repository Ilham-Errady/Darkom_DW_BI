CREATE SCHEMA IF NOT EXISTS clean;

DROP TABLE IF EXISTS clean.cls_annonces CASCADE;

CREATE TABLE clean.cls_annonces (
    annonce_id VARCHAR(50) PRIMARY KEY,
    date_publication DATE,
    titre TEXT,
    ville VARCHAR(100),
    quartier VARCHAR(150),
    type_bien VARCHAR(50),
    transaction VARCHAR(50),
    prix_mad NUMERIC(12, 2),
    surface_m2 INT,
    nb_chambres INT,
    nb_salles_bain INT,
    etage INT,
    annee_construction INT,
    prix_m2 NUMERIC(12, 2),
    age_bien INT,
    categorie_prix VARCHAR(50),
    categorie_surface VARCHAR(50),
    annonce_annee INT,
    annonce_mois INT,
    annonce_trimestre INT
);