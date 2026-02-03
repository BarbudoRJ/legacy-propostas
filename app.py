import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import datetime
import urllib.parse

# =========================
# 1. CONFIGURAÇÕES GERAIS
# =========================
st.set_page_config(page_title="Gerador Legacy Oficial", page_icon="🛡️", layout="centered")

# Definições de Tamanho e Arquivos
W, H = 1080, 1350
BG_PATH = "fundo.png"      # Deve conter logos, rótulos e textos institucionais
FONT_BOLD = "bold.ttf"     # Fonte para valores e títulos
FONT_REG = "regular.ttf"   # Fonte para itens da lista

# =========================
# 2. MAPA DE COORDENADAS (CALIBRAGEM)
# =========================
# Ajuste o 'x' e 'y' para cair exatamente ao lado dos rótulos do seu BG.
POS = {
    # Cabeçalho (Preenchimento de campos)
    "proposta":   {"x": 290, "y": 170, "max_w": 400}, # Ao lado de "PROPOSTA PARA:"
    "data":       {"x": 290, "y": 210, "max_w": 220}, # Ao lado de "DATA:"
    
    "adesao":     {"x": 780, "y": 170, "max_w": 180}, # Ao lado de "ADESÃO R$:"
    "consultor":  {"x": 780, "y": 210, "max_w": 250}, # Ao lado de "CONSULTOR:"
    
    "placa":      {"x": 380, "y": 285, "max_w": 580}, # Ao lado de "PLACA:"
    "modelo_ano": {"x": 380, "y": 325, "max_w": 580}, # Ao lado de "VEÍCULO:"
}

# Área onde a Tabela será desenhada (x0, y0, x1, y1)
# Deve ocupar o espaço em branco entre os dados do carro e o rodapé fixo
TABLE_RECT = (60, 420, 1020, 950) 

# =========================
# 3. FUNÇÕES GRÁFICAS (MOTOR DE DESENHO)
# =========================

def load_fonts():
    """Carrega as fontes ou usa padrão se falhar"""
    try:
        return {
            "val": ImageFont.truetype(FONT_BOLD, 34),       # Valores preenchidos
            "val_sm": ImageFont.truetype(FONT_BOLD, 28),    # Valores secundários
            "head": ImageFont.truetype(FONT_BOLD, 30),      # Cabeçalho Tabela
            "price": ImageFont.truetype(FONT_BOLD, 36),     # Preço Tabela
            "item": ImageFont.truetype(FONT_REG, 28),       # Itens Tabela
            "badge": ImageFont.truetype(FONT_BOLD, 26)      # Badges (200, 10d)
        }
    except:
        d = ImageFont.load_default()
        return {"val": d, "val_sm": d, "head": d, "price": d, "item": d, "badge": d}

def fit_text(draw, x, y, text, font_obj, max_w, fill):
    """Escreve texto reduzindo a fonte se ultrapassar a largura máxima"""
    current_size = getattr(font_obj, "size", 30)
    font = font_obj
    
    # Reduz até caber ou chegar a 18px
    while draw.textbbox((0,0), text, font=font)[2] > max_w and current_size > 18:
        current_size -= 2
        try:
            # Tenta manter o estilo (Bold ou Regular)
            font_file = FONT_BOLD if "bold" in str(font_obj).lower() else FONT_REG
            font = ImageFont.truetype(font_file, current_size)
        except:
            break
            
    # Anchor 'lm' = Left Middle (Alinhado à esquerda, centralizado verticalmente na linha)
    draw.text((x, y), text, font=font, fill=fill, anchor="lm")

def draw_custom_check(draw, cx, cy, status):
    """Desenha ícones vetoriais manuais (Check ou X) sem usar emojis"""
    r = 16 # Raio do círculo
    
    if status == "✔":
        color = (36, 168, 90, 255) # Verde Legacy
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        # Check branco
        points = [(cx-6, cy+1), (cx-1, cy+6), (cx+8, cy-5)]
        draw.line(points[0:2], fill="white", width=3)
        draw.line(points[1:3], fill="white", width=3)
        
    elif status == "✖":
        color = (220, 70, 70, 255) # Vermelho
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        # X branco
        d = 5
        draw.line([(cx-d, cy-d), (cx+d, cy+d)], fill="white", width=3)
        draw.line([(cx+d, cy-d), (cx-d, cy+d)], fill="white", width=3)

def draw_badge(draw, cx, cy, text, font):
    """Desenha pílula cinza para valores numéricos da tabela"""
    w = draw.textbbox((0,0), text, font=font)[2]
    pad_x, pad_y = 16, 6
    x0, y0 = cx - w/2 - pad_x, cy - 14
    x1, y1 = cx + w/2 + pad_x, cy + 14
    
    draw.rounded_rectangle([x0,y0,x1,y1], radius=14, fill=(240,240,240,255), outline=(200,200,200,255), width=1)
    draw.text((cx, cy), text, font=font, fill=(50,50,50,255), anchor="mm")

