import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerador Legacy Story", page_icon="📱", layout="centered")

# --- FUNÇÃO PARA ÍCONES BONITOS (Bolinhas) ---
def desenhar_icone(draw_obj, x, y, status, font_icon, verde, vermelho, branco, cinza, font_bold):
    if status == "✔":
        raio = 30
        draw_obj.ellipse([(x-raio, y-raio), (x+raio, y+raio)], fill=verde)
        draw_obj.text((x, y), "✔", font=font_icon, fill=branco, anchor="mm")
    elif status == "✖":
        raio = 30
        draw_obj.ellipse([(x-raio, y-raio), (x+raio, y+raio)], fill=vermelho)
        draw_obj.text((x, y), "✖", font=font_icon, fill=branco, anchor="mm")
    else:
        # Texto normal (ex: "200", "10d")
        draw_obj.text((x, y), status, font=font_bold, fill=cinza, anchor="ma")

# --- DESENHO DA IMAGEM ---
def criar_proposta(dados):
    W, H = 1080, 1920
    
    # 1. SETUP DO FUNDO
    try:
        # Tenta carregar fundo.jpg e redimensionar
        bg = Image.open("fundo.jpg").convert("RGBA")
        img = bg.resize((W, H), Image.LANCZOS)
    except:
        # Fundo branco de emergência
        img = Image.new('RGBA', (W, H), color=(255, 255, 255, 255))

    # Camada para transparências
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    draw = ImageDraw.Draw(img) # Draw principal

    # CORES
    LARANJA = (243, 112, 33, 255)
    CINZA = (50, 50, 50, 255)
    BRANCO = (255, 255, 255, 255)
    VERDE_VIVO = (0, 200, 0, 255)
    VERMELHO_VIVO = (220, 0, 0, 255)
    BRANCO_TRANSP = (255, 255, 255, 230) # Caixa quase sólida

    # FONTES LOCAIS
    try:
        f_h1 = ImageFont.truetype("bold.ttf", 70)
        f_h2 = ImageFont.truetype("bold.ttf", 45)
        f_body = ImageFont.truetype("regular.ttf", 35)
        f_bold = ImageFont.truetype("bold.ttf", 35)
        f_check = ImageFont.truetype("regular.ttf", 45) # Check menor para caber na bolinha
    except:
        f_h1 = f_h2 = f_body = f_bold = f_check = ImageFont.load_default()

    # --- COMEÇA O DESENHO ---

    # TOPO SÓLIDO
    draw.rectangle([(0, 0), (W, 250)], fill=LARANJA)
    try:
        logo = Image.open("logo.png").convert("RGBA")
        ratio = 200 / logo.height
        logo = logo.resize((int(logo.width * ratio), 200))
        img.paste(logo, ((W - logo.width)//2, 25), logo)
    except:
        draw.text((W//2, 100), "LOGO LEGACY", font=f_h1, fill=BRANCO, anchor="mm")

    # DADOS DO CLIENTE
    y = 280
    # Caixa transparente atrás dos dados
    draw_overlay.rectangle([(20, y), (W-20, y+140)], fill=BRANCO_TRANSP)
    draw.text((50, y+10), f"Cliente: {dados['cliente']}", font=f_h2, fill=CINZA)
    draw.text((50, y+70), f"Consultor: {dados['consultor']}", font=f_bold, fill=LARANJA)
    
    y += 160
    # Caixa transparente do carro
    draw_overlay.rectangle([(20, y), (W-20, y+220)], fill=BRANCO_TRANSP)
    draw.text((W//2, y+40), f"{dados['modelo']} ({dados['ano']})", font=f_h2, fill=CINZA, anchor="ma", align="center")
    draw.text((W//2, y+130), f"FIPE: {dados['fipe']}", font=f_h1, fill=LARANJA, anchor="ma")

    # ÁREA DA TABELA (Fundo transparente grande)
    y_table_start = y + 240
    draw_overlay.rectangle([(0, y_table_start), (W, H-250)], fill=BRANCO_TRANSP)

    y = y_table_start + 30
    # Destaque Adesão
    draw.text((W//2, y), f"Taxa de Adesão: R$ {dados['adesao']}", font=f_h2, fill=CINZA, anchor="ma")
    
    y += 70
    margem = 300
    w_col = (W - margem) // 4
    colunas = ["Econ.", "Básico", "Plus", "Prem."]
    
    # Cabeçalho
    for i, col in enumerate(colunas):
        x = margem + (i * w_col) + (w_col // 2)
        draw.text((x, y), col, font=f_bold, fill=LARANJA, anchor="ma")
    
    y += 50
    draw.line([(40, y), (W-40, y)], fill=CINZA, width=3)
    
    # Mensalidades
    y += 30
    for i, preco in enumerate(dados['precos']):
        x = margem + (i * w_col) + (w_col // 2)
        val = preco.replace("R$ ", "")
        draw.text((x, y), f"R$\n{val}", font=f_h2, fill=CINZA, anchor="ma", align="center")

    # BENEFÍCIOS COM ÍCONES NOVOS
    y += 180
    itens = [
        ("Rastreamento", ["✔", "✔", "✔", "✔"]),
        ("Reboque", ["200", "400", "1mil", "1mil"]),
        ("Roubo/Furto", ["✖", "✔", "✔", "✔"]),
        ("Colisão/PT", ["✖", "✖", "✔", "✔"]),
        ("Terceiros", ["✖", "✖", "✔", "✔"]),
        ("Vidros", ["✖", "✖", "✔", "✔"]),
        ("Carro Res.", ["✖", "✖", "10d", "30d"]),
        ("Gás (GNV)", ["✖", "✖", "✖", "✔"]),
    ]

    for nome, status_lista in itens:
        draw.text((40, y+10), nome, font=f_body, fill=CINZA)
        for i, status in enumerate(status_lista):
            x = margem + (i * w_col) + (w_col // 2)
            # Chama a função que desenha as bolinhas
            desenhar_icone(draw, x, y+25, status, f_check, VERDE_VIVO, VERMELHO_VIVO, BRANCO, CINZA, f_bold)
        y += 90

    # APLICAR TRANSARÊNCIA E RODAPÉ
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img) # Draw final

    # Rodapé Sólido
    draw.rectangle([(0, H-250), (W, H)], fill=LARANJA)
    aviso = "⚠ PAGAMENTO ANTECIPADO ⚠\nGARANTE DESCONTO NA MENSALIDADE!"
    draw.multiline_text((W//2, H-125), aviso, font=f_h2, fill=BRANCO, anchor="mm", align="center")

    return img.convert("RGB")

# --- CÁLCULO MENSALIDADE ---
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

# --- INTERFACE ---
st.title("📱 Gerador Legacy Oficial")
c1, c2 = st.columns(2)
cliente = c1.text_input("Nome do Cliente")
consultor = c2.text_input("Nome do Consultor")
modelo = st.text_input("Modelo do Veículo")
c3, c4, c5 = st.columns(3)
ano = c3.text_input("Ano")
fipe = c4.number_input("Valor FIPE", step=100.0)
regiao = c5.selectbox("Região", ["Capital", "Serrana"])
adesao = st.text_input("Valor da Adesão (R$)", value="300,00")

if st.button("GERAR PROPOSTA", type="primary"):
    if fipe > 0 and cliente and consultor:
        with st.spinner("Gerando..."):
            precos = calcular_mensalidades(fipe, regiao)
            if precos:
                dados = {"cliente": cliente, "consultor": consultor, "modelo": modelo, "ano": ano, "fipe": f"R$ {fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "precos": precos, "adesao": adesao}
                img = criar_proposta(dados)
                st.image(img, caption="Resultado", width=350)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 BAIXAR IMAGEM", buf.getvalue(), f"Proposta_{cliente}.png", "image/png")
    else:
        st.warning("Preencha Cliente, Consultor e FIPE.")
