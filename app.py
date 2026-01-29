import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Proposta Legacy", page_icon="🧡", layout="centered")

# --- 2. DADOS E REGRAS DE NEGÓCIO ---
def calcular_mensalidades(fipe, regiao):
    # Tabela de Preços (Capital vs Serrana)
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
            
    if not valores:
        return None 
    
    return [f"R$ {v:.2f}".replace('.', ',') for v in valores]

# --- 3. FUNÇÃO DE DESENHO NA IMAGEM ---
def gerar_imagem(dados, template_path="TAMPLATE PROPOSTA.jpg"): 
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # --- CORREÇÃO DAS FONTES (USANDO FONTE DO SISTEMA LINUX) ---
    try:
        # Tenta pegar a fonte DejaVuSans que existe no servidor
        path_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        path_font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        font_padrao = ImageFont.truetype(path_font, 28) 
        font_bold = ImageFont.truetype(path_font_bold, 28)
        font_grid = ImageFont.truetype(path_font_bold, 24) 
        font_check = ImageFont.truetype(path_font, 40)
        font_small_bold = ImageFont.truetype(path_font_bold, 20)
    except:
        # Se der erro, tenta carregar Arial local ou fallback
        try:
            font_padrao = ImageFont.truetype("arial.ttf", 28)
            font_bold = ImageFont.truetype("arialbd.ttf", 28)
            font_grid = ImageFont.truetype("arialbd.ttf", 24)
            font_check = ImageFont.