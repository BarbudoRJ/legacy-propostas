import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import urllib.request # Usando biblioteca padrão para não dar erro

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerador Legacy Story", page_icon="📱", layout="centered")

# --- AUTO-DOWNLOAD DE FONTES (SEM DEPENDÊNCIAS EXTRAS) ---
def carregar_fontes():
    # Links diretos para fontes
    fontes = {
        "Roboto-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Bold.ttf",
        "Roboto-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf"
    }
    
    path_bold = "Roboto-Bold.ttf"
    path_reg = "Roboto-Regular.ttf"

    # Baixa se não existir
    for nome, url in fontes.items():
        if not os.path.exists(nome):
            try:
                urllib.request.urlretrieve(url, nome)
            except:
                pass # Se falhar, usa padrão

    try:
        return {
            "h1": ImageFont.truetype(path_bold, 70),
            "h2": ImageFont.truetype(path_bold, 45),
            "body": ImageFont.truetype(path_reg, 35),
            "bold": ImageFont.truetype(path_bold, 35),
            "check": ImageFont.truetype(path_reg, 55)
        }
    except:
        # Fallback (Fonte de emergência se o download falhar)
        p = ImageFont.load_default()
        return {"h1": p, "h2": p, "body": p, "bold": p, "check": p}

FONTES = carregar_fontes()

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

# --- DESENHO DA IMAGEM ---
def criar_proposta(dados):
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Cores
    LARANJA = (243, 112, 33) 
    CINZA = (50, 50, 50)
    CLARO = (240, 240, 240)
    BRANCO = (255, 255, 255)
    VERDE = (0, 180, 0)
    VERMELHO = (200, 0, 0)

    # 1. TOPO (LOGO)
    draw.rectangle([(0, 0), (W, 250)], fill=LARANJA)
    try:
        logo = Image.open("logo.png").convert("RGBA")
        ratio = 200 / logo.height
        logo = logo.resize((int(logo.width * ratio), 200))
        img.paste(logo, ((W - logo.width)//2, 25), logo)
    except:
        draw.text((W//2, 100), "LOGO LEGACY", font=FONTES['h1'], fill=BRANCO, anchor="mm")

    # 2. INFORMAÇÕES (CONSULTOR, CLIENTE, ADESÃO)
    y = 280
    
    # Linha 1: Cliente e Consultor
    draw.text((50, y), f"Cliente: {dados['cliente']}", font=FONTES['h2'], fill=CINZA)
    y += 60
    draw.text((50, y), f"Consultor: {dados['consultor']}", font=FONTES['bold'], fill=LARANJA)
    
    y += 70
    draw.rectangle([(40, y), (W-40, y+220)], fill=CLARO)
    
    # Bloco Carro
    draw.text((W//2, y+40), f"{dados['modelo']} ({dados['ano']})", font=FONTES['h2'], fill=CINZA, anchor="ma", align="center")
    draw.text((W//2, y+130), f"FIPE: {dados['fipe']}", font=FONTES['h1'], fill=LARANJA, anchor="ma")

    # 3. TABELA DE PREÇOS
    y += 260
    
    # Destaque Adesão
    draw.text((W//2, y), f"Taxa de Adesão: R$ {dados['adesao']}", font=FONTES['h2'], fill=CINZA, anchor="ma")
    
    y += 70
    margem_nomes = 300
    largura_col = (W - margem_nomes) // 4
    colunas = ["Econ.", "Básico", "Plus", "Prem."]
    
    # Cabeçalho
    for i, col in enumerate(colunas):
        x = margem_nomes + (i * largura_col) + (largura_col // 2)
        draw.text((x, y), col, font=FONTES['bold'], fill=LARANJA, anchor="ma")
    
    y += 50
    draw.line([(40, y), (W-40, y)], fill=CINZA, width=3)
    
    # Mensalidades
    y += 30
    for i, preco in enumerate(dados['precos']):
        x = margem_nomes + (i * largura_col) + (largura_col // 2)
        val = preco.replace("R$ ", "")
        draw.text((x, y), f"R$\n{val}", font=FONTES['h2'], fill=CINZA, anchor="ma", align="center")

    # 4. BENEFÍCIOS
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
        draw.text((50, y+10), nome, font=FONTES['body'], fill=CINZA)
        for i, status in enumerate(status_lista):
            x = margem_nomes + (i * largura_col) + (largura_col // 2)
            cor = VERDE if status == "✔" else VERMELHO if status == "✖" else CINZA
            font = FONTES['check'] if status in ["✔", "✖"] else FONTES['bold']
            draw.text((x, y), status, font=font, fill=cor, anchor="ma")
        y += 85

    # 5. RODAPÉ
    draw.rectangle([(0, H-250), (W, H)], fill=LARANJA)
    aviso = "⚠ PAGAMENTO ANTECIPADO ⚠\nGARANTE DESCONTO NA MENSALIDADE!"
    draw.multiline_text((W//2, H-125), aviso, font=FONTES['h2'], fill=BRANCO, anchor="mm", align="center")

    return img

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
                dados = {
                    "cliente": cliente, "consultor": consultor,
                    "modelo": modelo, "ano": ano, 
                    "fipe": f"R$ {fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
                    "precos": precos, "adesao": adesao
                }
                img = criar_proposta(dados)
                st.image(img, caption="Resultado", width=350)
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 BAIXAR IMAGEM", buf.getvalue(), f"Proposta_{cliente}.png", "image/png")
    else:
        st.warning("Preencha Cliente, Consultor e FIPE.")
