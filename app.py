import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerador Legacy Story", page_icon="📱", layout="centered")

# --- FUNÇÃO PARA ÍCONES (Bolinhas Vívidas) ---
def desenhar_icone(draw_obj, x, y, status, font_icon, verde, vermelho, branco, cinza, font_bold):
    if status == "✔":
        raio = 30
        # Bolinha Verde sem transparência
        draw_obj.ellipse([(x-raio, y-raio), (x+raio, y+raio)], fill=verde)
        draw_obj.text((x, y), "✔", font=font_icon, fill=branco, anchor="mm")
    elif status == "✖":
        raio = 30
        # Bolinha Vermelha sem transparência
        draw_obj.ellipse([(x-raio, y-raio), (x+raio, y+raio)], fill=vermelho)
        draw_obj.text((x, y), "✖", font=font_icon, fill=branco, anchor="mm")
    else:
        # Texto Cinza Escuro/Preto
        draw_obj.text((x, y), status, font=font_bold, fill=cinza, anchor="ma")

# --- DESENHO DA IMAGEM ---
def criar_proposta(dados):
    W, H = 1080, 1920
    
    # 1. CARREGAR FUNDO (Original, sem filtros)
    try:
        # Abre o fundo e garante que ele preencha tudo
        bg = Image.open("fundo.jpg").convert("RGBA")
        img = bg.resize((W, H), Image.LANCZOS)
    except:
        # Se não tiver fundo, usa branco puro
        img = Image.new('RGBA', (W, H), color=(255, 255, 255, 255))

    # Criamos o desenhista direto na imagem original
    draw = ImageDraw.Draw(img)

    # --- PALETA DE CORES "SUPER VÍVIDA" (Sem transparência) ---
    LARANJA = (243, 112, 33, 255)
    PRETO = (0, 0, 0, 255)         # Preto total para leitura máxima
    BRANCO = (255, 255, 255, 255)
    VERDE_VIVO = (0, 200, 0, 255)  # Verde forte
    VERMELHO_VIVO = (220, 0, 0, 255) # Vermelho forte
    CINZA_ESCURO = (40, 40, 40, 255) # Quase preto

    # FONTES LOCAIS
    try:
        f_h1 = ImageFont.truetype("bold.ttf", 70)
        f_h2 = ImageFont.truetype("bold.ttf", 45)
        f_body = ImageFont.truetype("regular.ttf", 35)
        f_bold = ImageFont.truetype("bold.ttf", 35)
        f_check = ImageFont.truetype("regular.ttf", 45)
    except:
        f_h1 = f_h2 = f_body = f_bold = f_check = ImageFont.load_default()

    # --- CABEÇALHO ---
    # Tarja Laranja no topo (opcional, se quiser tirar, apague essa linha)
    draw.rectangle([(0, 0), (W, 250)], fill=LARANJA)
    
    try:
        logo = Image.open("logo.png").convert("RGBA")
        ratio = 200 / logo.height
        logo = logo.resize((int(logo.width * ratio), 200))
        # Centraliza logo
        img.paste(logo, ((W - logo.width)//2, 25), logo)
    except:
        draw.text((W//2, 100), "LOGO LEGACY", font=f_h
