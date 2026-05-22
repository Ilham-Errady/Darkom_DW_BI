CREATE TABLE staging.stg_annonces (
    annonce_id VARCHAR(255),
    date_publication VARCHAR(100),
    titre TEXT,
    ville VARCHAR(100),
    quartier VARCHAR(255),
    type_bien VARCHAR(100),
    transaction VARCHAR(100),           
    prix VARCHAR(100),
    surface VARCHAR(100),
    nb_chambres VARCHAR(50),
    nb_salles_bain VARCHAR(50),
    etage VARCHAR(50),
    annee_construction VARCHAR(50),
    date_extraction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);