import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep

from ingestion.core import config
from ingestion.core.base_extractor import BaseScraper
from ingestion.core.logger import get_logger
from ingestion.core.decorators import log_execution


class SodimacScraper(BaseScraper):

    def __init__(self):
        super().__init__("sodimac")
        self.logger = get_logger("sodimac")

    @log_execution("sodimac")
    def run(self):

        self.logger.info("Iniciando Sodimac scraper")

        all_data = []

        for produto in config.PRODUTOS:

            self.logger.info(f"Coletando: {produto}")

            data = self.buscar_produto(produto)

            all_data.extend(data)

            self.logger.info(f"{produto}: {len(data)} produtos coletados")

        df = pd.DataFrame(all_data)

        if not df.empty:
            df.drop_duplicates(
                subset=["search_term", "product_name", "brand", "product_url"],
                inplace=True
            )

        self.save("sodimac_products.csv", df)

        self.logger.info(f"Finalizado. Total: {len(df)}")

    def buscar_produto(self, produto: str):

        results = []
        page = 1

        while True:

            url = (
                f"{config.SODIMAC_BASE_URL}"
                f"?Ntt={produto}"
                f"&page={page}"
                f"&store=so_retail"
            )

            try:
                response = requests.get(
                    url,
                    headers=config.SODIMAC_HEADERS,
                    timeout=config.REQUEST_TIMEOUT
                )

                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                items = soup.find_all("div", class_="search-results-4-grid")

                if not items:
                    break

                self.logger.info(
                    f"{produto} | página {page} | {len(items)} itens"
                )

                for item in items:
                    results.append(self.parse_item(item, produto))

                if len(items) < config.SODIMAC_PAGE_SIZE:
                    break

                page += 1
                sleep(config.SODIMAC_SLEEP_SECONDS)

            except Exception as e:
                self.logger.error(f"Erro na página {page}: {e}")
                break

        return results

    def parse_item(self, item, produto: str):

        link = item.select_one("a.pod-link")
        name = item.select_one("b.pod-subTitle")
        brand = item.select_one("b.pod-title")
        price = item.select_one("span.copy10")
        list_price = item.select_one("span.crossed")

        return self.add_timestamp({
            "source": "sodimac",
            "search_term": produto,
            "product_id": None,
            "product_name": name.get_text(strip=True) if name else None,
            "brand": brand.get_text(strip=True) if brand else None,
            "price": price.get_text(strip=True) if price else None,
            "list_price": list_price.get_text(strip=True) if list_price else None,
            "product_url": link.get("href") if link else None
        })


if __name__ == "__main__":
    SodimacScraper().run()