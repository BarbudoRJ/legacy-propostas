import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import math
from datetime import datetime

st.set_page_config(page_title="Gerador Cotação Legacy", page_icon="📝", layout="centered")

# =========================
# CONFIG VISUAL (AJUSTE AQUI)
# =========================
W, H = 1080, 1350

# Área-alvo da TABELA (onde ela pode existir sem invadir BG/veículos)
# Ajuste fino aqui se precisar (DEBUG mostra o retângulo)
TABLE_BOX = (70, 520, 1010, 980)  # (x1, y1, x2, y2)

# Área-alvo dos campos do TOPO (preencher apenas os valores, não os rótulos)
# Esses pontos assumem que o BG tem rótulos fixos e espaço ao lado/dentro.
FIELDS = {
    "proposta_para":  (260, 275),  # valor ao lado de "PROPOSTA PARA:"
    "data":           (260, 305),  # valor ao lado de "DATA:"
    "adesao":         (720, 275),  # valor ao lado de "ADESÃO: R$"
    "consultor":      (720, 305),  # valor ao lado de "CONSULTOR:"
    "placa":          (190, 410),  # valor ao lado de "PLACA:"
    "modelo_ano":     (310, 470),  # valor ao lado de "MODELO/ANO:"
}

# =========================
# FONTES
# =========================
def load_fonts():
    try:
        # Troque pelos nomes reais se você tiver arquivos de fonte
        f_regular = ImageFont.truetype("regular.ttf", 32)
        f_bold    = ImageFont.truetype("bold.ttf", 34)
        f_italic  = ImageFont.truetype("italic.ttf", 34)
        f_small   = ImageFont.truetype("regular.ttf", 24)
        return f_regular, f_bold, f_italic, f_small
    except:
        d = ImageFont.load_default()
        return d, d, d, d

F_REG, F_BOLD, F_ITAL, F_SMALL = load_fonts()

# =========================
# CORES
# =========================
AZUL = (22, 42, 63, 255)
LARANJA = (243, 112, 33, 255)
PRETO = (25, 25, 25, 255)
BRANCO = (255, 255, 255, 255)
CINZA_TXT = (90, 90, 90, 255)

# =========================
# HELPERS DE TEXTO
# =========================
def fit_text(draw, text, max_width, font_path=None, start_size=36, min_size=18, bold=False):
    # Ajusta tamanho até caber
    size = start_size
    while size >= min_size:
        try:
            font = ImageFont.truetype("bold.ttf" if bold else "regular.ttf", size)
        except:
            font = ImageFont.load_default()
        w = draw.textlength(text, font=font)
        if w <= max_width:
            return font
        size -= 1
    return font

def brl(v):
    # v float -> "1.234,56"
    s = f"{v:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# ÍCONES BONITOS (DESENHADOS)
# =========================
def draw_check(draw, cx, cy, r=16):
    # círculo verde + check branco
    green = (33, 163, 102, 255)
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=green)
    # check
    x1, y1 = cx - r*0.35, cy + r*0.05
    x2, y2 = cx - r*0.10, cy + r*0.30
    x3, y3 = cx + r*0.40, cy - r*0.25
    draw.line((x1,y1,x2,y2), fill=BRANCO, width=4)
    draw.line((x2,y2,x3,y3), fill=BRANCO, width=4)

def draw_x(draw, cx, cy, r=16):
    # círculo vermelho + X branco
    red = (214, 68, 68, 255)
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=red)
    d = r*0.35
    draw.line((cx-d, cy-d, cx+d, cy+d), fill=BRANCO, width=4)
    draw.line((cx-d, cy+d, cx+d, cy-d), fill=BRANCO, width=4)

def draw_pill(draw, x, y, w, h, text, font):
    # pílula cinza clara com texto
    fill = (245, 245, 245, 235)
    outline = (215, 215, 215, 255)
    r = h // 2
    draw.rounded_rectangle((x, y, x+w, y+h), radius=r, fill=fill, outline=outline, width=2)
    tw = draw.textlength(text, font=font)
    draw.text((x + w/2 - tw/2, y + (h - font.size)/2 - 2), text, font=font, fill=PRETO)

