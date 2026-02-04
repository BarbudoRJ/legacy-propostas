import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
import urllib.parse

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Cotação LEGACY", page_icon="🧾", layout="centered")

# Estilo do botão de compartilhamento
st.markdown("""
<style>
    .stButton>button { width: 100%; font-weight: bold; }
    .share-btn {
        background-color: #25D366; color: white; padding: 12px 20px;
        text-align: center; text-decoration: none; display: block;
        font-size: 16px; border-radius: 8px; border: none; width: 100%;
        font-weight: bold; cursor: pointer; margin-top: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .share-btn:hover { background-color: #128C7E; }
</style>
""", unsafe_allow_html=True)

BG_PATH = "fundo.png"

# =========================
# DADOS (TABELA FIXA)
# =========================
TABELA = {
  "carro_capital": [
    {"min":0,"max":10000,"economico":75.00,"basico":86.60,"plus":110.40,"premium":151.50},
    {"min":10001,"max":20000,"economico":75.00,"basico":110.60,"plus":137.49,"premium":170.49},
    {"min":20001,"max":30000,"economico":75.00,"basico":126.80,"plus":172.69,"premium":202.50},
    {"min":30001,"max":40000,"economico":75.00,"basico":148.50,"plus":202.89,"premium":238.50},
    {"min":40001,"max":50000,"economico":75.00,"basico":180.69,"plus":243.60,"premium":277.60},
    {"min":50001,"max":60000,"economico":75.00,"basico":220.49,"plus":270.59,"premium":332.49},
    {"min":60001,"max":70000,"economico":75.00,"basico":248.79,"plus":322.79,"premium":370.50},
    {"min":70001,"max":80000,"economico":75.00,"basico":290.69,"plus":372.60,"premium":418.60},
    {"min":80001,"max":90000,"economico":75.00,"basico":330.49,"plus":422.79,"premium":475.70},
    {"min":90001,"max":100000,"economico":75.00,"basico":370.59,"plus":487.59,"premium":535.69},
  ],
  "carro_serrana": [
    {"min":0,"max":10000,"economico":75.00,"basico":80.60,"plus":93.00,"premium":140.69},
    {"min":10001,"max":20000,"economico":75.00,"basico":108.10,"plus":125.00,"premium":167.00},
    {"min":20001,"max":30000,"economico":75.00,"basico":123.60,"plus":141.00,"premium":202.00},
    {"min":30001,"max":40000,"economico":75.00,"basico":146.40,"plus":176.00,"premium":232.00},
    {"min":40001,"max":50000,"economico":75.00,"basico":178.80,"plus":213.00,"premium":273.00},
    {"min":50001,"max":60000,"economico":75.00,"basico":219.90,"plus":240.00,"premium":301.00},
    {"min":60001,"max":70000,"economico":75.00,"basico":246.90,"plus":277.00,"premium":337.00},
    {"min":70001,"max":80000,"economico":75.00,"basico":288.90,"plus":313.00,"premium":373.00},
    {"min":80001,"max":90000,"economico":75.00,"basico":329.90,"plus":348.00,"premium":410.00},
    {"min":90001,"max":100000,"economico":75.00,"basico":389.60,"plus":465.00,"premium":520.00},
  ],
  "utilitario_capital": [
    {"min":0,"max":10000,"economico":80.00,"basico":91.60,"plus":115.40,"premium":156.50},
    {"min":10001,"max":20000,"economico":80.00,"basico":115.60,"plus":142.49,"premium":175.49},
    {"min":20001,"max":30000,"economico":80.00,"basico":131.80,"plus":177.69,"premium":207.50},
    {"min":30001,"max":40000,"economico":80.00,"basico":153.50,"plus":207.89,"premium":243.50},
    {"min":40001,"max":50000,"economico":80.00,"basico":185.69,"plus":248.60,"premium":282.60},
    {"min":50001,"max":60000,"economico":80.00,"basico":225.49,"plus":275.59,"premium":337.49},
    {"min":60001,"max":70000,"economico":80.00,"basico":253.79,"plus":327.79,"premium":375.50},
    {"min":70001,"max":80000,"economico":80.00,"basico":295.69,"plus":377.60,"premium":423.60},
    {"min":80001,"max":90000,"economico":80.00,"basico":335.49,"plus":427.79,"premium":480.70},
    {"min":90001,"max":100000,"economico":80.00,"basico":375.59,"plus":492.59,"premium":540.69},
  ],
  "utilitario_serrana": [
    {"min":0,"max":10000,"economico":80.00,"basico":85.60,"plus":98.00,"premium":145.69},
    {"min":10001,"max":20000,"economico":80.00,"basico":113.10,"plus":130.00,"premium":172.00},
    {"min":20001,"max":30000,"economico":80.00,"basico":128.60,"plus":146.00,"premium":207.00},
    {"min":30001,"max":40000,"economico":80.00,"basico":151.40,"plus":181.00,"premium":237.00},
    {"min":40001,"max":50000,"economico":80.00,"basico":183.80,"plus":218.00,"premium":278.00},
    {"min":50001,"max":60000,"economico":80.00,"basico":224.90,"plus":245.00,"premium":306.00},
    {"min":60001,"max":70000,"economico":80.00,"basico":251.90,"plus":282.00,"premium":342.00},
    {"min":70001,"max":80000,"economico":80.00,"basico":293.90,"plus":318.00,"premium":378.00},
    {"min":80001,"max":90000,"economico":80.00,"basico":334.90,"plus":353.00,"premium":415.00},
    {"min":90001,"max":100000,"economico":80.00,"basico":394.60,"plus":470.00,"premium":525.00},
  ],
}

