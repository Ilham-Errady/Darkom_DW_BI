import os
import pandas as pd
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

def run_warehouse_pipeline():
    logging.info("--- DEBUT DU CHARGEMENT DATA WAREHOUSE ---")
    
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    
    try:
        # 1. Extraction (Controle de presence des donnees clean)
        df = pd.read_sql_table('cls_annonces', schema='clean', con=engine)
        if df.empty:
            logging.error("La table clean.cls_annonces est vide ! Abandon.")
            return False
            
        with engine.connect() as conn:
            # 2. Nettoyage des anciennes donnees du Warehouse (Trancate avec CASCADE)
            logging.info("Vidage des tables du Data Warehouse...")
            conn.execute(text("TRUNCATE TABLE bi_schema.fact_annonces CASCADE;"))
            conn.execute(text("TRUNCATE TABLE bi_schema.dim_temps CASCADE;"))
            conn.execute(text("TRUNCATE TABLE bi_schema.dim_localisation CASCADE;"))
            conn.execute(text("TRUNCATE TABLE bi_schema.dim_caracteristiques CASCADE;"))
            conn.commit()
            
            # 3. Chargement de la Dimension Temporelle (dim_temps)
            logging.info("Chargement de dim_temps...")
            df_temps = df[['date_publication', 'annonce_annee', 'annonce_trimestre', 'annonce_mois']].drop_duplicates()
            df_temps.columns = ['date_key', 'annee', 'trimestre', 'mois']
            df_temps.to_sql('dim_temps', schema='bi_schema', con=engine, if_exists='append', index=False)
            
            # 4. Chargement de la Dimension Localisation (dim_localisation)
            logging.info("Chargement de dim_localisation...")
            df_loc = df[['ville', 'quartier']].drop_duplicates()
            df_loc.to_sql('dim_localisation', schema='bi_schema', con=engine, if_exists='append', index=False)
            
            # 5. Chargement de la Dimension Caracteristiques (dim_caracteristiques)
            logging.info("Chargement de dim_caracteristiques...")
            df_carac = df[['type_bien', 'transaction', 'categorie_prix', 'categorie_surface', 'annee_construction']].drop_duplicates()
            df_carac.to_sql('dim_caracteristiques', schema='bi_schema', con=engine, if_exists='append', index=False)
            
            conn.commit()
            
            # 6. Recuperation des Cles Generees pour le Mapping (Optimisation des relations)
            dim_loc_db = pd.read_sql_table('dim_localisation', schema='bi_schema', con=engine)
            dim_carac_db = pd.read_sql_table('dim_caracteristiques', schema='bi_schema', con=engine)
            
            # 7. Creation de la Table de Faits (fact_annonces) via Joins
            logging.info("Mapping et preparation de la table de faits...")
            df_fact = df.merge(dim_loc_db, on=['ville', 'quartier'], how='inner')
            df_fact = df_fact.merge(dim_carac_db, on=['type_bien', 'transaction', 'categorie_prix', 'categorie_surface', 'annee_construction'], how='inner')
            
            df_fact['date_key'] = df_fact['date_publication']
            
            df_fact_final = df_fact[[
                'annonce_id', 'date_key', 'localisation_key', 'caracteristique_key',
                'prix_mad', 'surface_m2', 'prix_m2', 'nb_chambres', 'nb_salles_bain', 'etage', 'age_bien'
            ]]
            
            # 8. Controle de coherence des donnees (Data Integrity Check)
            if len(df_fact_final) == len(df):
                logging.info(f"✓ Controle de coherence reussi : 100% des lignes mappees ({len(df_fact_final)}/{len(df)}).")
            else:
                logging.warning(f"⚠️ Alerte coherence : {len(df) - len(df_fact_final)} lignes perdues lors du mapping.")
            
            # 9. Insertion finale dans la table de faits
            df_fact_final.to_sql('fact_annonces', schema='bi_schema', con=engine, if_exists='append', index=False)
            conn.commit()
            
        logging.info("✓ DATA WAREHOUSE CHARGE ET OPTIMISE AVEC SUCCES !")
        return True
        
    except Exception as e:
        logging.error(f"✗ Erreur lors du chargement du Warehouse : {str(e)}")
        return False

if __name__ == "__main__":
    run_warehouse_pipeline()