# =========================
# 4. LÓGICA DE NEGÓCIO
# =========================
BENEFICIOS = [
    ("Rastreamento", ["✔","✔","✔","✔"]),
    ("Reboque",      ["200","400","1mil","1mil"]),
    ("Roubo/Furto",  ["✖","✔","✔","✔"]),
    ("Colisão/PT",   ["✖","✖","✔","✔"]),
    ("Terceiros",    ["✖","✖","✔","✔"]),
    ("Vidros",       ["✖","✖","✔","✔"]),
    ("Carro Res.",   ["✖","✖","10d","30d"]),
    ("Gás (GNV)",    ["✖","✖","✖","✔"]),
]

def calcular_tabela(fipe, regiao):
    # Tabela simplificada para o exemplo
    # [Econ, Basico, Plus, Premium]
    precos_base = {
        10000:  [75.00,  86.60, 110.40, 151.50],
        30000:  [75.00, 126.80, 172.69, 202.50],
        50000:  [75.00, 180.69, 243.60, 277.60],
        70000:  [75.00, 248.79, 322.79, 370.50],
        100000: [75.00, 370.59, 487.59, 535.69],
    }
    
    # Lógica simples de teto para exemplo
    valores = [75.00, 370.59, 487.59, 535.69] # Default (alto)
    for teto, lista in precos_base.items():
        if fipe <= teto:
            valores = lista
            break
            
    # Ajuste regional (Exemplo: Serrana +5%)
    if regiao == "Serrana":
        valores = [v * 1.05 for v in valores]
        
    return [f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in valores]

def gerar_cotacao(dados):
    # 1. Carregar BG
    try:
        bg = Image.open(BG_PATH).convert("RGBA")
        bg = bg.resize((W, H), Image.LANCZOS)
    except:
        return None # Erro tratado no UI

    # 2. Camada de Desenho
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    fonts = load_fonts()
    
    # Cores
    TEXT_COLOR = (255, 255, 255, 255) # Texto sobre o BG escuro/azul
    TABLE_TEXT = (20, 20, 20, 255)    # Texto dentro da tabela clara

    # ---------------------------------------------------------
    # PARTE 1: PREENCHIMENTO DE FORMULÁRIO (Respeitando o BG)
    # ---------------------------------------------------------
    p = POS
    # Cliente
    fit_text(draw, p["proposta"]["x"], p["proposta"]["y"], dados["cliente"], fonts["val"], p["proposta"]["max_w"], TEXT_COLOR)
    # Data
    fit_text(draw, p["data"]["x"], p["data"]["y"], dados["data"], fonts["val_sm"], p["data"]["max_w"], TEXT_COLOR)
    # Adesão (Apenas número)
    fit_text(draw, p["adesao"]["x"], p["adesao"]["y"], dados["adesao"], fonts["val"], p["adesao"]["max_w"], TEXT_COLOR)
    # Consultor
    fit_text(draw, p["consultor"]["x"], p["consultor"]["y"], dados["consultor"], fonts["val_sm"], p["consultor"]["max_w"], TEXT_COLOR)
    # Veículo
    fit_text(draw, p["placa"]["x"], p["placa"]["y"], dados["placa"], fonts["val"], p["placa"]["max_w"], TEXT_COLOR)
    fit_text(draw, p["modelo_ano"]["x"], p["modelo_ano"]["y"], dados["modelo_ano"], fonts["val"], p["modelo_ano"]["max_w"], TEXT_COLOR)

    # ---------------------------------------------------------
    # PARTE 2: TABELA DINÂMICA (Glassmorphism)
    # ---------------------------------------------------------
    tx0, ty0, tx1, ty1 = TABLE_RECT
    
    # Sombra
    draw.rounded_rectangle([tx0+6, ty0+8, tx1+6, ty1+8], radius=25, fill=(0,0,0,60))
    # Vidro (Fundo Branco Translúcido)
    draw.rounded_rectangle([tx0, ty0, tx1, ty1], radius=25, fill=(255,255,255,235), outline=(200,200,200,100), width=1)
    
    # Grid interno
    pad = 20
    ix0, iy0 = tx0 + pad, ty0 + pad
    ix1, iy1 = tx1 - pad, ty1 - pad
    
    cols = ["Econ.", "Básico", "Plus", "Prem."]
    # Largura: Coluna nomes (menor) + 4 colunas iguais
    total_w = ix1 - ix0
    name_col_w = total_w * 0.22 
    data_col_w = (total_w - name_col_w) / 4
    
    # Cabeçalho Laranja
    head_h = 50
    draw.rounded_rectangle([ix0, iy0, ix1, iy0+head_h], radius=12, fill=(243,112,33,255))
    
    # Textos Cabeçalho
    for i, col in enumerate(cols):
        cx = ix0 + name_col_w + (i * data_col_w) + (data_col_w/2)
        draw.text((cx, iy0 + head_h/2), col, font=fonts["head"], fill="white", anchor="mm")
        
    # Preços
    price_y = iy0 + head_h + 10
    price_h = 80
    
    for i, val in enumerate(dados["precos"]):
        cx = ix0 + name_col_w + (i * data_col_w) + (data_col_w/2)
        draw.text((cx, price_y + 25), "R$", font=fonts["val_sm"], fill=TABLE_TEXT, anchor="mm")
        draw.text((cx, price_y + 55), val, font=fonts["price"], fill=TABLE_TEXT, anchor="mm")
        
    # Linha divisória
    line_y = price_y + price_h + 5
    draw.line([(ix0, line_y), (ix1, line_y)], fill=(200,200,200,255), width=2)
    
    # Itens (Loop)
    curr_y = line_y + 25
    row_h = 52 # Altura da linha
    
    for nome, status_list in BENEFICIOS:
        # Nome do benefício
        draw.text((ix0 + 10, curr_y), nome, font=fonts["item"], fill=(80,80,80,255), anchor="lm")
        
        # Ícones
        for i, status in enumerate(status_list):
            cx = ix0 + name_col_w + (i * data_col_w) + (data_col_w/2)
            if status in ["✔", "✖"]:
                draw_custom_check(draw, cx, curr_y, status)
            else:
                draw_badge(draw, cx, curr_y, status, fonts["badge"])
        
        curr_y += row_h
        # Segurança para não desenhar fora do painel
        if curr_y > iy1: break

    # Compõe e retorna
    return Image.alpha_composite(bg, overlay).convert("RGB")

