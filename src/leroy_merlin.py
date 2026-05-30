import requests
import pandas as pd
import re
from datetime import datetime
from time import sleep
from pathlib import Path


PRODUTOS = [
    "cimento",
    "areia",
    "desmolde",
    "superplastificante",
    "macrofibra"
]

ALGOLIA_URL = "https://1cf3zt43zu-dsn.algolia.net/1/indexes/*/queries"

HEADERS = {
    "x-algolia-api-key": "28e054533dcdd3d71379fc3f38e78f1e",
    "x-algolia-application-id": "1CF3ZT43ZU",
    "Content-Type": "application/json"
}


def extrair_product_id(item: dict) -> str | None:
    """
    Tenta obter o ID do produto.
    Primeiro procura objectID.
    Caso não exista, extrai da URL.
    """

    product_id = item.get("objectID")

    if product_id:
        return str(product_id)

    url = item.get("url")

    if url:
        match = re.search(r"_(\d+)$", url)

        if match:
            return match.group(1)

    return None


def buscar_produto(termo: str) -> list[dict]:

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
            ALGOLIA_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        result = data["results"][0]

        hits = result["hits"]

        if not hits:
            break

        print(
            f"Termo: {termo} | Página: {pagina} | Produtos: {len(hits)}"
        )

        for item in hits:

            regiao = (
                item.get("regionalAttributes", {})
                .get("grande_sao_paulo", {})
            )

            marca = (
                item.get("attributes", {})
                .get("Marca")
            )

            if isinstance(marca, list):
                marca = marca[0] if marca else None

            resultados.append({
                "search_term": termo,
                "product_id": extrair_product_id(item),
                "product_name": item.get("name"),
                "brand": marca,
                "category_id": item.get("categoryPageId"),
                "ean": ",".join(item.get("eans", [])),
                "price": regiao.get("promotionalPrice"),
                "list_price": regiao.get("originalPrice"),
                "available": regiao.get("available"),
                "has_stock": (
                    regiao.get("stock", {})
                    .get("hasStock")
                ),
                "product_url": item.get("url"),
                "scraping_date": datetime.now()
            })

        pagina += 1

        sleep(0.5)

    return resultados


def main():

    todos_produtos = []

    for produto in PRODUTOS:

        try:

            produtos = buscar_produto(produto)

            todos_produtos.extend(produtos)

            print(
                f"{produto}: {len(produtos)} produtos encontrados"
            )

        except Exception as e:

            print(
                f"Erro ao buscar '{produto}': {e}"
            )

    df = pd.DataFrame(todos_produtos)

    if not df.empty:

        df.drop_duplicates(
            subset=["product_id"],
            inplace=True
        )

        # cria a pasta caso não exista
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)

        nome_arquivo = (
            output_dir
            / f"leroy_merlin_products.csv"
        )

        df.to_csv(
            nome_arquivo,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"\nCSV salvo em: {nome_arquivo.resolve()}")
        print(f"Total de produtos: {len(df)}")

    else:

        print("Nenhum produto encontrado.")


if __name__ == "__main__":
    main()
