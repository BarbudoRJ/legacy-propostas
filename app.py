import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Legacy Story", page_icon="📱", layout="centered")

# --- FUNÇÃO PARA BAIXAR FONTES AUTOMATICAMENTE ---
def garantir_fontes():
    # Links diretos do Google Fonts
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
            except:
                pass # Se der erro, usaremos a padrão

# Executa o download das fontes ao abrir o app
garantir_fontes()

# --- REGRAS DE NEGÓCIO ---
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
    idx_regiao = 0 if regiao == "Capital" else 1
    valores = None
    for teto, precos in tabela.items():
        if fipe <= teto:
            valores = precos[idx_regiao]
            break
    if not valores: return None
    return [f"R$ {v:.2f}".replace('.', ',') for v in valores]

# --- GERADOR DE IMAGEM 9:16 ---
def criar_proposta_automatica(dados):
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # CORES
    LARANJA = (243, 112, 33) 
    CINZA_ESC = (50, 50, 50)
    CINZA_CLARO = (240, 240, 240)
    BRANCO = (255, 255, 255)
    VERDE = (0, 180, 0)
    VERMELHO = (200, 0, 0)

    # --- FONTES (Agora busca do arquivo baixado) ---
    try:
        font_h1 = ImageFont.truetype("Roboto-Bold.ttf", 80)
        font_h2 = ImageFont.truetype("Roboto-Bold.ttf", 50)
        font_body = ImageFont.truetype("Roboto-Regular.ttf", 40)
        font_bold = ImageFont.truetype("Roboto-Bold.ttf", 40)
        font_small = ImageFont.truetype("Roboto-Regular.ttf", 30)
        font_check = ImageFont.truetype("Roboto-Regular.ttf", 60)
    except:
        font_h1 = font_h2 = font_body = font_bold = font_small = font_check = ImageFont.load_default()

    # 1. CABEÇALHO
    draw.rectangle([(0, 0), (W, 250)], fill=LARANJA)
    
    # Logo
    try:
        logo = Image.open("logo.png")
        if logo.mode != 'RGBA': logo = logo.convert('RGBA')
        ratio = 200 / logo.height
        new_size = (int(logo.width * ratio), 200)
        logo = logo.resize(new_size)
        img.paste(logo, ((W - new_size[0]) // 2, 25), logo)
    except:
        draw.text((W//2 - 200, 80), "LOGO AQUI", font=font_h2, fill=BRANCO)

    # 2. DADOS
    cursor_y = 280
    draw.text((50, cursor_y), f"Proposta para: {dados['cliente']}", font=font_h2, fill=CINZA_ESC)
    cursor_y += 80
    
    # Caixa cinza
    draw.rectangle([(50, cursor_y), (W-50, cursor_y + 280)], fill=CINZA_CLARO)
    
    # Texto Centralizado na Caixa
    texto_carro = f"{dados['modelo']}\n{dados['ano']}"
    draw.multiline_text((W//2, cursor_y + 40), texto_carro, font=font_h2, fill=LARANJA, anchor="ma", align="center")
    
    draw.text((W//2, cursor_y + 180), f"FIPE: {dados['fipe_texto']}", font=font_h1, fill=CINZA_ESC, anchor="ma")

    # 3. TABELA PREÇOS
    cursor_y += 350
    colunas = ["Econ.", "Básico", "Plus", "Premium"]
    largura_col = W // 4
    
    # Títulos das Colunas
    for i, col in enumerate(colunas):
        x_pos = i * largura_col + (largura_col//2)
        draw.text((x_pos, cursor_y), col, font=font_h2, fill=LARANJA, anchor="ma")
    
    cursor_y += 70
    draw.line([(50, cursor_y), (W-50, cursor_y)], fill=CINZA_ESC, width=3)
    cursor_y += 30

    # Valores
    precos = dados['lista_precos']
    for i, preco in enumerate(precos):
        x_pos = i * largura_col + (largura_col//2)
        valor_limpo = preco.replace("R$ ", "")
        draw.text((x_pos, cursor_y), f"R$\n{valor_limpo}", font=font_h2, fill=CINZA_ESC, anchor="ma", align="center")
    
    # 4. GRID BENEFÍCIOS
    cursor_y += 180
    beneficios = [
        ("Rastreamento", ["✔", "✔", "✔", "✔"]),
        ("Reboque", ["200", "400", "1mil", "1mil"]),
        ("Roubo/Furto", ["✖", "✔", "✔", "✔"]),
        ("Colisão/PT", ["✖", "✖", "✔", "✔"]),
        ("Terceiros/Vidros", ["✖", "✖", "✔", "✔"]),
        ("Carro Reserva", ["✖", "✖", "10d", "30d"]),
        ("Cob. GNV", ["✖", "✖", "✖", "✔"]),
    ]

    for nome, status_lista in beneficios:
        # Nome na esquerda
        draw.text((40, cursor_y + 15), nome, font=font_small, fill=CINZA_ESC, anchor="lm")
        
        # Ícones
        for i, status in enumerate(status_lista):
            x_pos = i * largura_col + (largura_col // 2)
            
            cor = VERDE if status == "✔" else VERMELHO if status == "✖" else CINZA_ESC
            fonte_uso = font_check if status in ["✔", "✖"] else font_bold
            
            draw.text((x_pos, cursor_y), status, font=fonte_uso, fill=cor, anchor="ma")
        
        cursor_y += 90

    # 5. RODAPÉ
    y_aviso = H - 250
    draw.rectangle([(0, y_aviso), (W, H)], fill=LARANJA)
    aviso = "⚠ PAGAMENTO ANTECIPADO ⚠\nGARANTE DESCONTO NA MENSALIDADE!"
    draw.multiline_text((W//2, y_aviso + 125), aviso, font=font_h2, fill=BRANCO, anchor="mm", align="center")

    return img

# --- INTERFACE ---
st.title("📱 Gerador Legacy (Story)")

col1, col2 = st.columns(2)
nome_cliente = col1.text_input("Nome do Cliente")
nome_consultor = col2.text_input("Nome do Consultor")

modelo = st.text_input("Modelo do Veículo")
c1, c2, c3 = st.columns(3)
ano = c1.text_input("Ano")
valor_fipe = c2.number_input("Valor FIPE", step=100.0)
regiao = c3.selectbox("Região", ["Capital", "Região Serrana"])

if st.button("GERAR PROPOSTA HD", type="primary"):
    if not valor_fipe or not nome_cliente:
        st.warning("Preencha FIPE e Nome do Cliente")
    else:
        precos = calcular_mensalidades(valor_fipe, regiao)
        if precos:
            dados = {"cliente": nome_cliente, "modelo": modelo, "ano": ano, "fipe_texto": f"R$ {valor_fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "lista_precos": precos}
            with st.spinner("Gerando imagem em alta definição..."):
                img_final = criar_proposta_automatica(dados)
                st.image(img_final, caption="Preview", width=350)
                
                buf = io.BytesIO()
                img_final.save(buf, format="PNG")
                st.download_button("📥 BAIXAR IMAGEM (HD)", data=buf.getvalue(), file_name=f"proposta_{nome_cliente}.png", mime="image/png")
        else:
            st.error("Valor FIPE fora da tabela.")
