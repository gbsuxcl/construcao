import time
import pandas as pd
from datetime import datetime
import os
from core import config

class BaseScraper:

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.data = []
    
    def log(self, message: str):
        print(f"[{self.source_name}] {message}")
    
    def save(self, filename: str, df: pd.DataFrame):
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

        path = os.path.join(config.OUTPUT_DIR, filename)

        df.to_csv(
            path,
            index=False,
            encoding="utf-8-sig",
            sep=";",
            decimal="."
        )

        self.log(f"Arquivo salvo em: {path}")
    
    def add_timestamp(self, row: dict):
        row[config.DATE_FIELD] = datetime.now()
        return row
    
    def sleep(self):
        time.sleep(config.SLEEP_SECONDS)