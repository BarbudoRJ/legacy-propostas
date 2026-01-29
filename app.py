import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerador Legacy Story", page_icon="📱", layout="centered")

# --- AUTO-DOWNLOAD DE FONTES (ROBOTO) ---
# Baixa as fontes do Google na primeira vez para garantir que o texto fique bonito
def garantir_fontes():
    urls = {
        "Roboto-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Bold.ttf",
        "Roboto-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf"
    }
    for nome_arquivo, url in urls.items():
        if not os.path.exists(nome_arquivo):
            try:
                r = requests.get(url)
                with open(nome_arquivo, 'wb') as f:
                    f.write(r.content)
            except: pass

garantir_fontes()

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
    
    # Cores Oficiais
    LARANJA = (243, 112, 33) 
    CINZA = (50, 50, 50)
    CLARO = (240, 240, 240)
    BRANCO = (255, 255, 255)
    VERDE = (0, 180, 0)
    VERMELHO = (200, 0, 0)

    # Carregar Fontes (Seguro contra erros)
    try:
        f_h1 = ImageFont.truetype("Roboto-Bold.ttf", 70)
        f_h2 = ImageFont.truetype("Roboto-Bold.ttf", 45)
        f_bold = ImageFont.truetype("Roboto-Bold.ttf", 35)
        f_reg = ImageFont.truetype("Roboto-Regular.ttf", 35)
        f_check = ImageFont.truetype("Roboto-Regular.ttf", 55)
    except:
        f_h1 = f_h2 = f_bold = f_reg = f_check = ImageFont.load_default()

    # 1. CABEÇALHO E LOGO
    draw.rectangle([(0, 0), (W, 250)], fill=LARANJA)
    try:
        # Tenta carregar o logo.png se existir
        logo = Image.open("logo.png").convert("RGBA")
        ratio = 200 / logo.height
        logo = logo.resize((int(logo.width * ratio), 200))
        img.paste(logo, ((W - logo.width)//2, 25), logo)
    except:
        # Se não tiver logo, escreve texto
        draw.text((W//2, 100), "LOGO LEGACY", font=f_h1, fill=BRANCO, anchor="mm")

    # 2. CLIENTE E DADOS DO CARRO
    y = 280
    draw.text((50, y), f"Proposta para: {dados['cliente']}", font=f_h2, fill=CINZA)
    
    y += 80
    draw.rectangle([(40, y), (W-40, y+280)], fill=CLARO)
    
    # Texto do carro centralizado
    draw.text((W//2, y+50), f"{dados['modelo']}\n{dados['ano']}", font=f_h2, fill=LARANJA, anchor="ma", align="center")
    draw.text((W//2, y+180), f"FIPE: {dados['fipe']}", font=f_h1, fill=CINZA, anchor="ma")

    # 3. TABELA DE PREÇOS
    y += 350
    # AQUI ESTÁ O AJUSTE: Margem esquerda maior (300px) para caber os nomes
    margem_nomes = 300
    largura_col = (W - margem_nomes) // 4
    
    colunas = ["Econ.", "Básico", "Plus", "Prem."]
    
    # Títulos das Colunas
    for i, col in enumerate(colunas):
        x = margem_nomes + (i * largura_col) + (largura_col // 2)
        draw.text((x, y), col, font=f_bold, fill=LARANJA, anchor="ma")
    
    y += 60
    draw.line([(40, y), (W-40, y)], fill=CINZA, width=3)
    
    # Valores Mensais
    y += 30
    for i, preco in enumerate(dados['precos']):
        x = margem_nomes + (i * largura_col) + (largura_col // 2)
        val = preco.replace("R$ ", "")
        draw.text((x, y), f"R$\n{val}", font=f_h2, fill=CINZA, anchor="ma", align="center")

    # 4. TABELA DE BENEFÍCIOS (GRID)
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
        # Nome do benefício na esquerda (na área de margem)
        draw.text((50, y+10), nome, font=f_reg, fill=CINZA)
        
        # Ícones nas colunas
        for i, status in enumerate(status_lista):
            x = margem_nomes + (i * largura_col) + (largura_col // 2)
            
            # Cores dinâmicas
            if status == "✔": cor = VERDE
            elif status == "✖": cor = VERMELHO
            else: cor = CINZA # Para texto como "200"
            
            # Fonte dinâmica (Check é maior)
            font = f_check if status in ["✔", "✖"] else f_bold
            
            draw.text((x, y), status, font=font, fill=cor, anchor="ma")
        
        y += 90 # Próxima linha

    # 5. RODAPÉ DE AVISO
    draw.rectangle([(0, H-250), (W, H)], fill=LARANJA)
    aviso = "⚠ PAGAMENTO ANTECIPADO ⚠\nGARANTE DESCONTO NA MENSALIDADE!"
    draw.multiline_text((W//2, H-125), aviso, font=f_h2, fill=BRANCO, anchor="mm", align="center")

    return img

# --- INTERFACE DO USUÁRIO ---
st.title("📱 Gerador Legacy Story")
c1, c2 = st.columns(2)
cliente = c1.text_input("Nome do Cliente")
modelo = c2.text_input("Modelo Veículo")
c3, c4, c5 = st.columns(3)
ano = c3.text_input("Ano")
fipe = c4.number_input("Valor FIPE", step=100.0)
regiao = c5.selectbox("Região", ["Capital", "Serrana"])

if st.button("GERAR IMAGEM AGORA", type="primary"):
    if fipe > 0 and cliente:
        with st.spinner("Desenhando proposta..."):
            precos = calcular_mensalidades(fipe, regiao)
            if precos:
                # Prepara dados
                dados = {
                    "cliente": cliente, 
                    "modelo": modelo, 
                    "ano": ano, 
                    "fipe": f"R$ {fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
                    "precos": precos
                }
                
                # Gera imagem
                img = criar_proposta(dados)
                
                # Mostra na tela
                st.image(img, caption="Visualização (Role para ver tudo)", width=350)
                
                # Prepara Download
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 BAIXAR PARA WHATSAPP", buf.getvalue(), f"Proposta_{cliente}.png", "image/png")
    else:
        st.warning("Por favor, preencha o Nome do Cliente e o Valor FIPE.")