# =========================
# TABELA (AREA-ALVO)
# =========================
def draw_table_on_box(img, precos, itens, box, debug=False):
    x1, y1, x2, y2 = box
    draw = ImageDraw.Draw(img, "RGBA")

    # Painel glass/esquelomorfo
    panel_fill = (255, 255, 255, 210)
    panel_outline = (210, 210, 210, 255)
    shadow = (0, 0, 0, 35)

    # sombra leve
    draw.rounded_rectangle((x1+8, y1+10, x2+8, y2+10), radius=28, fill=shadow)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=28, fill=panel_fill, outline=panel_outline, width=2)

    if debug:
        # borda de debug em vermelho
        draw.rectangle((x1, y1, x2, y2), outline=(255, 0, 0, 255), width=2)

    # Métricas internas
    pad = 26
    inner_x1, inner_y1 = x1 + pad, y1 + pad
    inner_x2, inner_y2 = x2 - pad, y2 - pad
    inner_w = inner_x2 - inner_x1

    # Colunas
    col_names = ["Econ.", "Básico", "Plus", "Prem."]
    label_col_w = int(inner_w * 0.34)     # coluna de benefícios
    plans_w = inner_w - label_col_w
    col_w = plans_w / 4

    # Cabeçalho laranja
    header_h = 64
    header_y1 = inner_y1
    header_y2 = header_y1 + header_h
    draw.rounded_rectangle((inner_x1, header_y1, inner_x2, header_y2), radius=18, fill=LARANJA)

    # Títulos das colunas (itálico)
    # Centraliza nas 4 colunas de planos
    for i, name in enumerate(col_names):
        cx = inner_x1 + label_col_w + (i + 0.5) * col_w
        tw = draw.textlength(name, font=F_ITAL)
        draw.text((cx - tw/2, header_y1 + 14), name, font=F_ITAL, fill=BRANCO)

    # Linha separadora pós-header
    y = header_y2 + 14
    draw.line((inner_x1, y, inner_x2, y), fill=(190, 190, 190, 255), width=2)
    y += 10

    # Linha de preços (1 linha dedicada)
    prices_block_h = 96
    prices_y1 = y
    prices_y2 = prices_y1 + prices_block_h

    # "R$" pequeno acima + valor grande
    for i, p in enumerate(precos):
        cx = inner_x1 + label_col_w + (i + 0.5) * col_w
        draw.text((cx - 10, prices_y1 + 4), "R$", font=F_SMALL, fill=PRETO)
        # valor
        font_val = fit_text(draw, p.replace("R$ ", ""), max_width=col_w-10, start_size=44, min_size=28, bold=True)
        tw = draw.textlength(p.replace("R$ ", ""), font=font_val)
        draw.text((cx - tw/2, prices_y1 + 30), p.replace("R$ ", ""), font=font_val, fill=PRETO)

    y = prices_y2 + 12
    draw.line((inner_x1, y, inner_x2, y), fill=(190, 190, 190, 255), width=2)
    y += 12

    # Agora vem o grid de benefícios, auto-ajustado no que sobrou
    available_h = inner_y2 - y
    n = len(itens)
    row_h = available_h / n

    # Proteção: se ficar muito apertado, reduz fonte do rótulo
    label_font = F_ITAL
    if row_h < 48:
        label_font = ImageFont.truetype("italic.ttf", 28) if hasattr(F_ITAL, "size") else F_ITAL
    if row_h < 40:
        label_font = ImageFont.truetype("italic.ttf", 24) if hasattr(F_ITAL, "size") else F_ITAL

    # Render das linhas
    for r, (nome, status_lista) in enumerate(itens):
        ry = y + r * row_h
        cy = ry + row_h / 2

        # Nome do benefício
        # Ajusta para não estourar a coluna
        max_label_w = label_col_w - 10
        f_label = fit_text(draw, nome, max_label_w, start_size=30, min_size=20, bold=False)
        draw.text((inner_x1, cy - f_label.size/2 - 2), nome, font=f_label, fill=CINZA_TXT)

        # Conteúdo nas colunas
        for i, status in enumerate(status_lista):
            cx = inner_x1 + label_col_w + (i + 0.5) * col_w

            if status == "✔":
                draw_check(draw, cx, cy, r=15)
            elif status == "✖":
                draw_x(draw, cx, cy, r=15)
            else:
                # texto em pílula
                txt = str(status)
                # dimensiona pill conforme conteúdo
                pill_h = 34
                pill_w = max(68, int(draw.textlength(txt, font=F_ITAL) + 28))
                draw_pill(draw, cx - pill_w/2, cy - pill_h/2, pill_w, pill_h, txt, F_ITAL)

    return img

