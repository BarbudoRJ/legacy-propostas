import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import urllib.request # Usando biblioteca padrão para não dar erro

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerador Legacy Story", page_icon="📱", layout="centered")

# --- AUTO-DOWNLOAD DE FONTES (SEM DEPENDÊNCIAS EXTRAS) ---
def carregar_fontes():
    # Links diretos para fontes
    fontes = {
        "Roboto-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Bold.ttf",
        "Roboto-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf"
    }
    
    path_bold = "Roboto-Bold.ttf"
    path_reg = "Roboto-Regular.ttf"

    # Baixa se não existir
    for nome, url in fontes.items():
        if not os.path.exists(nome):
            try:
                urllib.request.urlretrieve(url, nome)
            except:
                pass # Se falhar, usa padrão

    try:
        return {
            "h1": ImageFont.truetype(path_bold, 70),
            "h2": ImageFont.truetype(path_bold, 45),
            "body": ImageFont.truetype(path_reg, 35),
            "bold": ImageFont.truetype(path_bold, 35),
            "check": ImageFont.truetype(path_reg, 55)
        }
    except:
        # Fallback (Fonte de emergência se o download falhar)
        p = ImageFont.load_default()
        return {"h1": p, "h2": p, "body": p, "bold": p, "check": p}

FONTES = carregar_fontes()

# --- CÁLCULO MENSALIDADE ---
def calcular_mensalidades(fipe, regiao):
    tabela = {
        10000: ([75.00, 86.60, 110.40, 151.50], [75.00, 80.60, 93.00, 140.69]),
        20000: ([75.00, 110.60, 137.49, 170.49], [75.00, 108.10, 125.00, 167.00]),
        30000: ([75.00, 126.80, 172.69, 202.50], [75.00, 123.60, 141.00, 202.00]),
        40000: ([75.00, 148.50, 202.89, 238.50], [75.00, 146.40, 176.00, 232.00]),
        50000: ([75.00, 180.69, 243.60, 277.60], [75.00, 178.80, 213.00, 273.00]),
        60000: ([75.00, 220.49, 270.59, 332.49], [75.00, 219.90, 240.00, 301.00]),
        70000: ([75.00, 248.79, 322.79, 370.50], [75.00, 246.90, 277.00, 337.00]),
        80000: ([75.00, 290.69, 372.60, 418.60], [75.00, 288.90, 313.00, 373.00]),
        90000: ([75.00, 330.49, 422.79, 475
