PRODUTOS = [
    "cimento",
    "areia",
    "desmolde",
    "superplastificante",
    "macrofibra"
]

REQUEST_TIMEOUT = 30
SLEEP_SECONDS = 5

OUTPUT_DIR = "data\output"
DATE_FIELD = "scraping_date"

# JOLI
JOLI_BASE_URL = "https://www.joli.com.br/api/catalog_system/pub/products/search"
JOLI_PAGE_SIZE = 50


# OBRAMAX
OBRAMAX_BASE_URL = "https://www.obramax.com.br/api/catalog_system/pub/products/search"
OBRAMAX_PAGE_SIZE = 50


# LEROY
LEROY_ALGOLIA_URL = "https://1cf3zt43zu-dsn.algolia.net/1/indexes/*/queries"

LEROY_HEADERS = {
    "x-algolia-api-key": "28e054533dcdd3d71379fc3f38e78f1e",
    "x-algolia-application-id": "1CF3ZT43ZU",
    "Content-Type": "application/json"
}


# SODIMAC
SODIMAC_BASE_URL = "https://www.sodimac.com.br/sodimac-br/search"

SODIMAC_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

SODIMAC_PAGE_SIZE = 48
SODIMAC_SLEEP_SECONDS = 5