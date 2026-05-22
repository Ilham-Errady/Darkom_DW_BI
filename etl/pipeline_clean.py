import os
import pandas as pd
import numpy as np
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

def run_comprehensive_clean_pipeline():
    logging.info("--- DEBUT DU PIPELINE CLEAN & FEATURES ---")
    
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    
    try:
        df = pd.read_sql_table('stg_annonces', schema='staging', con=engine)
        logging.info(f"Donnees brutes extraites : {len(df)} lignes.")
        
        df.replace('[null]', np.nan, inplace=True)
        df.replace('nan', np.nan, inplace=True)
        df.drop_duplicates(subset=['annonce_id'], keep='first', inplace=True)
        
        df['prix_mad'] = pd.to_numeric(df['prix'], errors='coerce')
        df['surface_m2'] = pd.to_numeric(df['surface'], errors='coerce')
        df.dropna(subset=['annonce_id', 'prix_mad', 'surface_m2'], inplace=True)
        
        df = df[(df['prix_mad'] >= 1000) & (df['surface_m2'] >= 10) & (df['surface_m2'] <= 5000)]
        
        df['nb_chambres'] = pd.to_numeric(df['nb_chambres'], errors='coerce').fillna(0).astype(int)
        df['nb_salles_bain'] = pd.to_numeric(df['nb_salles_bain'], errors='coerce').fillna(0).astype(int)
        df['etage'] = pd.to_numeric(df['etage'], errors='coerce').fillna(0).astype(int)
        df['annee_construction'] = pd.to_numeric(df['annee_construction'], errors='coerce').fillna(2020).astype(int)
        
        df['date_publication'] = pd.to_datetime(df['date_publication'], errors='coerce').fillna(pd.Timestamp.now())
        df['ville'] = df['ville'].str.strip().str.upper().str.replace('È', 'E').str.replace('É', 'E')
        df['quartier'] = df['quartier'].str.strip().str.capitalize().fillna('Inconnu')
        df['type_bien'] = df['type_bien'].str.strip().str.capitalize().fillna('Autre')
        df['transaction'] = df['transaction'].str.strip().str.capitalize()
        
        df['prix_m2'] = np.where(df['surface_m2'] > 0, (df['prix_mad'] / df['surface_m2']).round(2), 0)
        df['age_bien'] = np.where((2026 - df['annee_construction']) < 0, 0, 2026 - df['annee_construction'])
        
        cond_prix = [df['prix_mad'] < 300000, df['prix_mad'] < 1000000, df['prix_mad'] < 3000000]
        choix_prix = ['Economique', 'Moyen standing', 'Haut standing']
        df['categorie_prix'] = np.select(cond_prix, choix_prix, default='Luxe')
        
        cond_surf = [df['surface_m2'] < 80, df['surface_m2'] <= 150]
        choix_surf = ['Petit (< 80 m²)', 'Moyen (80-150 m²)']
        df['categorie_surface'] = np.select(cond_surf, choix_surf, default='Grand (> 150 m²)')
        
        df['annonce_annee'] = df['date_publication'].dt.year
        df['annonce_mois'] = df['date_publication'].dt.month
        df['annonce_trimestre'] = df['date_publication'].dt.quarter
        df['date_publication'] = df['date_publication'].dt.date

        df_final = df[[
            'annonce_id', 'date_publication', 'titre', 'ville', 'quartier', 
            'type_bien', 'transaction', 'prix_mad', 'surface_m2', 
            'nb_chambres', 'nb_salles_bain', 'etage', 'annee_construction',
            'prix_m2', 'age_bien', 'categorie_prix', 'categorie_surface',
            'annonce_annee', 'annonce_mois', 'annonce_trimestre'
        ]]
        
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE clean.cls_annonces;"))
            conn.commit()
            
        df_final.to_sql('cls_annonces', schema='clean', con=engine, if_exists='append', index=False)
        logging.info(f"✓ Succes ! Pipeline termine avec {len(df_final)} lignes inserees.")
        return True
        
    except Exception as e:
        logging.error(f"✗ Erreur : {str(e)}")
        return False

if __name__ == "__main__":
    run_comprehensive_clean_pipeline()