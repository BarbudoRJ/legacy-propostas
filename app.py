import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
from datetime import datetime # Importando biblioteca de data

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Legacy Premium", page_icon="💎", layout="centered")

# --- FORMATADOR DE TELEFONE ---
def formatar_telefone(tel):
    if not tel: return ""
    nums = "".join(filter(str.isdigit, tel))
    if len(nums) == 11:
        return f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
    elif len(nums) == 10:
        return f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
    return tel

# --- LÓGICA DE CÁLCULO ---
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

# --- MOTOR GRÁFICO ---
def criar_proposta(dados):
    W, H = 1080, 1350

    # --- FUNDO ---
    try:
        bg = Image.open("fundo.png").convert("RGBA")
        bg = bg.resize((W, H), Image.LANCZOS)
        img = bg.copy()
    except:
        img = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    base_draw = ImageDraw.Draw(img)

    # --- CORES ---
    LARANJA     = (243, 112, 33, 255)
    AZUL_LEGACY = (0, 35, 95, 255)
    PRETO       = (15, 15, 15, 255)
    CINZA_TEXTO = (90, 90, 90, 255)
    BRANCO      = (255, 255, 255, 255)

    # Esquelmorfo
    PAINEL_FILL   = (255, 255, 255, 210)
    PAINEL_BORDA  = (220, 220, 220, 255)
    PAINEL_BRILHO = (255, 255, 255, 120)

    VERDE_BADGE = (40, 170, 90, 255)
    VERM_BADGE  = (220, 60, 60, 255)

    # --- FONTES ---
    try:
        f_titulo      = ImageFont.truetype("bold.ttf", 46)
        f_subtitulo   = ImageFont.truetype("bold.ttf", 34)
        f_texto       = ImageFont.truetype("regular.ttf", 28)
        f_negrito     = ImageFont.truetype("bold.ttf", 28)
        f_head_planos = ImageFont.truetype("bold.ttf", 26)
        f_preco_num   = ImageFont.truetype("bold.ttf", 34)
        f_preco_rs    = ImageFont.truetype("regular.ttf", 22)
        f_footer      = ImageFont.truetype("bold.ttf", 22)
        f_small       = ImageFont.truetype("regular.ttf", 22)
    except:
        f_titulo = f_subtitulo = f_texto = f_negrito = f_head_planos = f_preco_num = f_preco_rs = f_footer = f_small = ImageFont.load_default()

    MARGEM_X = 70
    CENTRO_X = W // 2

    # =========================================================
    # 1) TOPO FIXO
    # =========================================================
    y = 175
    
    # Lado Esquerdo: "Proposta para"
    base_draw.text((MARGEM_X, y), "Proposta para:", font=f_texto, fill=CINZA_TEXTO)
    
    # Lado Direito: DATA AUTOMÁTICA
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    # Alinhado à direita (W - Margem)
    base_draw.text((W - MARGEM_X, y), f"Data: {data_hoje}", font=f_texto, fill=CINZA_TEXTO, anchor="ra")
    
    # Nome do Cliente
    base_draw.text((MARGEM_X + 215, y), dados["cliente"], font=f_negrito, fill=AZUL_LEGACY)
    y += 42

    # Consultor + Telefone
    texto_consultor = f"Consultor(a): {dados['consultor']}"
    if dados['telefone']:
        texto_consultor += f"   •   {dados['telefone']}"

    base_draw.text((MARGEM_X, y), texto_consultor, font=f_negrito, fill=LARANJA)
    y += 55

    base_draw.line([(MARGEM_X, y), (W - MARGEM_X, y)], fill=(210, 210, 210, 255), width=2)
    y += 35

    base_draw.text((CENTRO_X, y), dados["modelo"], font=f_subtitulo, fill=PRETO, anchor="ma")
    y += 46

    base_draw.text((CENTRO_X, y), f"Ano: {dados['ano']}  |  FIPE: {dados['fipe']}", font=f_titulo, fill=AZUL_LEGACY, anchor="ma")
    y += 70

    # Badge adesão
    badge_w, badge_h = 520, 64
    bx0 = CENTRO_X - badge_w // 2
    by0 = y
    base_draw.rounded_rectangle([bx0, by0, bx0 + badge_w, by0 + badge_h], radius=16, fill=(245, 245, 245, 235))
    base_draw.text((CENTRO_X, by0 + 20), f"Adesão: R$ {dados['adesao']}", font=f_subtitulo, fill=PRETO, anchor="ma")

    # =========================================================
    # 2) PAINEL ESQUELMORFO
    # =========================================================
    painel_x0, painel_x1 = 55, W - 55
    painel_y0, painel_y1 = 650, H - 40 
    painel_w = painel_x1 - painel_x0
    painel_h = painel_y1 - painel_y0

    # Sombra
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([painel_x0+6, painel_y0+10, painel_x1+6, painel_y1+10], radius=28, fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, shadow)

    # Painel
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([painel_x0, painel_y0, painel_x1, painel_y1], radius=28, fill=PAINEL_FILL, outline=PAINEL_BORDA, width=2)
    pd.rounded_rectangle([painel_x0+2, painel_y0+2, painel_x1-2, painel_y0 + int(painel_h*0.22)], radius=26, fill=PAINEL_BRILHO)

    img = Image.alpha_composite(img, panel)
    draw = ImageDraw.Draw(img)

    # =========================================================
    # 3) GRID DE PLANOS + BENEFÍCIOS
    # =========================================================
    itens = [
        ("Rastreamento", ["✔", "✔", "✔", "✔"]),
        ("Reboque",      ["200", "400", "1mil", "1mil"]),
        ("Roubo/Furto",  ["✖", "✔", "✔", "✔"]),
        ("Colisão/PT",   ["✖", "✖", "✔", "✔"]),
        ("Terceiros",    ["✖", "✖", "✔", "✔"]),
        ("Vidros",       ["✖", "✖", "✔", "✔"]),
        ("Carro Res.",   ["✖", "✖", "10d", "30d"]),
        ("Gás (GNV)",    ["✖", "✖", "✖", "✔"]),
    ]

    pad = 28
    inner_x0 = painel_x0 + pad
    inner_x1 = painel_x1 - pad
    inner_y0 = painel_y0 + 20
    inner_y1 = painel_y1 - 18
    inner_h = inner_y1 - inner_y0
    inner_w = inner_x1 - inner_x0

    head_h   = 40
    line_h   = 18
    preco_h  = 78
    gap1     = 18
    footer_h = 72
    gap2     = 12

    lista_h = inner_h - (head_h + line_h + preco_h + gap1 + footer_h + gap2)
    row_h = max(42, int(lista_h / len(itens)))

    label_w = 310
    col_w = (inner_w - label_w) / 4
    x_label = inner_x0 + 8
    x_cols = [inner_x0 + label_w + (i * col_w) + (col_w / 2) for i in range(4)]

    # --- CABEÇALHO COLUNAS (FUNDO LARANJA + TEXTO BRANCO) ---
    y0 = inner_y0
    colunas = ["Econ.", "Básico", "Plus", "Prem."]
    
    # Tarja Laranja atrás dos títulos para o branco aparecer
    # Desenhamos uma barra arredondada só no topo
    draw.rounded_rectangle([inner_x0, y0, inner_x1, y0 + head_h + 5], radius=8, fill=LARANJA)

    for i, col in enumerate(colunas):
        # Texto BRANCO sobre a tarja Laranja
        draw.text((x_cols[i], y0 + 12), col, font=f_head_planos, fill=BRANCO, anchor="mm")

    # Linha Preta (Abaixo da tarja)
    y_line = y0 + head_h + 5
    draw.line([(inner_x0, y_line), (inner_x1, y_line)], fill=PRETO, width=3)

    # Preços
    y_preco = y_line + 18
    for i, p in enumerate(dados["precos"]):
        valor = p.replace("R$ ", "")
        draw.text((x_cols[i], y_preco + 10), "R$", font=f_preco_rs, fill=PRETO, anchor="mm")
        draw.text((x_cols[i], y_preco + 44), valor, font=f_preco_num, fill=PRETO, anchor="mm")

    y_div = y_preco + preco_h
    draw.line([(inner_x0, y_div), (inner_x1, y_div)], fill=(210, 210, 210, 255), width=2)

    # Funções de Desenho
    def draw_badge(x, y, kind):
        r = 14
        if kind == "check":
            draw.ellipse([x-r, y-r, x+r, y+r], fill=VERDE_BADGE)
            draw.line([(x-6, y+1), (x-1, y+6)], fill=(255,255,255,255), width=3)
            draw.line([(x-1, y+6), (x+8, y-5)], fill=(255,255,255,255), width=3)
        elif kind == "x":
            draw.ellipse([x-r, y-r, x+r, y+r], fill=VERM_BADGE)
            draw.line([(x-6, y-6), (x+6, y+6)], fill=(255,255,255,255), width=3)
            draw.line([(x+6, y-6), (x-6, y+6)], fill=(255,255,255,255), width=3)

    def draw_pill(x, y, txt):
        tw, th = draw.textbbox((0,0), txt, font=f_negrito)[2:]
        pw = max(54, tw + 26)
        ph = 32
        px0, py0 = x - pw/2, y - ph/2
        draw.rounded_rectangle([px0, py0, px0+pw, py0+ph], radius=14, fill=(245,245,245,255), outline=(215,215,215,255), width=2)
        draw.text((x, y-1), txt, font=f_negrito, fill=PRETO, anchor="mm")

    # Lista
    y_list = y_div + gap1
    for nome, status_lista in itens:
        y_mid = y_list + (row_h // 2)
        draw.text((x_label, y_mid), nome, font=f_texto, fill=CINZA_TEXTO, anchor="lm")
        for i, st in enumerate(status_lista):
            cx = x_cols[i]
            if st == "✔": draw_badge(cx, y_mid, "check")
            elif st == "✖": draw_badge(cx, y_mid, "x")
            else: draw_pill(cx, y_mid, st)
        y_list += row_h

    # Rodapé
    y_footer = inner_y1 - footer_h + 10
    draw.text((CENTRO_X, y_footer + 10), "⚠ PAGAMENTO ANTECIPADO GERA DESCONTO ⚠", font=f_footer, fill=LARANJA, anchor="mm")
    draw.text((CENTRO_X, y_footer + 42), "A COTAÇÃO PODE SOFRER ALTERAÇÕES BASEADAS NOS VALORES VIGENTES", font=f_small, fill=AZUL_LEGACY, anchor="mm")

    return img.convert("RGB")

# --- INTERFACE ---
st.title("🛡️ Gerador Legacy Premium")

c1, c2 = st.columns(2)
cliente = c1.text_input("Nome do Cliente")
modelo = c2.text_input("Modelo do Veículo")

c3, c4 = st.columns(2)
consultor = c3.text_input("Nome do Consultor")
telefone = c4.text_input("WhatsApp Consultor (ex: 21999998888)")

c5, c6, c7, c8 = st.columns(4)
ano = c5.text_input("Ano")
fipe = c6.number_input("Valor FIPE", step=100.0)
regiao = c7.selectbox("Região", ["Capital", "Serrana"])
adesao = c8.text_input("Adesão (R$)", value="300,00")

if st.button("GERAR COTAÇÃO", type="primary"):
    if fipe > 0 and cliente:
        with st.spinner("Gerando imagem em alta definição..."):
            precos = calcular_mensalidades(fipe, regiao)
            if precos:
                # Formata telefone
                tel_formatado = formatar_telefone(telefone)
                
                dados = {
                    "cliente": cliente, 
                    "consultor": consultor, 
                    "telefone": tel_formatado,
                    "modelo": modelo, 
                    "ano": ano, 
                    "fipe": f"R$ {fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
                    "precos": precos, 
                    "adesao": adesao
                }
                img = criar_proposta(dados)
                st.image(img, caption="Layout Premium", width=400)
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 BAIXAR IMAGEM", buf.getvalue(), f"Cotacao_{cliente}.png", "image/png")
    else:
        st.warning("Preencha FIPE e Nome do Cliente.")
