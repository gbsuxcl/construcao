import os
import time
import requests
import pandas as pd
from datetime import datetime

PRODUTOS = [
    "cimento",
    "areia",
    "desmolde",
    "superplastificante",
    "macrofibra"
]

BASE_URL = "https://www.obramax.com.br/api/catalog_system/pub/products/search"

PAGE_SIZE = 50
SLEEP_SECONDS = 5

data = []

for produto in PRODUTOS:

    print(f"\n{'=' * 80}")
    print(f"Coletando produtos para: {produto}")
    print(f"{'=' * 80}")

    inicio = 0

    while True:

        params = {
            "ft": produto,
            "_from": inicio,
            "_to": inicio + PAGE_SIZE - 1
        }

        try:

            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30
            )

            print(
                f"Requisição: {response.url}"
            )

            if not response.ok:
                print(
                    f"Erro HTTP {response.status_code} "
                    f"para '{produto}'"
                )
                break

            products = response.json()

            if not products:
                print(
                    f"Fim da paginação para '{produto}'"
                )
                break

            print(
                f"Página {inicio}-{inicio + PAGE_SIZE - 1}: "
                f"{len(products)} produtos"
            )

            for product in products:

                try:

                    item = product["items"][0]

                    if not item.get("sellers"):
                        continue

                    seller = item["sellers"][0]
                    offer = seller.get("commertialOffer", {})

                    data.append({
                        "search_term": produto,
                        "product_id": product.get("productId"),
                        "product_name": product.get("productName"),
                        "brand": product.get("brand"),
                        "category_id": product.get("categoryId"),
                        "ean": item.get("ean"),
                        "price": offer.get("Price"),
                        "list_price": offer.get("ListPrice"),
                        "available_quantity": offer.get("AvailableQuantity"),
                        "product_url": product.get("link"),
                        "scraping_date": datetime.now()
                    })

                except (IndexError, KeyError, TypeError) as e:
                    print(
                        f"Erro ao processar produto: {e}"
                    )
                    continue

            inicio += PAGE_SIZE

            print(
                f"Dormindo {SLEEP_SECONDS}s..."
            )

            time.sleep(SLEEP_SECONDS)

        except Exception as e:

            print(
                f"Erro na busca '{produto}': {e}"
            )
            break

df = pd.DataFrame(data)

# Remove duplicados caso o mesmo produto apareça
# em mais de uma busca
if not df.empty:

    df = df.drop_duplicates(
        subset=["product_id"]
    )

os.makedirs(
    "data/output",
    exist_ok=True
)

output_file = "data/output/obramax_products.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig",
    sep=";",
    decimal="."
)

print(f"\n{'=' * 80}")
print("Processo finalizado!")
print(f"Produtos únicos: {len(df)}")
print(f"Arquivo salvo em: {output_file}")
print(f"{'=' * 80}")