# =========================
# HELPERS
# =========================
def brl(v: float) -> str:
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

def pick_planos(fipe_val: float, categoria: str, regiao: str):
    prefix = "carro" if categoria == "Carro" else "utilitario"
    suffix = "capital" if regiao == "Capital" else "serrana"
    key = f"{prefix}_{suffix}"

    # Fallback se a chave não existir
    if key not in TABELA: return None

    # Verifica limite superior
    if fipe_val > 100000:
        last = TABELA[key][-1]
        return [last["economico"], last["basico"], last["plus"], last["premium"]]

    for faixa in TABELA[key]:
        if faixa["min"] <= fipe_val <= faixa["max"]:
            return [faixa["economico"], faixa["basico"], faixa["plus"], faixa["premium"]]
    return None

def load_font(size, bold=False):
    # Tenta carregar fontes, senão usa padrão
    try:
        path = "bold.ttf" if bold else "regular.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def fit_text(draw, text, max_w, start_size=44, bold=False, min_size=16):
    size = start_size
    # Proteção contra loop infinito ou fonte padrão
    font = load_font(size, bold=bold)
    
    # Se for fonte padrão, não dá pra redimensionar, retorna direto
    if not hasattr(font, 'size'):
        return font

    while size >= min_size:
        font = load_font(size, bold=bold)
        w = draw.textlength(text, font=font)
        if w <= max_w:
            return font
        size -= 2
    return load_font(min_size, bold=bold)

def draw_round_rect(draw, xy, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_neu_card(base_img, box, radius=28):
    """Caixa com sombra suave (Glassmorphism/Neumorphism)"""
    x1,y1,x2,y2 = box
    card = Image.new("RGBA", base_img.size, (0,0,0,0))
    d = ImageDraw.Draw(card)

    # sombra escura (baixo-direita)
    d.rounded_rectangle((x1+8, y1+10, x2+8, y2+10), radius=radius, fill=(0,0,0,70))
    # sombra clara (cima-esquerda)
    d.rounded_rectangle((x1-6, y1-6, x2-6, y2-6), radius=radius, fill=(255,255,255,120))
    # corpo
    d.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=(255,255,255,230), outline=(210,210,210,255), width=2)

    return Image.alpha_composite(base_img.convert("RGBA"), card)

def draw_icon_check(draw, cx, cy, r=16):
    # círculo verde + check
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(36,168,90,255))
    # check desenhado
    pts = [(cx-6, cy+1), (cx-1, cy+6), (cx+8, cy-5)]
    draw.line(pts[0:2], fill="white", width=4)
    draw.line(pts[1:3], fill="white", width=4)

def draw_icon_x(draw, cx, cy, r=16):
    # círculo vermelho + X
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(220,70,70,255))
    # X desenhado
    d = 5
    draw.line((cx-d, cy-d, cx+d, cy+d), fill="white", width=4)
    draw.line((cx+d, cy-d, cx-d, cy+d), fill="white", width=4)

def draw_centered_value(draw, text, center, max_w, base_size=40, bold=True):
    font = fit_text(draw, text, max_w=max_w, start_size=base_size, bold=bold, min_size=18)
    draw.text(center, text, font=font, fill=(255,255,255,255), anchor="mm")