# =========================
# 5. INTERFACE (STREAMLIT)
# =========================
col_logo, col_title = st.columns([1,4])
with col_title:
    st.title("Gerador de Cotação")
    st.caption("Preenchimento Automático sobre Layout Oficial")

# Inputs
c1, c2 = st.columns(2)
cliente = c1.text_input("Nome do Cliente")
consultor = c2.text_input("Nome do Consultor")

c3, c4 = st.columns(2)
whatsapp = c3.text_input("WhatsApp Cliente (com DDD)", placeholder="21999999999")
placa = c4.text_input("Placa", placeholder="ABC-1234")

c5, c6 = st.columns(2)
modelo = c5.text_input("Modelo Veículo", placeholder="Ex: Honda Civic")
ano = c6.text_input("Ano", placeholder="2023")

c7, c8 = st.columns(2)
fipe = c7.number_input("Valor FIPE (R$)", min_value=0.0, step=100.0)
regiao = c8.selectbox("Região", ["Capital", "Serrana"])

adesao = st.text_input("Valor Adesão (Sem R$)", value="300,00")

# Botão Gerar
if st.button("GERAR COTAÇÃO", type="primary"):
    if not cliente or not consultor or fipe == 0:
        st.error("Preencha Cliente, Consultor e FIPE.")
    else:
        # 1. Calcular
        precos = calcular_tabela(fipe, regiao)
        
        # 2. Preparar Dados
        dados_img = {
            "cliente": cliente.upper(),
            "data": datetime.date.today().strftime("%d/%m/%Y"),
            "adesao": adesao,
            "consultor": consultor.upper(),
            "placa": placa.upper() if placa else "---",
            "modelo_ano": f"{modelo.upper()} / {ano}",
            "precos": precos
        }
        
        # 3. Gerar Imagem
        img = gerar_cotacao(dados_img)
        
        if img:
            # Mostrar Prévia
            st.image(img, caption="Prévia Final", use_container_width=True)
            
            # Preparar Download
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()
            
            st.download_button("📥 BAIXAR IMAGEM", img_bytes, file_name=f"Cotacao_{cliente}.png", mime="image/png")
            
            # 4. Botão WhatsApp (Fluxo Gratuito)
            # Cria mensagem de texto + link wa.me
            msg_texto = f"*Cotação Legacy*\n\nCliente: {cliente}\nVeículo: {modelo} ({ano})\nFIPE: R$ {fipe:,.2f}\n\n*Confira a imagem anexa com os planos detalhados.*"
            msg_encoded = urllib.parse.quote(msg_texto)
            
            link_zap = f"https://wa.me/{whatsapp}?text={msg_encoded}" if whatsapp else f"https://wa.me/?text={msg_encoded}"
            
            st.markdown("---")
            st.success("Imagem gerada! Agora envie para o cliente.")
            
            # Botão HTML Verde
            st.markdown(f"""
                <a href="{link_zap}" target="_blank">
                    <button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer; width:100%;">
                        📱 ENVIAR NO WHATSAPP
                    </button>
                </a>
                <p style="text-align:center; font-size:12px; color:gray; margin-top:5px;">
                    Ao abrir o WhatsApp, anexe a imagem que você acabou de baixar.
                </p>
            """, unsafe_allow_html=True)
            
        else:
            st.error("Erro: Imagem de fundo não encontrada.")
