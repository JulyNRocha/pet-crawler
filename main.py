from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

def configurar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--log-level=3')
    options.add_argument('--enable-unsafe-swiftshader')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    return driver

def capturar_dados(url, driver):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    dados = []

    for item in soup.find_all('a', class_='listaAnimal'):
        nome = item.find('b').get_text(strip=True)

        porte_sexo_elem = item.find(string=lambda string: "|" in string and "ano" not in string)
        porte_sexo = porte_sexo_elem.strip() if porte_sexo_elem else ""

        idade_elem = item.find(string=lambda string: "ano" in string or "meses" in string)
        idade = idade_elem.strip() if idade_elem else ""

        dados.append({
            "nome": nome,
            "porte_sexo": porte_sexo,
            "idade": idade
        })

    return dados

def salvar_dados_completo(dados_completo):
    data_atual = datetime.now().strftime('%Y-%m-%d')
    nome_arquivo = f"{data_atual}.json"

    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        json.dump(dados_completo, arquivo, ensure_ascii=False, indent=4)

def rotina_de_captura(url_base, intervalo=3600):
    driver = configurar_driver()
    dados_completo = []

    try:
        while True:
            page_number = 1
            last_data = None
            nova_captura = False

            while True:
                url = f"{url_base}?p={page_number}"
                print(f"Acessando: {url}")
                dados = capturar_dados(url, driver)

                if dados == last_data:
                    print(f"Página {page_number} é igual à anterior. Última página disponível: {page_number - 1}")
                    break

                dados_completo.extend(dados)
                last_data = dados
                page_number += 1
                nova_captura = True

            salvar_dados_completo(dados_completo)

            if nova_captura:
                print(f"Captura completa. Esperando {intervalo/3600} hora(s) para próxima execução.")
                time.sleep(intervalo)
            else:
                print("Nenhuma nova página encontrada. Tentando novamente em breve.")
                time.sleep(300)

    finally:
        driver.quit()

url_base = "https://adotar.com.br/adocao-de-animais/gato/vitoria-es"
rotina_de_captura(url_base)
