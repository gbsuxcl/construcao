import requests
import pandas as pd

from ingestion.core import config
from ingestion.core.base_extractor import BaseScraper
from ingestion.core.logger import get_logger
from ingestion.core.decorators import log_execution


class ObramaxScraper(BaseScraper):

    def __init__(self):
        super().__init__("obramax")
        self.logger = get_logger("obramax")


    @log_execution("obramax")
    def run(self):

        self.logger.info("Iniciando scraper Obramax")

        todos_produtos = []

        for produto in config.PRODUTOS:

            try:
                self.logger.info(f"Coletando: {produto}")

                produtos = self.buscar_produtos(produto)

                todos_produtos.extend(produtos)

                self.logger.info(
                    f"{produto}: {len(produtos)} produtos coletados"
                )

            except Exception as e:
                self.logger.error(
                    f"Erro no produto {produto}: {e}"
                )

        df = pd.DataFrame(todos_produtos)

        if not df.empty:
            df.drop_duplicates(subset=["product_id"], inplace=True)

        self.save("obramax_products.csv", df)

        self.logger.info(f"Finalizado. Total: {len(df)} produtos")


    def buscar_produtos(self, termo: str) -> list[dict]:

        resultados = []
        inicio = 0

        while True:

            params = {
                "ft": termo,
                "_from": inicio,
                "_to": inicio + config.OBRAMAX_PAGE_SIZE - 1
            }

            response = requests.get(
                config.OBRAMAX_BASE_URL,
                params=params,
                timeout=config.REQUEST_TIMEOUT
            )

            if not response.ok:
                self.logger.error(
                    f"HTTP {response.status_code} em {termo}"
                )
                break

            products = response.json()

            if not products:
                break

            for product in products:

                try:
                    resultados.append(
                        self.parse_item(product, termo)
                    )

                except Exception as e:
                    self.logger.error(
                        f"Erro ao processar item: {e}"
                    )

            inicio += config.OBRAMAX_PAGE_SIZE
            self.sleep()

        return resultados


    def parse_item(self, product: dict, termo: str) -> dict:

        item = product["items"][0]

        seller = item["sellers"][0]
        offer = seller.get("commertialOffer", {})

        return self.add_timestamp({
            "source": "obramax",
            "search_term": termo,
            "product_id": product.get("productId"),
            "product_name": product.get("productName"),
            "brand": product.get("brand"),
            "price": offer.get("Price"),
            "list_price": offer.get("ListPrice"),
            "product_url": product.get("link")
        })


if __name__ == "__main__":
    ObramaxScraper().run()