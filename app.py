import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerador Legacy Pro", page_icon="🛡️", layout="centered")

# --- LÓGICA DE NEGÓCIO (Cálculos) ---
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
    idx = 0 if regiao == "Capital" else 1
    for teto, precos in tabela.items():
        if fipe <= teto: return [f"R$ {v:.2f}".replace('.', ',') for v in precos[idx]]
    return None

# --- MOTOR DE DESENHO (SUA VERSÃO OTIMIZADA) ---
def criar_proposta(dados):
    # DIMENSÕES
    W, H = 1080, 1350

    # FUNDO
    try:
        bg = Image.open("fundo.png").convert("RGBA")
        # Ajuste inteligente: Resize mantendo proporção (Crop) ou esticando? 
        # Como seu código usou resize direto, mantive, mas o ideal para fundo.png é garantir que seja 1080x1350
        bg = bg.resize((W, H), Image.LANCZOS)  
        img = bg.copy()
    except:
        img = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    # CORES
    LARANJA     = (243, 112, 33, 255)
    AZUL_LEGACY = (0, 35, 95, 255)
    PRETO       = (15, 15, 15, 255)
    CINZA_TEXTO = (85, 85, 85, 255)
    VERDE       = (0, 170, 0, 255)
    VERMELHO    = (200, 0, 0, 255)

    # FONTES
    try:
        f_titulo      = ImageFont.truetype("bold.ttf", 46)   # FIPE (mais contido)
        f_subtitulo   = ImageFont.truetype("bold.ttf", 34)   # Modelo
        f_texto       = ImageFont.truetype("regular.ttf", 28) # labels
        f_negrito     = ImageFont.truetype("bold.ttf", 28)
        f_tabela_head = ImageFont.truetype("bold.ttf", 26)
        f_tabela_val  = ImageFont.truetype("bold.ttf", 32)
        f_aviso       = ImageFont.truetype("regular.ttf", 22)
        f_check       = ImageFont.truetype("bold.ttf", 30)
        f_small       = ImageFont.truetype("regular.ttf", 24)
    except:
        f_titulo = f_subtitulo = f_texto = f_negrito = f_tabela_head = f_tabela_val = f_aviso = f_check = f_small = ImageFont.load_default()

    # =========================================================
    # DIAGRAMAÇÃO / POSIÇÕES FIXAS (1080x1350)
    # =========================================================
    MARGEM_X = 70
    CENTRO_X = W // 2

    # ZONAS (baseadas no seu fundo)
    TOPO_Y0       = 170    # começa abaixo do logo
    # TOPO_Y_MAX    = 520    # (Referência visual apenas)
    # VEIC_Y0       = 520    # (Referência visual apenas)
    BASE_Y0       = 860    # começa a tabela/benefícios
    RODAPE_Y      = 1290   # mensagens finais

    # Painel translúcido pra leitura (tabela + benefícios)
    PAINEL_X0 = 45
    PAINEL_X1 = W - 45
    PAINEL_Y0 = BASE_Y0 - 20
    PAINEL_Y1 = H - 70
    # =========================================================

    # --- 1) HEADER (TOPO) ---
    y = TOPO_Y0

    # Linha 1: Proposta para
    draw.text((MARGEM_X, y), "Proposta para:", font=f_texto, fill=CINZA_TEXTO)
    draw.text((MARGEM_X + 215, y), dados["cliente"], font=f_negrito, fill=AZUL_LEGACY)
    y += 42

    # Linha 2: Consultor
    draw.text((MARGEM_X, y), f"Consultor(a): {dados['consultor']}", font=f_negrito, fill=LARANJA)
    y += 52

    # Divisor
    draw.line([(MARGEM_X, y), (W - MARGEM
