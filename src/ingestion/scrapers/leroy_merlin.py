import requests
import pandas as pd
import re
from time import sleep

from ingestion.core import config
from ingestion.core.base_extractor import BaseScraper
from ingestion.core.logger import get_logger
from ingestion.core.decorators import log_execution


class LeroyScraper(BaseScraper):

    def __init__(self):
        super().__init__("leroy")
        self.logger = get_logger("leroy")


    @log_execution("leroy")
    def run(self):

        self.logger.info("Iniciando scraper Leroy Merlin")

        todos_produtos = []

        for produto in config.PRODUTOS:

            try:
                self.logger.info(f"Buscando termo: {produto}")

                produtos = self.buscar_produto(produto)

                todos_produtos.extend(produtos)

                self.logger.info(
                    f"{produto}: {len(produtos)} produtos encontrados"
                )

            except Exception as e:
                self.logger.error(
                    f"Erro ao buscar '{produto}': {e}"
                )

        df = pd.DataFrame(todos_produtos)

        if not df.empty:
            df.drop_duplicates(subset=["product_id"], inplace=True)

        self.save("leroy_products.csv", df)

        self.logger.info(f"Finalizado. Total: {len(df)} produtos")



    def buscar_produto(self, termo: str) -> list[dict]:

        resultados = []
        pagina = 0

        while True:

            payload = {
                "requests": [
                    {
                        "indexName": "production_products",
                        "query": termo,
                        "hitsPerPage": 100,
                        "page": pagina,
                        "analytics": True
                    }
                ]
            }

            response = requests.post(
                config.LEROY_ALGOLIA_URL,
                headers=config.LEROY_HEADERS,
                json=payload,
                timeout=config.REQUEST_TIMEOUT
            )

            response.raise_for_status()

            data = response.json()
            result = data["results"][0]
            hits = result.get("hits", [])

            if not hits:
                break

            self.logger.info(
                f"{termo} | página {pagina} | {len(hits)} produtos"
            )

            for item in hits:

                resultados.append(self.parse_item(item, termo))

            pagina += 1
            sleep(0.5)

        return resultados



    def parse_item(self, item: dict, termo: str) -> dict:

        regiao = (
            item.get("regionalAttributes", {})
            .get("grande_sao_paulo", {})
        )

        marca = item.get("attributes", {}).get("Marca")

        if isinstance(marca, list):
            marca = marca[0] if marca else None

        return self.add_timestamp({
            "source": "leroy",
            "search_term": termo,
            "product_id": self.extrair_product_id(item),
            "product_name": item.get("name"),
            "brand": marca,
            "price": regiao.get("promotionalPrice"),
            "list_price": regiao.get("originalPrice"),
            "product_url": item.get("url")
        })


    def extrair_product_id(self, item: dict) -> str | None:

        product_id = item.get("objectID")

        if product_id:
            return str(product_id)

        url = item.get("url")

        if url:
            match = re.search(r"_(\d+)$", url)

            if match:
                return match.group(1)

        return None


if __name__ == "__main__":
    LeroyScraper().run()