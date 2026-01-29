import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Legacy Story", page_icon="📱", layout="centered")

# --- FUNÇÃO PARA BAIXAR FONTES AUTOMATICAMENTE ---
def garantir_fontes():
    # Links diretos do Google Fonts
    urls = {
        "Roboto-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Bold.ttf",
        "Roboto-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf"
    }
    
    for nome_arquivo, url in urls.items():
        if not os.path.exists(nome_arquivo):
            try:
                r = requests.get(url)
                with open(nome_arquivo, 'wb') as f:
                    f.write(r.content)
            except:
                pass # Se der erro, usaremos a padrão

# Executa o download das fontes ao abrir o app
garantir_fontes()

# --- REGRAS DE NEGÓCIO ---
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
        90000: ([75.00, 330.49, 422.79, 475.70], [75.00, 329.90, 348.00, 410.00]),
        100000:([75.00, 370.59, 487.59, 535.69], [75.00, 389.60, 465.00, 520.00]),
    }
    idx_regiao = 0 if regiao == "Capital" else 1
    valores = None
    for teto, precos in tabela.items():
        if fipe <= teto:
            valores = precos[idx_regiao]
            break
    if not valores: return None
    return [f"R$ {v:.2f}".replace('.', ',') for v in valores]

# --- GERADOR DE IMAGEM 9:16 ---
def criar_proposta_automatica(dados):
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # CORES
    LARANJA = (243, 112, 33) 
    CINZA_ESC = (50, 50, 50)
    CINZA_CLARO = (240, 240, 240)
    BRANCO = (255, 255, 255)
    VERDE = (0, 180, 0)
    VERMELHO = (200, 0, 0)

    # --- FONTES (Agora busca do arquivo baixado) ---
    try:
        font_h1 = ImageFont.truetype("Roboto-Bold.ttf", 80)
        font_h2 = ImageFont.truetype("Roboto-Bold.ttf", 50)
        font_body = ImageFont.truetype("Roboto-Regular.ttf", 40)
        font_bold = ImageFont.truetype("Roboto-Bold.ttf", 40)
        font_small = ImageFont.truetype("Roboto-Regular.ttf", 30)
        font_check = ImageFont.truetype("Roboto-Regular.ttf", 60)
    except:
        font_h1 = font_h2 = font_body = font_bold = font_small = font_check = ImageFont.load_default()

    # 1. CABEÇALHO
    draw.rectangle([(0, 0), (W, 250)], fill=LARANJA)
    
    # Logo
    try:
        logo = Image.open("logo.png")
        if logo.mode != 'RGBA': logo = logo.convert('RGBA')
        ratio = 200 / logo.height
        new_size = (int(logo.width * ratio), 200)
        logo = logo.resize(new_size)
        img.paste(logo, ((W - new_size[0]) // 2, 25), logo)
    except:
        draw.text((W//2 - 200, 80), "LOGO AQUI", font=font_h2, fill=BRANCO)

    # 2. DADOS
