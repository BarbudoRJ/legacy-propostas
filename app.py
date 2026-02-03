import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import urllib.parse
from datetime import date

# =========================================================
# CONFIG GERAL
# =========================================================
st.set_page_config(page_title="Cotação Legacy", page_icon="📝", layout="centered")

W, H = 1080, 1350

# Provedor FIPE gratuito (paralellum)
BASE_FIPE = "https://parallelum.com.br/fipe/api/v1"
TYPE_MAP = {"Carro": "carros", "Moto": "motos", "Utilitário": "caminhoes"}  # caminhões/ônibus

# =========================================================
# HELPERS: API + CACHE
# =========================================================
@st.cache_data(ttl=60 * 60)
def api_get(url: str):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60 * 60)
def listar_marcas(tipo_api: str):
    return api_get(f"{BASE_FIPE}/{tipo_api}/marcas")

@st.cache_data(ttl=60 * 60)
def listar_modelos(tipo_api: str, marca_id: int):
    return api_get(f"{BASE_FIPE}/{tipo_api}/marcas/{marca_id}/modelos")

@st.cache_data(ttl=60 * 60)
def listar_anos(tipo_api: str, marca_id: int, modelo_id: int):
    return api_get(f"{BASE_FIPE}/{tipo_api}/marcas/{marca_id}/modelos/{modelo_id}/anos")

def buscar_fipe(tipo_api: str, marca_id: int, modelo_id: int, ano_codigo: str):
    return api_get(f"{BASE_FIPE}/{tipo_api}/marcas/{marca_id}/modelos/{modelo_id}/anos/{ano_codigo}")

def brl_to_float(valor_brl: str) -> float:
    # "R$ 28.000,00" -> 28000.00
    v = valor_brl.replace("R$", "").strip()
    v = v.replace(".", "").replace(",", ".")
    return float(v)

def apenas_ano(ano_nome: str) -> str:
    # Ex.: "2012 Gasolina" -> "2012"
    for ch in ano_nome:
        pass
    return ano_nome[:4] if len(ano_nome) >= 4 and ano_nome[:4].isdigit() else ano_nome

# =========================================================
# SUA REGRA DE MENSALIDADES (por faixa) - já existente
# =========================================================
def calcular_mensalidades(fipe_float, regiao):
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
        if fipe_float <= teto:
            return [f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in precos[idx]]
    return None

# =========================================================
# DESENHO: ÍCONES BONITINHOS (círculo + check/x)
# =========================================================
def draw_check_icon(draw, cx, cy, ok=True):
    # estilo simples e limpo: círculo + símbolo branco
    r = 17
    if ok:
        fill = (30, 160, 90, 255)   # verde
        symbol = "✓"
    else:
        fill = (210, 60, 60, 255)   # vermelho
        symbol = "✕"
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)
    # símbolo central
    draw.text((cx, cy+1), symbol, fill=(255,255,255,255), anchor="mm", font=F_ICON)

def draw_pill(draw, x, y, text, font, padding_x=20, padding_y=8,
              fill=(255,255,255,210), outline=(200,200,200,255), text_fill=(15,15,15,255)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    w = tw + padding_x*2
    h = th + padding_y*2
    r = int(h/2)
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=2)
    draw.text((x + w/2, y + h/2), text, font=font, fill=text_fill, anchor="mm")
    return (x, y, x+w, y+h)

# =========================================================
# FONTES (tenta carregar; se falhar, usa default)
# =========================================================
def load_fonts():
    try:
        f_bold = ImageFont.truetype("bold.ttf", 34)
        f_reg  = ImageFont.truetype("regular.ttf", 30)
        f_small= ImageFont.truetype("regular.ttf", 24)
        f_tbl_h= ImageFont.truetype("bold.ttf", 30)
        f_tbl_v= ImageFont.truetype("bold.ttf", 34)
        f_icon = ImageFont.truetype("bold.ttf", 22)
    except:
        f_bold = f_reg = f_small = f_tbl_h = f_tbl_v = f_icon = ImageFont.load_default()
    return f_bold, f_reg, f_small, f_tbl_h, f_tbl_v, f_icon

