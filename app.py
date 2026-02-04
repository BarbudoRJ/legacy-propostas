import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import datetime
import urllib.parse

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Gerador de Cotação Legacy", page_icon="📝", layout="centered")

W, H = 1080, 1350
BG_PATH = "fundo.png"   # coloque seu BG fixo com esse nome na mesma pasta do app

# ✅ Área-alvo fixa da tabela (x1, y1, x2, y2)
# Ajuste fino depois se quiser (+/- 10px), mas essa base já resolve o “bagunçado”
TABLE_BOX = (60, 600, 1020, 1265)

# Paleta
LARANJA = (243, 112, 33, 255)
AZUL = (0, 35, 95, 255)
PRETO = (25, 25, 25, 255)
CINZA_TXT = (90, 90, 90, 255)
BRANCO = (255, 255, 255, 255)

VERDE = (25, 160, 90, 255)
VERMELHO = (210, 70, 70, 255)

# =========================================================
# FONT LOADER
# =========================================================
def load_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# Ajuste os nomes dos seus arquivos de fonte se necessário
F_BOLD = "bold.ttf"
F_REG  = "regular.ttf"

f_title    = load_font(F_BOLD, 54)
f_sub      = load_font(F_BOLD, 38)
f_label    = load_font(F_REG,  26)   # ✅ menor pra caber +2 linhas
f_small    = load_font(F_REG,  22)
f_plan     = load_font(F_BOLD, 30)
f_price    = load_font(F_BOLD, 44)
f_icon_txt = load_font(F_BOLD, 22)
f_footer   = load_font(F_BOLD, 24)
f_footer2  = load_font(F_REG,  20)

# =========================================================
# HELPERS - SHAPES / ICONS
# =========================================================
def draw_rounded_rect(img, box, radius, fill, outline=None, outline_w=1):
    """Draw rounded rectangle onto RGBA image."""
    x1, y1, x2, y2 = box
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)

    # PIL >=8 supports rounded_rectangle
    d.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=outline_w)
    img.alpha_composite(overlay)

def drop_shadow(img, box, radius=22, shadow_offset=(10,10), shadow_blur=18, shadow_alpha=120):
    """Soft shadow behind a rounded rect."""
    x1, y1, x2, y2 = box
    shadow = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(shadow)
    ox, oy = shadow_offset

    d.rounded_rectangle([x1+ox, y1+oy, x2+ox, y2+oy], radius=radius, fill=(0,0,0,shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    img.alpha_composite(shadow)

def draw_check_icon(draw, cx, cy, r=14):
    """Skeuomorph-ish green circle with white check."""
    # base circle
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=VERDE)
    # subtle highlight
    draw.ellipse([cx-r+3, cy-r+3, cx+r-5, cy+r-5], fill=(255,255,255,35))
    # check
    # simple polyline
    draw.line([(cx - r*0.45, cy + r*0.05),
               (cx - r*0.10, cy + r*0.35),
               (cx + r*0.55, cy - r*0.35)], fill=BRANCO, width=4, joint="curve")

def draw_x_icon(draw, cx, cy, r=14):
    """Skeuomorph-ish red circle with white X."""
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=VERMELHO)
    draw.ellipse([cx-r+3, cy-r+3, cx+r-5, cy+r-5], fill=(255,255,255,35))
    draw.line([(cx-r*0.40, cy-r*0.40), (cx+r*0.40, cy+r*0.40)], fill=BRANCO, width=4)
    draw.line([(cx+r*0.40, cy-r*0.40), (cx-r*0.40, cy+r*0.40)], fill=BRANCO, width=4)

