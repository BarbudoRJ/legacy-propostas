import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
from datetime import datetime
import urllib.parse
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Legacy Premium", page_icon="💎", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; font-weight: bold; }
    
    /* Estilo do botão HTML personalizado */
    .share-btn {
        background-color: #25D366; /* Verde WhatsApp */
        color: white;
        padding: 14px 20px;
        text-align: center;
        text-decoration: none;
        display: block;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        width: 100%;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 10px;
    }
    .share-btn:hover { background-color: #128C7E; }
    .share-btn:active { transform: scale(0.98); }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def formatar_telefone(tel):
    if not tel: return ""
    nums = "".join(filter(str.isdigit, tel))
    if len(nums) == 11: return f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
    elif len(nums) == 10: return f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
    return tel

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
    try:
        bg = Image.open("fundo.png").convert("RGBA")
        bg = bg.resize((W, H), Image.LANCZOS)
        img = bg.copy()
    except:
        img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    
    base_draw = ImageDraw.Draw(img)
    # CORES
    LARANJA, AZUL_LEGACY = (243, 112, 33, 255), (0, 35, 95, 255)
    PRETO, CINZA_TEXTO, BRANCO = (15, 15, 15, 255), (90, 90, 90, 255), (255, 255, 255, 255)
    PAINEL_FILL, PAINEL_BORDA, PAINEL_BRILHO = (255, 255, 255, 215), (220, 220, 220, 255), (255, 255, 255, 120)
    VERDE_BADGE, VERM_BADGE = (40, 170, 90, 255), (220, 60, 60, 255)

    # FONTES
    try:
        f_titulo = ImageFont.truetype("bold.ttf", 46)
        f_subtitulo = ImageFont.truetype("bold.ttf", 34)
        f_texto = ImageFont.truetype("regular.ttf", 28)
        f_negrito = ImageFont.truetype("bold.ttf", 28)
        f_head_planos = ImageFont.truetype("bold.ttf", 26)
        f_preco_num = ImageFont.truetype("bold.ttf", 34)
        f_preco_rs = ImageFont.truetype("regular.ttf", 22)
        f_footer = ImageFont.truetype("bold.ttf", 22)
        f_small = ImageFont.truetype("regular.ttf", 20)
        f_moto = ImageFont.truetype("bold.ttf", 24)
    except:
        f_titulo = f_subtitulo = f_texto = f_negrito = f_head_planos = f_preco_num = f_preco_rs = f_footer = f_small = f_moto = ImageFont.load_default()

    MARGEM_X, CENTRO_X = 70, W // 2

    # 1) TOPO
    y = 175
    base_draw.text((MARGEM_X, y), "Proposta para:", font=f_texto, fill=CINZA_TEXTO)
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    base_draw.text((W - MARGEM_X, y), f"Data: {data_hoje}", font=f_texto, fill=CINZA_TEXTO, anchor="ra")
    base_draw.text((MARGEM_X + 215, y), dados["cliente"], font=f_negrito, fill=AZUL_LEGACY)
    y += 42
    texto_consultor = f"Consultor(a): {dados['consultor']}"
    if dados['telefone']: texto_consultor += f"   •   {dados['telefone']}"
    base_draw.text((MARGEM_X, y), texto_consultor, font=f_negrito, fill=LARANJA)
    y += 55
    base_draw.line([(MARGEM_X, y), (W - MARGEM_X, y)], fill=(210, 210, 210, 255), width=2)
    y += 35
    base_draw.text((CENTRO_X, y), dados["modelo"], font=f_subtitulo, fill=PRETO, anchor="ma")
    y += 46
    base_draw.text((CENTRO_X, y), f"Ano: {dados['ano']}  |  FIPE: {dados['fipe']}", font=f_titulo, fill=AZUL_LEGACY, anchor="ma")
    y += 70
    badge_w, badge_h = 520, 64
    bx0, by0 = CENTRO_X - badge_w // 2, y
    base_draw.rounded_rectangle([bx0, by0, bx0 + badge_w, by0 + badge_h], radius=16, fill=(245, 245, 245, 235))
    base_draw.text((CENTRO_X, by0 + 20), f"Adesão: R$ {dados['adesao']}", font=f_subtitulo, fill=PRETO, anchor="ma")

    # 2) PAINEL
    painel_x0, painel_x1 = 55, W - 55
    painel_y0, painel_y1 = 650, H - 40 
    painel_h = painel_y1 - painel_y0
    
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([painel_x0+6, painel_y0+10, painel_x1+6, painel_y1+10], radius=28, fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, shadow)

    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([painel_x0, painel_y0, painel_x1, painel_y1], radius=28, fill=PAINEL_FILL, outline=PAINEL_BORDA, width=2)
    pd.rounded_rectangle([painel_x0+2, painel_y0+2, painel_x1-2, painel_y0 + int(painel_h*0.22)], radius=26, fill=PAINEL_BRILHO)
    img = Image.alpha_composite(img, panel)
    draw = ImageDraw.Draw(img)

    # 3) GRID
    itens = [
        ("Rastreamento", ["✔", "✔", "✔", "✔"]), ("Reboque", ["200", "400", "1mil", "1mil"]),
        ("Roubo/Furto", ["✖", "✔", "✔", "✔"]), ("Colisão/PT", ["✖", "✖", "✔", "✔"]),
        ("Terceiros", ["✖", "✖", "✔", "✔"]), ("Vidros", ["✖", "✖", "✔", "✔"]),
        ("Carro Res.", ["✖", "✖", "10d", "30d"]), ("Gás (GNV)", ["✖", "✖", "✖", "✔"]),
    ]
    pad = 28
    inner_x0, inner_x1 = painel_x0 + pad, painel_x1 - pad
    inner_y0, inner_y1 = painel_y0 + 20, painel_y1 - 18
    inner_w, inner_h = inner_x1 - inner_x0, inner_y1 - inner_y0
    head_h, line_h, preco_h, footer_h = 40, 18, 78, 110
    lista_h = inner_h - (head_h + line_h + preco_h + footer_h + 30)
    row_h = max(42, int(lista_h / len(itens)))
    label_w = 310
    col_w = (inner_w - label_w) / 4
    x_label = inner_x0 + 8
    x_cols = [inner_x0 + label_w + (i * col_w) + (col_w / 2) for i in range(4)]
    y0 = inner_y0

    draw.rounded_rectangle([inner_x0, y0, inner_x1, y0 + head_h + 5], radius=8, fill=LARANJA)
    for i, col in enumerate(["Econ.", "Básico", "Plus", "Prem."]):
        draw.text((x_cols[i], y0 + 12), col, font=f_head_planos, fill=BRANCO, anchor="mm")
    y_line = y0 + head_h + 5
    draw.line([(inner_x0, y_line), (inner_x1, y_line)], fill=PRETO, width=3)
    
    y_preco = y_line + 18
    for i, p in enumerate(dados["precos"]):
        valor = p.replace("R$ ", "")
        draw.text((x_cols[i], y_preco + 10), "R$", font=f_preco_rs, fill=PRETO, anchor="mm")
        draw.text((x_cols[i], y_preco + 44), valor, font=f_preco_num, fill=PRETO, anchor="mm")
    y_div = y_preco + preco_h
    draw.line([(inner_x0, y_div), (inner_x1, y_div)], fill=(210, 210, 210, 255), width=2)

    def draw_badge(x, y, kind):
        r, fill_c = (14, VERDE_BADGE) if kind == "check" else (14, VERM_BADGE)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=fill_c)
        pts = [(x-6, y+1), (x-1, y+6), (x+8, y-5)] if kind == "check" else [(x-6, y-6), (x+6, y+6), (x+6, y-6), (x-6, y+6)]
        if kind == "check":
            draw.line(pts[0:2], fill=BRANCO, width=3); draw.line(pts[1:3], fill=BRANCO, width=3)
        else:
            draw.line(pts[0:2], fill=BRANCO, width=3); draw.line(pts[2:4], fill=BRANCO, width=3)
            
    def draw_pill(x, y, txt):
        tw, _ = draw.textbbox((0,0), txt, font=f_negrito)[2:]
        pw = max(54, tw + 26)
        px0 = x - pw/2
        draw.rounded_rectangle([px0, y-16, px0+pw, y+16], radius=14, fill=(245,245,245,255), outline=(215,215,215,255), width=2)
        draw.text((x, y-1), txt, font=f_negrito, fill=PRETO, anchor="mm")

    y_list = y_div + 18
    for nome, status_lista in itens:
        y_mid = y_list + (row_h // 2)
        draw.text((x_label, y_mid), nome, font=f_texto, fill=CINZA_TEXTO, anchor="lm")
        for i, st in enumerate(status_lista):
            if st == "✔": draw_badge(x_cols[i], y_mid, "check")
            elif st == "✖": draw_badge(x_cols[i], y_mid, "x")
            else: draw_pill(x_cols[i], y_mid, st)
        y_list += row_h

    # RODAPÉ
    y_footer_base = inner_y1 - 10
    draw.text((CENTRO_X, y_footer_base), "A COTAÇÃO PODE SOFRER ALTERAÇÕES BASEADAS NOS VALORES VIGENTES", font=f_small, fill=AZUL_LEGACY, anchor="ms")
    y_moto = y_footer_base - 35
    draw.rounded_rectangle([CENTRO_X - 420, y_moto - 32, CENTRO_X + 420, y_moto + 8], radius=10, fill=(240, 240, 250, 255), outline=AZUL_LEGACY, width=1)
    draw.text((CENTRO_X, y_moto - 12), "⚡ CONHEÇA OS NOSSOS PLANOS PARA PROTEÇÃO DE MOTOS ELÉTRICAS ⚡", font=f_moto, fill=AZUL_LEGACY, anchor="mm")
    y_promo = y_moto - 50
    draw.text((CENTRO_X, y_promo), "⚠ PAGAMENTO ANTECIPADO GERA DESCONTO ⚠", font=f_footer, fill=LARANJA, anchor="ms")
    return img.convert("RGB")

# --- INTERFACE ---
st.title("🛡️ Gerador Legacy Premium")

c1, c2 = st.columns(2)
cliente = c1.text_input("Nome do Cliente")
# (Removemos o input de telefone do cliente para focar no compartilhamento nativo)

c3, c4 = st.columns(2)
modelo = c3.text_input("Modelo do Veículo")
ano = c4.text_input("Ano")

c5, c6 = st.columns(2)
consultor = c5.text_input("Nome do Consultor")
telefone_consultor = c6.text_input("WhatsApp Consultor")

c7, c8, c9 = st.columns(3)
fipe = c7.number_input("Valor FIPE", step=100.0)
regiao = c8.selectbox("Região", ["Capital", "Serrana"])
adesao = c9.text_input("Adesão (R$)", value="300,00")

if st.button("GERAR COTAÇÃO", type="primary"):
    if fipe > 0 and cliente:
        with st.spinner("Gerando imagem..."):
            precos = calcular_mensalidades(fipe, regiao)
            if precos:
                dados = {
                    "cliente": cliente, "consultor": consultor, 
                    "telefone": formatar_telefone(telefone_consultor),
                    "modelo": modelo, "ano": ano, 
                    "fipe": f"R$ {fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
                    "precos": precos, "adesao": adesao
                }
                img = criar_proposta(dados)
                
                # Prepara Base64 para JS
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                img_bytes = buf.getvalue()
                b64_img = base64.b64encode(img_bytes).decode()
                
                st.markdown("---")
                st.success("✅ Sucesso!")
                col_img, col_btn = st.columns([1, 1])
                
                with col_img:
                    st.image(img, caption="Prévia", width=350)
                
                with col_btn:
                    # Botão HTML/JS para Compartilhamento Nativo (Mobile)
                    share_code = f"""
                    <script>
                    async function shareImage() {{
                        const b64 = "{b64_img}";
                        const blob = await (await fetch(`data:image/png;base64,${{b64}}`)).blob();
                        const file = new File([blob], "cotacao_{cliente}.png", {{ type: "image/png" }});
                        
                        if (navigator.share) {{
                            try {{
                                await navigator.share({{
                                    files: [file],
                                    title: 'Cotação Legacy',
                                    text: 'Olá {cliente}, segue sua cotação Legacy!'
                                }});
                            }} catch (err) {{
                                console.log('Compartilhamento cancelado');
                            }}
                        }} else {{
                            alert('⚠️ Função disponível apenas no Celular (Android/iOS).\\n\\nNo computador, clique com botão direito na imagem e Salvar, ou use o botão de Download.');
                        }}
                    }}
                    </script>
                    <button onclick="shareImage()" class="share-btn">
                        📱 ENVIAR IMAGEM (Abrir WhatsApp)
                    </button>
                    """
                    st.components.v1.html(share_code, height=100)
                    
                    st.download_button(
                        label="📥 BAIXAR NO COMPUTADOR",
                        data=img_bytes,
                        file_name=f"Cotacao_{cliente}.png",
                        mime="image/png"
                    )
            else:
                st.error("FIPE fora da tabela.")
    else:
        st.warning("Preencha os dados.")