# =========================
# RENDER PRINCIPAL
# =========================
def render_cotacao(dados):
    try:
        bg = Image.open(BG_PATH).convert("RGBA")
    except:
        # Fallback se não tiver imagem
        bg = Image.new("RGBA", (1080, 1350), (200, 200, 200, 255))
        
    bg = bg.resize((1080, 1350), Image.LANCZOS)
    draw = ImageDraw.Draw(bg)

    # ===== 1. PREENCHIMENTO DO TOPO =====
    # Tarja esquerda
    draw_centered_value(draw, dados["cliente"], (330, 182), max_w=380, base_size=44, bold=True)
    draw_centered_value(draw, dados["data"], (330, 210), max_w=380, base_size=38, bold=False)

    # Tarja direita
    draw_centered_value(draw, dados["adesao_brl"], (760, 182), max_w=380, base_size=44, bold=True)
    draw_centered_value(draw, dados["consultor"], (760, 210), max_w=380, base_size=40, bold=True)

    # Tarja grande (Placa / Modelo)
    if dados["placa"]:
        draw_centered_value(draw, dados["placa"], (390, 275), max_w=520, base_size=54, bold=True)

    modelo_ano = f"{dados['modelo']} / {dados['ano']}"
    draw_centered_value(draw, modelo_ano, (520, 310), max_w=650, base_size=48, bold=True)

    # ===== 2. TABELA NO ESPAÇO EM BRANCO =====
    TABLE_BOX = (70, 400, 1010, 890) # Ajuste vertical para não encostar
    
    # Desenha o cartão (fundo branco translúcido)
    bg = draw_neu_card(bg, TABLE_BOX, radius=30)
    draw = ImageDraw.Draw(bg)

    x1, y1, x2, y2 = TABLE_BOX
    pad = 28
    inner_x1, inner_x2 = x1 + pad, x2 - pad
    inner_y1 = y1 + pad
    
    # Métricas Colunas
    w = x2 - x1
    label_col_w = int(w * 0.30)
    col_area_w = (inner_x2 - inner_x1) - label_col_w
    col_w = col_area_w / 4
    
    col_centers = [inner_x1 + label_col_w + (i * col_w) + (col_w/2) for i in range(4)]

    # Cabeçalho Laranja
    header_h = 62
    draw_round_rect(draw, (x1+18, y1+18, x2-18, y1+18+header_h), radius=22, fill=(242, 120, 40, 255))

    f_head = load_font(34, bold=True)
    for i, t in enumerate(["Econ.", "Básico", "Plus", "Prem."]):
        draw.text((col_centers[i], y1+18+header_h/2), t, font=f_head, fill="white", anchor="mm")

    # Preços
    price_top = y1 + 18 + header_h + 18
    f_price_rs = load_font(22, bold=False)
    f_price = load_font(40, bold=True)
    
    for i, val in enumerate(dados["precos"]):
        draw.text((col_centers[i], price_top+10), "R$", font=f_price_rs, fill=(30,30,30,255), anchor="mm")
        draw.text((col_centers[i], price_top+40), brl(val), font=f_price, fill=(30,30,30,255), anchor="mm")

    sep_y = price_top + 78
    draw.line((x1+30, sep_y, x2-30, sep_y), fill=(190,190,190,255), width=2)

    # Benefícios
    itens = [
        ("Rastreamento", ["check","check","check","check"]),
        ("Reboque",      ["200","400","1mil","1mil"]),
        ("Roubo/Furto",  ["x","check","check","check"]),
        ("Colisão/PT",   ["x","x","check","check"]),
        ("Incêndio",     ["x","x","check","check"]),
        ("Terceiros",    ["x","x","check","check"]),
        ("Vidros",       ["x","x","check","check"]),
        ("Carro Res.",   ["x","x","10d","30d"]),
        ("Gás (GNV)",    ["x","x","x","check"]),
        ("Clube Certo",  ["x","check","check","check"]),
    ]

    body_top = sep_y + 22
    body_bottom = y2 - 26
    row_h = (body_bottom - body_top) / len(itens)
    f_label = load_font(28, bold=False)

    # Função interna para desenhar pílulas (ex: "200", "10d")
    def draw_small_pill(cx, cy, text):
        font = load_font(24, bold=True)
        tw = draw.textlength(text, font=font)
        # Borda e fundo
        draw_round_rect(draw, (cx - tw/2 - 14, cy - 16, cx + tw/2 + 14, cy + 16), radius=16, 
                        fill=(240,240,240,255), outline=(200,200,200,255))
        draw.text((cx, cy), text, font=font, fill=(50,50,50,255), anchor="mm")

    for idx, (nome, vals) in enumerate(itens):
        cy = body_top + (idx * row_h) + (row_h/2)
        # Nome Benefício
        draw.text((inner_x1, cy), nome, font=f_label, fill=(85,85,85,255), anchor="lm")

        # Colunas de Status
        for i, v in enumerate(vals):
            cx = col_centers[i]
            if v == "check": draw_icon_check(draw, cx, cy)
            elif v == "x":     draw_icon_x(draw, cx, cy)
            else:              draw_small_pill(cx, cy, v)

    return bg.convert("RGB")