F_BOLD, F_REG, F_SMALL, F_TBL_H, F_TBL_V, F_ICON = load_fonts()

# =========================================================
# GERADOR DE IMAGEM (RESPEITA FUNDO - SÓ VALORES + TABELA)
# =========================================================
def criar_imagem(dados):
    # 1) carregar fundo SEM CROP
    bg = Image.open("fundo.png").convert("RGBA")
    bg = bg.resize((W, H), Image.LANCZOS)
    img = bg.copy()

    # cores
    AZUL = (0, 35, 95, 255)
    PRETO = (15, 15, 15, 255)
    LARANJA = (230, 120, 20, 255)
    CINZA_L = (245, 245, 245, 230)
    OUTLINE = (205, 205, 205, 255)

    draw = ImageDraw.Draw(img)

    # -----------------------------
    # (A) PREENCHER CAMPOS DO LAYOUT (SÓ VALORES)
    # -----------------------------
    # Coordenadas alinhadas ao layout enviado (1080x1350)
    x_val_top = 300
    y_proposta = 125
    y_consultor = 155
    y_contato  = 185
    y_data     = 215

    draw.text((x_val_top, y_proposta), dados.get("cliente",""), font=F_BOLD, fill=AZUL, anchor="lm")
    draw.text((x_val_top, y_consultor), dados.get("consultor",""), font=F_BOLD, fill=AZUL, anchor="lm")
    draw.text((x_val_top, y_contato), dados.get("contato",""), font=F_BOLD, fill=AZUL, anchor="lm")
    draw.text((x_val_top, y_data), dados.get("data",""), font=F_BOLD, fill=AZUL, anchor="lm")

    x_val_box = 295
    y_placa   = 310
    y_modelo  = 360
    y_adesao  = 410

    draw.text((x_val_box, y_placa),  dados.get("placa",""), font=F_BOLD, fill=PRETO, anchor="lm")

    modelo_ano = f"{dados.get('modelo','')} | {dados.get('ano','')}"
    draw.text((x_val_box, y_modelo), modelo_ano, font=F_BOLD, fill=PRETO, anchor="lm")

    draw.text((x_val_box, y_adesao), dados.get("adesao",""), font=F_BOLD, fill=PRETO, anchor="lm")

    # -----------------------------
    # (B) PAINEL DA TABELA (não mexe no rodapé fixo do fundo)
    # -----------------------------
    panel_x0, panel_y0, panel_x1, panel_y1 = 70, 520, 1010, 1085

    # efeito "esquelmorfo" simples: blur do recorte + overlay claro
    # (sem precisar de nada avançado)
    panel_crop = img.crop((panel_x0, panel_y0, panel_x1, panel_y1)).filter(ImageFilter.GaussianBlur(6))
    overlay = Image.new("RGBA", (panel_x1-panel_x0, panel_y1-panel_y0), CINZA_L)
    panel = Image.alpha_composite(panel_crop, overlay)

    # borda e sombra leve (fake)
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle([8, 8, (panel_x1-panel_x0)-8, (panel_y1-panel_y0)-8],
                                 radius=28, outline=OUTLINE, width=3)

    # cola o painel pronto
    img.paste(panel, (panel_x0, panel_y0), panel)

    # agora desenhar a tabela EM CIMA do painel
    draw = ImageDraw.Draw(img)

    # grid base
    inner_x0 = panel_x0 + 35
    inner_x1 = panel_x1 - 35
    inner_y0 = panel_y0 + 35
    inner_y1 = panel_y1 - 35

    cols = ["Econ.", "Básico", "Plus", "Prem."]
    col_w = int((inner_x1 - inner_x0) / 4)

    # Header laranja
    header_h = 56
    draw.rounded_rectangle([inner_x0, inner_y0, inner_x1, inner_y0 + header_h],
                           radius=18, fill=LARANJA)
    for i, c in enumerate(cols):
        cx = inner_x0 + i*col_w + col_w//2
        draw.text((cx, inner_y0 + header_h/2), c, font=F_TBL_H, fill=(255,255,255,255), anchor="mm")

    y = inner_y0 + header_h + 20

    # valores (mensalidades)
    precos = dados["precos"]  # lista 4 itens já formatados em BRL
    for i, p in enumerate(precos):
        cx = inner_x0 + i*col_w + col_w//2
        # quebra "R$ 75,00" em duas linhas: R$ e valor
        valor = p.replace("R$ ", "")
        draw.text((cx, y), "R$", font=F_SMALL, fill=PRETO, anchor="mm")
        draw.text((cx, y+34), valor, font=F_TBL_V, fill=PRETO, anchor="mm")

    # linha
    y += 85
    draw.line([(inner_x0, y), (inner_x1, y)], fill=(210,210,210,255), width=2)
    y += 25

    # Benefícios (fixos conforme seu exemplo anterior)
    # status pode ser: True/False/"200"/"400"/"1mil"/"10d"/"30d"
    itens = [
        ("Rastreamento", [True, True, True, True]),
        ("Reboque",      ["200", "400", "1mil", "1mil"]),
        ("Roubo/Furto",  [False, True, True, True]),
        ("Colisão/PT",   [False, False, True, True]),
        ("Terceiros",    [False, False, True, True]),
        ("Vidros",       [False, False, True, True]),
        ("Carro Res.",   [False, False, "10d", "30d"]),
        ("Gás (GNV)",    [False, False, False, True]),
    ]

    row_h = 52
    label_x = inner_x0
    for nome, status in itens:
        # nome
        draw.text((label_x, y + row_h/2), nome, font=F_REG, fill=(90,90,90,255), anchor="lm")

        for i, s in enumerate(status):
            cx = inner_x0 + i*col_w + col_w//2

            if s is True:
                draw_check_icon(draw, cx, y + row_h/2, ok=True)
            elif s is False:
                draw_check_icon(draw, cx, y + row_h/2, ok=False)
            else:
                # texto em "pill"
                px = cx - 44
                py = y + row_h/2 - 18
                draw_pill(draw, px, py, str(s), font=F_REG,
                          fill=(255,255,255,200), outline=(210,210,210,255), text_fill=PRETO)

        y += row_h

    return img.convert("RGB")

