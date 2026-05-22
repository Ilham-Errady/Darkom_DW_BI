import os
import pandas as pd
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

def run_staging_ingestion():
    logging.info("--- DEBUT INGESTION STAGING ---")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "darkom-annonces.csv")
    
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    
    try:
       
        with engine.connect() as schema_conn:
            schema_conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging;"))
            schema_conn.commit()

        df = pd.read_csv(csv_path, dtype=str, encoding='utf-8')
        
        
        df.to_sql('stg_annonces', schema='staging', con=engine, if_exists='replace', index=False)
        
        logging.info(f"✓ Ingestion reussie. {len(df)} lignes chargees.")
        return True
    except Exception as e:
        logging.error(f"✗ Erreur lors de l'ingestion : {str(e)}")
        return False

if __name__ == "__main__":
    run_staging_ingestion()