# =========================
# UI (STREAMLIT)
# =========================
st.title("🧾 Cotação LEGACY")
st.caption("Gerador com Tabela Fixa e Fundo Personalizado")

# Formulário
c1, c2 = st.columns(2)
cliente = c1.text_input("Cliente", placeholder="Nome do Cliente")
consultor = c2.text_input("Consultor", value="Seu Nome")

c3, c4 = st.columns(2)
adesao = c3.number_input("Adesão (R$)", min_value=0.0, step=50.0, value=300.0)
data_str = c4.text_input("Data", value=datetime.now().strftime("%d/%m/%Y"))

placa = st.text_input("Placa (Opcional)", placeholder="ABC-1234")

c5, c6 = st.columns(2)
categoria = c5.selectbox("Categoria", ["Carro", "Utilitário"])
regiao = c6.selectbox("Região", ["Capital", "Serrana"])

c7, c8 = st.columns(2)
modelo = c7.text_input("Modelo", placeholder="Ex: Honda Civic")
ano = c8.text_input("Ano", placeholder="Ex: 2021")

fipe_val = st.number_input("Valor Veículo (Tabela FIPE)", min_value=0.0, step=500.0)

if "img_data" not in st.session_state:
    st.session_state.img_data = None
if "client_name" not in st.session_state:
    st.session_state.client_name = ""

# Botão Gerar
if st.button("GERAR COTAÇÃO", type="primary"):
    if not cliente or not modelo or fipe_val <= 0:
        st.warning("Preencha Cliente, Modelo e Valor do Veículo.")
    else:
        precos = pick_planos(fipe_val, categoria, regiao)
        if not precos:
            st.error("Valor do veículo fora da tabela cadastrada.")
        else:
            dados = {
                "cliente": cliente.upper(),
                "data": data_str,
                "adesao_brl": brl(adesao),
                "consultor": consultor.upper(),
                "placa": placa.upper(),
                "modelo": modelo.upper(),
                "ano": ano,
                "precos": precos,
            }
            
            img = render_cotacao(dados)
            
            # Converte para bytes
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()
            
            # Salva no estado
            st.session_state.img_data = img_bytes
            st.session_state.client_name = cliente
            st.success("Imagem gerada com sucesso!")

# Exibição e Envio
if st.session_state.img_data:
    st.markdown("---")
    col_view, col_action = st.columns([1, 1])
    
    with col_view:
        st.image(st.session_state.img_data, caption="Prévia", use_container_width=True)
        
    with col_action:
        # Download PC
        st.download_button(
            "📥 Baixar no Computador",
            st.session_state.img_data,
            file_name=f"Cotacao_{st.session_state.client_name}.png",
            mime="image/png"
        )
        
        # Botão Inteligente (Mobile)
        b64_img = base64.b64encode(st.session_state.img_data).decode()
        share_code = f"""
        <script>
        async function shareImage() {{
            const b64 = "{b64_img}";
            const blob = await (await fetch(`data:image/png;base64,${{b64}}`)).blob();
            const file = new File([blob], "cotacao.png", {{ type: "image/png" }});
            if (navigator.share) {{
                await navigator.share({{
                    files: [file],
                    title: 'Cotação Legacy',
                    text: 'Olá {st.session_state.client_name}, segue sua cotação!'
                }});
            }} else {{
                alert('Recurso disponível apenas em Celulares (Android/iOS). No PC, use o botão de Baixar.');
            }}
        }}
        </script>
        <button onclick="shareImage()" class="share-btn">
            📱 ENVIAR IMAGEM (WhatsApp)
        </button>
        """
        st.components.v1.html(share_code, height=60)