# =========================================================
# WHATSAPP: mensagem
# =========================================================
def montar_mensagem(dados):
    msg = (
        f"Olá, {dados.get('cliente','')}! Segue sua cotação LEGACY.\n\n"
        f"Placa: {dados.get('placa','')}\n"
        f"Veículo: {dados.get('modelo','')} | Ano: {dados.get('ano','')}\n"
        f"FIPE: {dados.get('fipe_str','')}\n"
        f"Adesão: {dados.get('adesao','')}\n\n"
        f"Mensalidades:\n"
        f"Econ: {dados['precos'][0]}\n"
        f"Básico: {dados['precos'][1]}\n"
        f"Plus: {dados['precos'][2]}\n"
        f"Premium: {dados['precos'][3]}\n\n"
        f"Pagamento antecipado gera desconto.\n"
        f"A cotação pode sofrer alterações baseadas nos valores vigentes."
    )
    return msg

# =========================================================
# UI (APP)
# =========================================================
st.title("📝 Cotação LEGACY (layout fixo + tabela automática)")

# Estado
if "fipe_float" not in st.session_state:
    st.session_state.fipe_float = None
if "fipe_str" not in st.session_state:
    st.session_state.fipe_str = None
if "cotacao_img_bytes" not in st.session_state:
    st.session_state.cotacao_img_bytes = None
if "cotacao_dados" not in st.session_state:
    st.session_state.cotacao_dados = None
if "wa_link" not in st.session_state:
    st.session_state.wa_link = None

with st.expander("Identificação", expanded=True):
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Proposta para", value="")
    data_txt = col2.text_input("Data", value=date.today().strftime("%d/%m/%Y"))

    col3, col4 = st.columns(2)
    consultor = col3.text_input("Consultor(a)", value="")
    contato = col4.text_input("Contato (telefone)", value="")

    placa = st.text_input("Placa (opcional)", value="")
    adesao = st.text_input("Adesão (texto que vai no layout)", value="R$ 300,00")

st.subheader("Dados do veículo (confiável)")
colA, colB = st.columns(2)
tipo_label = colA.selectbox("Tipo", ["Carro", "Moto", "Utilitário"])
regiao = colB.selectbox("Região (para sua tabela interna)", ["Capital", "Serrana"])

