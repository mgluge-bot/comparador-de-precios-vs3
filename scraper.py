import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json

productos = [
    {
        "nombre": "Nivea Sun Tono Medio",
        "farmacity": "https://www.farmacity.com/protector-solar-nivea-sun-tono-medio-fps-50-x-40-ml/p",
        "farmaplus": "https://www.farmaplus.com.ar/protector-solar-facial-nivea-sun-ultra-light-daily-fluid-tono-medio-fps-50--para-todo-tipo-de-piel-x-40-ml/p",
        "Selma": "https://selmadigital.com/p/protector-solar-facial-nivea-sun-ultra-light-daily-fluid-tono-medio-fps50-40-ml/8118c7f9-6892-47e5-ac4e-0fa1af236362"
    },
    {
        "nombre": "Vichy Capital Soleil",
        "farmacity": "https://www.farmacity.com/aceite-solar-invisible-vichy-capital-soleil-cell-protect-spf-50-x-200-ml/p",
        "farmaplus": "https://www.farmaplus.com.ar/vichy-capital-soleil-oil-invisible-cell-protect-spf50-200ml/p",
        "Selma": "https://selmadigital.com/p/capital-solei-fps-50-cell-protect-spray-x-200-ml/4096eb08-cf6c-47e0-a812-0a59ed6a4104"
    },
    {
        "nombre": "Caviahue Contorno de Ojos",
        "farmacity": "https://www.farmacity.com/contorno-de-ojos-caviahue-vitamina-k3-x-15-g/p",
        "farmaplus": "https://www.farmaplus.com.ar/caviahue-contorno-de-ojos-con-vitamina-k3-15-gr-barr/p",
        "Selma": "https://selmadigital.com/p/contorno-de-ojos-vitamina-k3-crema-x-15-gramos/64ec1ceb-cf50-4250-9f39-a217abb608a1"
    },
    {
        "nombre": "Maybelline Rubor Líquido Face Sunkisser",
        "farmacity": "https://www.farmacity.com/rubor-liquido-maybelline-sunkisser-mate-x-4-7-ml/p",
        "farmaplus": "https://www.farmaplus.com.ar/maybelline-rubor-liquido-sunkisser-matte-blush/p",
        "Selma": None
    },
    {
        "nombre": "Isdin Fusion Water Magic",
        "farmacity": "https://www.farmacity.com/protector-solar-facial-isdin-fotoprotector-fusion-water-magic-x-50-ml/p",
        "farmaplus": "https://www.farmaplus.com.ar/isdin-fusion-water-magic-fotoprotector-solar-fps50-50ml/p",
        "Selma": "https://selmadigital.com/p/fotoprotector-spf50-fusion-water-magic-50ml/10c1444c-bf32-431f-b1f9-517d5a300bcb"
    },
    {
        "nombre": "102 Magnesio Citrato Vitaminas Y Minerales Gummies 90 Unidades",
        "farmacity": "https://www.farmacity.com/magnesio-102-gummies-x-90/p",
        "farmaplus": "https://www.farmaplus.com.ar/102-magnesio-citrato-vitaminas-y-minerales-gummies-90-uds/p",
        "Selma": "https://selmadigital.com/p/102-magnesio-gummies-x90-gomitas/64339877-0c71-43b8-ac2a-81ac7594cbb4"
    }

]

headers = {
    "User-Agent": "Mozilla/5.0"
}
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 15)

def precio_farmacity(url):
    try:
        driver.get(url)
        precio = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".vtex-product-price-1-x-sellingPriceValue")
            )
        )
        return precio.text, "NA"
    except:
        return "NA", "NA"

def precio_farmaplus(url):
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        texto = soup.get_text()
        precios = re.findall(r"\$\s?[\d\.]+", texto)
        precio = precios[0] if len(precios) > 0 else "NA"
        lista = precios[1] if len(precios) > 1 else "NA"
        return precio, lista
    except:
        return "NA", "NA"


def precio_selma(url):

    if url is None:
        return "NA", "NA"
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        # buscar precio visible
        texto = soup.get_text()
        precios = re.findall(r"\$\s?[\d\.]+", texto)
        precio = precios[0] if len(precios) > 0 else "NA"
        lista = precios[1] if len(precios) > 1 else "NA"
        return precio, lista
    except:
        return "NA", "NA"


data = []

for p in productos:

    pf, lf = precio_farmacity(p["farmacity"])
    pp, lp = precio_farmaplus(p["farmaplus"])
    ps, ls = precio_selma(p.get("selma"))
    
    data.append({
        "fecha": datetime.date.today(),
        "producto": p["nombre"],
        "precio_farmacity": pf,
        "lista_farmacity": lf,
        "precio_farmaplus": pp,
        "lista_farmaplus": lp,
        "precio_selma": ps,
        "lista_selma": ls
        
    })

driver.quit()

df = pd.DataFrame(data)

df.to_csv("precios.csv", mode="a", index=False, header=not pd.io.common.file_exists("precios.csv"))
