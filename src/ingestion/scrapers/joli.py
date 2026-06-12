import requests
import pandas as pd

from ingestion.core import config
from ingestion.core.base_extractor import BaseScraper
from ingestion.core.logger import get_logger
from ingestion.core.decorators import log_execution


class JoliScraper(BaseScraper):

    def __init__(self):
        super().__init__("joli")
        self.logger = get_logger("joli")

    @log_execution("joli")
    def run(self):

        data = []

        for produto in config.PRODUTOS:

            self.logger.info(f"Coletando: {produto}")

            inicio = 0

            while True:

                params = {
                    "ft": produto,
                    "_from": inicio,
                    "_to": inicio + config.JOLI_PAGE_SIZE - 1
                }

                response = requests.get(
                    config.JOLI_BASE_URL,
                    params=params,
                    timeout=config.REQUEST_TIMEOUT
                )

                if not response.ok:
                    self.logger.error(
                        f"HTTP {response.status_code} | produto={produto}"
                    )
                    break

                products = response.json()

                if not products:
                    break

                for product in products:

                    try:
                        item = product["items"][0]
                        seller = item["sellers"][0]
                        offer = seller.get("commertialOffer", {})

                        data.append(
                            self.add_timestamp({
                                "source": "joli",
                                "search_term": produto,
                                "product_id": product.get("productId"),
                                "product_name": product.get("productName"),
                                "brand": product.get("brand"),
                                "price": offer.get("Price"),
                                "list_price": offer.get("ListPrice"),
                                "product_url": product.get("link")
                            })
                        )

                    except Exception as e:
                        self.logger.error(
                            f"Erro produto {produto}: {e}"
                        )

                inicio += config.JOLI_PAGE_SIZE
                self.sleep()

        self.logger.info(f"Registros brutos: {len(data)}")

        df = pd.DataFrame(data)

        self.logger.info(f"Registros no dataframe: {len(df)}")

        if not df.empty:
            df = df.drop_duplicates(subset=["product_id"])
        
        self.save("joli_products.csv", df)

        self.logger.info(f"Após remoção de duplicados: {len(df)}"
        )

if __name__ == "__main__":
    JoliScraper().run()

        