# =========================
# MENSALIDADES (SEU MAPA)
# =========================
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
        if fipe <= teto:
            return [f"R$ {brl(v)}" for v in precos[idx]]
    return None

# =========================
# CRIAR IMAGEM (BG FIXO + VALORES + TABELA)
# =========================
def criar_cotacao(bg_path, dados, precos, debug=False):
    bg = Image.open(bg_path).convert("RGBA")
    bg = bg.resize((W, H), Image.LANCZOS)
    img = bg.copy()
    draw = ImageDraw.Draw(img, "RGBA")

    # 1) Preencher valores (sem recriar rótulos)
    # Ajuste automático de fonte por largura de campo (aproximação)
    # Definimos larguras máximas conservadoras por campo:
    maxw = {
        "proposta_para": 360,
        "data": 260,
        "adesao": 220,
        "consultor": 280,
        "placa": 780,
        "modelo_ano": 760
    }

    for k, (x, y) in FIELDS.items():
        text = dados.get(k, "")
        if not text:
            continue

        # estilo do topo: branco
        # (se você quiser outro, muda aqui)
        font = fit_text(draw, text, maxw.get(k, 300), start_size=44 if k in ["placa", "modelo_ano"] else 34, min_size=20, bold=False)
        draw.text((x, y), text, font=font, fill=BRANCO)

    # 2) Itens da tabela (com Incêndio e Clube Certo)
    itens = [
        ("Rastreamento", ["✔", "✔", "✔", "✔"]),
        ("Reboque", ["200", "400", "1mil", "1mil"]),
        ("Roubo/Furto", ["✖", "✔", "✔", "✔"]),
        ("Colisão/PT", ["✖", "✖", "✔", "✔"]),
        ("Incêndio", ["✖", "✖", "✔", "✔"]),       # CONFIRMADO POR VOCÊ
        ("Terceiros", ["✖", "✖", "✔", "✔"]),
        ("Vidros", ["✖", "✖", "✔", "✔"]),
        ("Carro Res.", ["✖", "✖", "10d", "30d"]),
        ("Gás (GNV)", ["✖", "✖", "✖", "✔"]),
        ("Clube Certo", ["✖", "✔", "✔", "✔"]),    # BÁSICO AO PREMIUM
    ]

    # 3) Desenhar tabela na área-alvo
    img = draw_table_on_box(img, precos, itens, TABLE_BOX, debug=debug)

    return img.convert("RGB")

# =========================
# UI STREAMLIT
# =========================
st.title("📝 Gerador de Cotação Legacy (BG fixo)")

bg_path = "fundo.png"  # mantenha o nome do arquivo do BG no ambiente

with st.expander("⚙️ Opções de ajuste", expanded=False):
    debug = st.checkbox("DEBUG: mostrar área-alvo da tabela", value=False)
    regiao = st.selectbox("Região", ["Capital", "Serrana"])
else:
    debug = False
    regiao = "Capital"

c1, c2 = st.columns(2)
proposta_para = c1.text_input("Proposta para (valor)")
data = c2.text_input("Data (valor)", value=datetime.now().strftime("%d/%m/%Y"))

c3, c4 = st.columns(2)
adesao = c3.text_input("Adesão (somente número, ex: 300,00)")
consultor = c4.text_input("Consultor (valor)")

c5, c6 = st.columns(2)
placa = c5.text_input("Placa (valor)")
modelo_ano = c6.text_input("Modelo/Ano (valor)", placeholder="Ex: RENEGADE / 2024")

fipe = st.number_input("Valor FIPE", step=100.0, min_value=0.0)

if st.button("GERAR COTAÇÃO", type="primary"):
    if fipe <= 0:
        st.warning("Informe um valor FIPE válido.")
    else:
        precos = calcular_mensalidades(fipe, regiao)
        if not precos:
            st.error("FIPE acima do limite da tabela.")
        else:
            dados = {
                "proposta_para": proposta_para.strip(),
                "data": data.strip(),
                "adesao": adesao.strip(),
                "consultor": consultor.strip(),
                "placa": placa.strip(),
                "modelo_ano": modelo_ano.strip(),
            }

            img = criar_cotacao(bg_path, dados, precos, debug=debug)
            st.image(img, caption="Cotação gerada", width=420)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            png_bytes = buf.getvalue()

            st.download_button(
                "📥 BAIXAR IMAGEM",
                data=png_bytes,
                file_name=f"Cotacao_{proposta_para or 'cliente'}.png",
                mime="image/png"
            )