def draw_pill(draw, cx, cy, text, font, fill=(245,245,245,255), outline=(210,210,210,255)):
    """Rounded pill behind small value (ex: 200, 10d)."""
    w = int(draw.textlength(text, font=font))
    pad_x, pad_y = 14, 8
    x1 = cx - (w//2) - pad_x
    y1 = cy - (font.size//2) - pad_y
    x2 = cx + (w//2) + pad_x
    y2 = cy + (font.size//2) + pad_y
    draw.rounded_rectangle([x1,y1,x2,y2], radius=18, fill=fill, outline=outline, width=1)
    draw.text((cx, cy), text, font=font, fill=PRETO, anchor="mm")

def draw_status(draw, cx, cy, status):
    """status: 'check'|'x' or string value."""
    if status == "check":
        draw_check_icon(draw, cx, cy, r=14)
    elif status == "x":
        draw_x_icon(draw, cx, cy, r=14)
    else:
        # numeric/duration → pill
        draw_pill(draw, cx, cy, str(status), font=f_icon_txt)

# =========================================================
# PRICE TABLES (do seu JSON)
# =========================================================
TABELAS = {
    "carro_capital": [
        (0, 10000,  [75.00,  86.60, 110.40, 151.50]),
        (10001,20000,[75.00, 110.60, 137.49, 170.49]),
        (20001,30000,[75.00, 126.80, 172.69, 202.50]),
        (30001,40000,[75.00, 148.50, 202.89, 238.50]),
        (40001,50000,[75.00, 180.69, 243.60, 277.60]),
        (50001,60000,[75.00, 220.49, 270.59, 332.49]),
        (60001,70000,[75.00, 248.79, 322.79, 370.50]),
        (70001,80000,[75.00, 290.69, 372.60, 418.60]),
        (80001,90000,[75.00, 330.49, 422.79, 475.70]),
        (90001,100000,[75.00,370.59, 487.59, 535.69]),
    ],
    "carro_serrana": [
        (0, 10000,  [75.00,  80.60,  93.00, 140.69]),
        (10001,20000,[75.00, 108.10, 125.00, 167.00]),
        (20001,30000,[75.00, 123.60, 141.00, 202.00]),
        (30001,40000,[75.00, 146.40, 176.00, 232.00]),
        (40001,50000,[75.00, 178.80, 213.00, 273.00]),
        (50001,60000,[75.00, 219.90, 240.00, 301.00]),
        (60001,70000,[75.00, 246.90, 277.00, 337.00]),
        (70001,80000,[75.00, 288.90, 313.00, 373.00]),
        (80001,90000,[75.00, 329.90, 348.00, 410.00]),
        (90001,100000,[75.00,389.60, 465.00, 520.00]),
    ],
    "utilitario_capital": [
        (0, 10000,  [80.00,  91.60, 115.40, 156.50]),
        (10001,20000,[80.00, 115.60, 142.49, 175.49]),
        (20001,30000,[80.00, 131.80, 177.69, 207.50]),
        (30001,40000,[80.00, 153.50, 207.89, 243.50]),
        (40001,50000,[80.00, 185.69, 248.60, 282.60]),
        (50001,60000,[80.00, 225.49, 275.59, 337.49]),
        (60001,70000,[80.00, 253.79, 327.79, 375.50]),
        (70001,80000,[80.00, 295.69, 377.60, 423.60]),
        (80001,90000,[80.00, 335.49, 427.79, 480.70]),
        (90001,100000,[80.00,375.59, 492.59, 540.69]),
    ],
    "utilitario_serrana": [
        (0, 10000,  [80.00,  85.60,  98.00, 145.69]),
        (10001,20000,[80.00, 113.10, 130.00, 172.00]),
        (20001,30000,[80.00, 128.60, 146.00, 207.00]),
        (30001,40000,[80.00, 151.40, 181.00, 237.00]),
        (40001,50000,[80.00, 183.80, 218.00, 278.00]),
        (50001,60000,[80.00, 224.90, 245.00, 306.00]),
        (60001,70000,[80.00, 251.90, 282.00, 342.00]),
        (70001,80000,[80.00, 293.90, 318.00, 378.00]),
        (80001,90000,[80.00, 334.90, 353.00, 415.00]),
        (90001,100000,[80.00,394.60, 470.00, 525.00]),
    ],
}

def fmt_brl(v: float) -> str:
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_prices(tipo, regiao, fipe):
    key = f"{tipo}_{'capital' if regiao=='Capital' else 'serrana'}"
    for mn, mx, vals in TABELAS[key]:
        if mn <= fipe <= mx:
            return vals
    return None

# =========================================================
# DRAW ENGINE
# =========================================================
def criar_imagem(dados):
    # BG
    try:
        bg = Image.open(BG_PATH).convert("RGBA")
        # garantir 1080x1350
        bg = bg.resize((W, H), Image.LANCZOS)
        img = bg.copy()
    except:
        img = Image.new("RGBA", (W, H), (255,255,255,255))

    draw = ImageDraw.Draw(img)

    # 1) Preencher textos (valores) em cima do BG, sem redesenhar rótulos.
    # Se seu BG for o novo (com caixas), você só muda estas coordenadas.
    # Para o BG "clássico" atual, isso já funciona.

    # Ajuste fino se precisar (x,y)
    # cliente / consultor / contato / data
    draw.text((330, 205), dados["cliente"], font=load_font(F_BOLD, 34), fill=AZUL)
    draw.text((305, 250), dados["consultor"], font=load_font(F_BOLD, 34), fill=LARANJA)
    draw.text((485, 250), f"•  {dados['contato']}" if dados["contato"] else "", font=load_font(F_BOLD, 30), fill=LARANJA)
    draw.text((820, 205), f"Data: {dados['data']}", font=load_font(F_REG, 28), fill=CINZA_TXT)

    # modelo / ano / fipe
    draw.text((W//2, 420), dados["modelo"], font=load_font(F_BOLD, 44), fill=PRETO, anchor="mm")
    draw.text((W//2, 500), f"Ano: {dados['ano']}  |  FIPE: R$ {dados['fipe']}", font=load_font(F_BOLD, 46), fill=AZUL, anchor="mm")

    # adesão (mantém a caixa do seu BG)
    draw.text((W//2, 580), f"Adesão: R$ {dados['adesao']}", font=load_font(F_REG, 38), fill=PRETO, anchor="mm")

    # 2) TABELA dentro da área-alvo fixa
    x1, y1, x2, y2 = TABLE_BOX

    # card skeuomorph: sombra + caixa branca translúcida
    drop_shadow(img, TABLE_BOX, radius=28, shadow_offset=(12,12), shadow_blur=18, shadow_alpha=95)
    draw_rounded_rect(img, TABLE_BOX, radius=28, fill=(255,255,255,220), outline=(220,220,220,255), outline_w=2)

    # layout interno do card
    pad = 24
    inner_x1, inner_y1, inner_x2, inner_y2 = x1+pad, y1+pad, x2-pad, y2-pad
    inner_w = inner_x2 - inner_x1

    # colunas
    col_names = ["Econ.", "Básico", "Plus", "Prem."]
    col_w = inner_w * 0.68 / 4  # 68% do espaço para 4 colunas
    label_w = inner_w - (col_w * 4)

    # header laranja
    head_h = 64
    head_box = (inner_x1, inner_y1, inner_x2, inner_y1 + head_h)
    draw.rounded_rectangle(head_box, radius=22, fill=LARANJA)

    # títulos colunas no header
    for i, name in enumerate(col_names):
        cx = inner_x1 + label_w + (i + 0.5) * col_w
        draw.text((cx, inner_y1 + head_h/2), name, font=f_plan, fill=BRANCO, anchor="mm")

    # preços (linha abaixo)
    prices_top = inner_y1 + head_h + 16
    prices_h = 92
    draw.line([(inner_x1, prices_top + prices_h), (inner_x2, prices_top + prices_h)], fill=(180,180,180,255), width=2)

    for i, price in enumerate(dados["precos"]):
        cx = inner_x1 + label_w + (i + 0.5) * col_w
        draw.text((cx, prices_top + 10), "R$", font=f_small, fill=PRETO, anchor="ma")
        draw.text((cx, prices_top + 60), fmt_brl(price), font=f_price, fill=PRETO, anchor="mm")

    # corpo (benefícios)
    itens = [
        ("Rastreamento", ["check","check","check","check"]),
        ("Reboque",       ["200","400","1mil","1mil"]),
        ("Roubo/Furto",   ["x","check","check","check"]),
        ("Colisão/PT",    ["x","x","check","check"]),
        ("Incêndio",      ["x","x","check","check"]),              # ✅ NOVO
        ("Terceiros",     ["x","x","check","check"]),
        ("Vidros",        ["x","x","check","check"]),
        ("Carro Res.",    ["x","x","10d","30d"]),
        ("Gás (GNV)",     ["x","x","x","check"]),
        ("Clube Certo",   ["x","check","check","check"]),          # ✅ NOVO
    ]

    body_top = prices_top + prices_h + 22
    # reserva espaço pro rodapé dentro do card (2 linhas + respiro)
    footer_space = 86
    body_bottom = inner_y2 - footer_space

    rows = len(itens)
    row_h = (body_bottom - body_top) / rows

    # linhas horizontais suaves (opcional)
    # for r in range(rows+1):
    #     y = body_top + r*row_h
    #     draw.line([(inner_x1, y), (inner_x2, y)], fill=(235,235,235,255), width=1)

    for r, (nome, statuses) in enumerate(itens):
        cy = body_top + r*row_h + row_h/2

        # label à esquerda
        draw.text((inner_x1, cy), nome, font=f_label, fill=CINZA_TXT, anchor="lm")

        # status por coluna
        for i, stt in enumerate(statuses):
            cx = inner_x1 + label_w + (i + 0.5) * col_w
            draw_status(draw, int(cx), int(cy), stt)

    # rodapé dentro do card (mantém suas 3 frases)
    foot_y = inner_y2 - footer_space + 8
    msg1 = "⚠ PAGAMENTO ANTECIPADO GERA DESCONTO ⚠"
    msg2 = "CONHEÇA OS NOSSOS PLANOS PARA PROTEÇÃO DE MOTOS ELÉTRICAS"
    msg3 = "A COTAÇÃO PODE SOFRER ALTERAÇÕES BASEADAS NOS VALORES VIGENTES"

    # msg1 (laranja)
    draw.text(((inner_x1+inner_x2)//2, foot_y), msg1, font=f_footer, fill=LARANJA, anchor="mm")

    # msg2 (caixa azul fina)
    pill_y = foot_y + 34
    pill_padx, pill_pady = 18, 10
    pill_w = int(draw.textlength(msg2, font=f_footer2)) + pill_padx*2
    pill_h = 36
    px1 = (inner_x1+inner_x2)//2 - pill_w//2
    py1 = pill_y - pill_h//2
    px2 = px1 + pill_w
    py2 = py1 + pill_h
    draw.rounded_rectangle([px1,py1,px2,py2], radius=18, fill=(230,240,255,255), outline=(50,90,140,255), width=2)
    draw.text(((inner_x1+inner_x2)//2, pill_y), msg2, font=f_footer2, fill=(20,60,110,255), anchor="mm")

    # msg3 (azul)
    draw.text(((inner_x1+inner_x2)//2, foot_y + 74), msg3, font=f_footer2, fill=AZUL, anchor="mm")

    return img.convert("RGB")

# =========================================================
# STREAMLIT UI
# =========================================================
st.title("📝 Gerador de Cotação")

c1, c2 = st.columns(2)
cliente = c1.text_input("Proposta para (Cliente)", value="")
consultor = c2.text_input("Consultor(a)", value="")

c3, c4 = st.columns(2)
contato = c3.text_input("Contato WhatsApp (ex: (21) 99999-9999)", value="")
data = c4.text_input("Data", value=datetime.date.today().strftime("%d/%m/%Y"))

st.divider()

c5, c6 = st.columns(2)
tipo = c5.selectbox("Tipo", ["carro", "utilitario"])
regiao = c6.selectbox("Região", ["Capital", "Serrana"])

modelo = st.text_input("Modelo do veículo", value="")
c7, c8 = st.columns(2)
ano = c7.text_input("Ano", value="")
fipe = c8.number_input("Valor FIPE (R$)", min_value=0.0, step=100.0, value=28000.0)

adesao = st.text_input("Adesão (R$)", value="300,00")

# Estado: imagem gerada
if "last_img_bytes" not in st.session_state:
    st.session_state.last_img_bytes = None
if "last_filename" not in st.session_state:
    st.session_state.last_filename = None

def montar_mensagem(cliente, modelo, ano, fipe, regiao, tipo):
    # texto curto pra WhatsApp
    return (
        f"Olá {cliente}! Segue sua cotação LEGACY.\n\n"
        f"Veículo: {modelo} ({ano})\n"
        f"FIPE: R$ {fipe}\n"
        f"Tipo: {tipo} | Região: {regiao}\n\n"
        f"Vou te enviar a imagem da cotação aqui no WhatsApp. ✅"
    )

if st.button("GERAR COTAÇÃO", type="primary"):
    if not cliente or not modelo or not ano or fipe <= 0:
        st.warning("Preencha: Cliente, Modelo, Ano e FIPE.")
    else:
        precos = get_prices(tipo, regiao, fipe)
        if not precos:
            st.error("FIPE fora das faixas (0 a 100.000).")
        else:
            dados = {
                "cliente": cliente.strip(),
                "consultor": consultor.strip(),
                "contato": contato.strip(),
                "data": data.strip(),
                "modelo": modelo.strip().upper(),
                "ano": ano.strip(),
                "fipe": fmt_brl(fipe),
                "adesao": adesao.strip(),
                "precos": precos,
            }

            img = criar_imagem(dados)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.session_state.last_img_bytes = buf.getvalue()
            safe_name = cliente.replace(" ", "_").replace("/", "_")
            st.session_state.last_filename = f"Cotacao_{safe_name}.png"

            st.image(img, caption="Prévia da Cotação", use_container_width=True)

            st.download_button(
                "📥 BAIXAR IMAGEM",
                st.session_state.last_img_bytes,
                st.session_state.last_filename,
                "image/png"
            )

# Botão de WhatsApp aparece só depois de gerar
if st.session_state.last_img_bytes:
    st.success("Cotação gerada. Confira e envie pelo WhatsApp.")

    msg = montar_mensagem(cliente, modelo, ano, fmt_brl(fipe), regiao, tipo)
    wa_text = urllib.parse.quote(msg)

    # Link genérico (abre WhatsApp Web/App com mensagem pronta)
    wa_link = f"https://wa.me/?text={wa_text}"

    st.markdown(
        f"""
        <a href="{wa_link}" target="_blank" style="text-decoration:none;">
            <div style="
                background:#19c37d;
                color:white;
                padding:14px 18px;
                border-radius:12px;
                font-weight:700;
                text-align:center;
                margin-top:10px;
            ">✅ ENVIAR COTAÇÃO (WhatsApp)</div>
        </a>
        <p style="color:#666;margin-top:8px;">
            Observação: o WhatsApp vai abrir com a mensagem pronta. Você só anexa a imagem baixada (2 cliques).
        </p>
        """,
        unsafe_allow_html=True
    )
