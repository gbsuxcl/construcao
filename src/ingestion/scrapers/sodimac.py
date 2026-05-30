import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


PRODUTOS = [
    "cimento",
    "areia",
    "desmolde",
    "superplastificante",
    "macrofibra"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

PRODUTOS_POR_PAGINA = 48
TEMPO_ESPERA = 5

data = []


for produto in PRODUTOS:

    print("\n" + "=" * 80)
    print(f"Coletando produto: {produto}")
    print("=" * 80)

    pagina = 1

    while True:

        url = (
            "https://www.sodimac.com.br/"
            f"sodimac-br/search?"
            f"Ntt={produto}"
            f"&page={pagina}"
            f"&store=so_retail"
        )

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            search_result = soup.find_all(
                "div",
                class_="search-results-4-grid"
            )

            quantidade_produtos = len(search_result)

            print(
                f"Página {pagina}: "
                f"{quantidade_produtos} produtos"
            )

            # Não encontrou produtos
            if quantidade_produtos == 0:

                print(
                    f"Fim da busca para '{produto}'"
                )

                break

            for result in search_result:

                try:

                    # Link
                    link_tag = result.select_one(
                        "a.pod-link"
                    )

                    product_url = (
                        link_tag.get("href")
                        if link_tag
                        else None
                    )

                    # Nome do produto
                    product_name_tag = result.select_one(
                        "b.pod-subTitle"
                    )

                    product_name = (
                        product_name_tag.get_text(
                            strip=True
                        )
                        if product_name_tag
                        else None
                    )

                    # Marca
                    brand_tag = result.select_one(
                        "b.pod-title"
                    )

                    brand = (
                        brand_tag.get_text(
                            strip=True
                        )
                        if brand_tag
                        else None
                    )

                    # Preço atual
                    price_tag = result.select_one(
                        "span.copy10"
                    )

                    price = (
                        price_tag.get_text(
                            strip=True
                        )
                        if price_tag
                        else None
                    )

                    # Preço riscado
                    list_price_tag = result.select_one(
                        "span.crossed"
                    )

                    list_price = (
                        list_price_tag.get_text(
                            strip=True
                        )
                        if list_price_tag
                        else None
                    )

                    data.append({
                        "source": "sodimac",
                        "search_term": produto,
                        "product_id": None,
                        "product_name": product_name,
                        "brand": brand,
                        "category_id": None,
                        "ean": None,
                        "price": price,
                        "list_price": list_price,
                        "available_quantity": None,
                        "product_url": product_url,
                        "scraping_date": datetime.now()
                    })

                except Exception as e:

                    print(
                        f"Erro ao processar produto: {e}"
                    )

                    continue

            # Última página
            if quantidade_produtos < PRODUTOS_POR_PAGINA:

                print(
                    f"Última página encontrada: {pagina}"
                )

                break

            pagina += 1

            print(
                f"Aguardando {TEMPO_ESPERA}s..."
            )

            time.sleep(TEMPO_ESPERA)

        except Exception as e:

            print(
                f"Erro na página {pagina}: {e}"
            )

            break


df = pd.DataFrame(data)

# Remove duplicados
df = df.drop_duplicates(
    subset=[
        "search_term",
        "product_name",
        "brand",
        "product_url"
    ]
)


os.makedirs(
    "data/output",
    exist_ok=True
)

output_file = (
    "data/output/sodimac_products.csv"
)

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig",
    sep=";",
    decimal="."
)

print("\n" + "=" * 80)
print("Processo finalizado!")
print(f"Produtos coletados: {len(df)}")
print(f"Arquivo salvo em: {output_file}")
print("=" * 80)