tipo_api = TYPE_MAP[tipo_label]

# Marcas
marcas = listar_marcas(tipo_api)
marca_opcoes = {m["nome"]: int(m["codigo"]) for m in marcas}
marca_nome = st.selectbox("Marca", list(marca_opcoes.keys()))
marca_id = marca_opcoes[marca_nome]

# Modelos
dados_modelos = listar_modelos(tipo_api, marca_id)
modelos = dados_modelos["modelos"]
modelo_opcoes = {m["nome"]: int(m["codigo"]) for m in modelos}
modelo_nome = st.selectbox("Modelo", list(modelo_opcoes.keys()))
modelo_id = modelo_opcoes[modelo_nome]

# Anos
anos = listar_anos(tipo_api, marca_id, modelo_id)
ano_opcoes = {a["nome"]: a["codigo"] for a in anos}
ano_nome = st.selectbox("Ano", list(ano_opcoes.keys()))
ano_codigo = ano_opcoes[ano_nome]

colC, colD = st.columns(2)

if colC.button("Buscar FIPE", type="primary"):
    try:
        info = buscar_fipe(tipo_api, marca_id, modelo_id, ano_codigo)
        valor_str = info.get("Valor")
        if not valor_str:
            st.error("Não consegui obter FIPE (resposta inesperada).")
        else:
            st.session_state.fipe_str = valor_str
            st.session_state.fipe_float = brl_to_float(valor_str)
            st.success(f"FIPE encontrado: {valor_str}")
    except Exception as e:
        st.error(f"Falha ao consultar FIPE: {e}")

if st.session_state.fipe_str:
    st.info(f"FIPE: {st.session_state.fipe_str}")

# Gerar Cotação
gerar_ok = st.session_state.fipe_float is not None and cliente.strip() != "" and consultor.strip() != ""

if colD.button("Gerar Cotação", disabled=not gerar_ok):
    fipe_float = st.session_state.fipe_float
    precos = calcular_mensalidades(fipe_float, regiao)

    if not precos:
        st.error("FIPE acima do limite ou fora das faixas configuradas.")
    else:
        dados = {
            "cliente": cliente.strip(),
            "consultor": consultor.strip(),
            "contato": contato.strip(),
            "data": data_txt.strip(),
            "placa": placa.strip(),
            "modelo": modelo_nome.strip(),
            "ano": apenas_ano(ano_nome),
            "adesao": adesao.strip(),
            "fipe_str": st.session_state.fipe_str,
            "fipe_float": fipe_float,
            "precos": precos
        }

        img = criar_imagem(dados)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.session_state.cotacao_img_bytes = buf.getvalue()
        st.session_state.cotacao_dados = dados

        # WhatsApp link
        msg = montar_mensagem(dados)
        msg_enc = urllib.parse.quote(msg)
        st.session_state.wa_link = f"https://wa.me/?text={msg_enc}"

# Preview + download + enviar whatsapp
if st.session_state.cotacao_img_bytes:
    st.image(st.session_state.cotacao_img_bytes, caption="Cotação gerada (respeitando o layout do fundo)", width=420)

    st.download_button(
        "📥 Baixar imagem",
        st.session_state.cotacao_img_bytes,
        file_name=f"Cotacao_{st.session_state.cotacao_dados['cliente']}.png",
        mime="image/png"
    )

    # Botão verde para WhatsApp
    if st.session_state.wa_link:
        st.markdown(
            f"""
            <a href="{st.session_state.wa_link}" target="_blank" style="text-decoration:none;">
                <button style="
                    background-color:#16a34a;
                    color:white;
                    border:none;
                    padding:14px 18px;
                    font-size:16px;
                    border-radius:12px;
                    cursor:pointer;
                    width:100%;
                    font-weight:700;">
                    ✅ ENVIAR COTAÇÃO (WhatsApp)
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )
        st.caption("O WhatsApp abre com a mensagem pronta. Anexe a imagem baixada e envie.")
else:
    st.caption("Para gerar: preencha Cliente + Consultor, escolha veículo, clique Buscar FIPE e depois Gerar Cotação.")
