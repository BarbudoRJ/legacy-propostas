import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerador Legacy Pro", page_icon="🛡️", layout="centered")

# --- FUNÇÃO ÍCONES ---
def desenhar_icone(draw_obj, x, y, status, font_icon, verde, vermelho, cinza):
    if status == "✔":
        # Check verde simples e limpo
        draw_obj.text((x, y), "✔", font=font_icon, fill=verde, anchor="mm")
    elif status == "✖":
        # X vermelho
        draw_obj.text((x, y), "✖", font=font_icon, fill=vermelho, anchor="mm")
    else:
        draw_obj.text((x, y), status, font=font_icon, fill=cinza, anchor="ma")

# --- DESENHO DA IMAGEM ---
def criar_proposta(dados):
    # MUDANÇA 1: Formato 4:5 (Padrão Feed/Doc Digital) - Mais largo visualmente
    W, H = 1080, 1350 
    
    # 1. FUNDO (Carros/Proteção)
    try:
        bg = Image.open("fundo.jpg").convert("RGBA")
        # Crop central para preencher 1080x1350 sem esticar
        ratio_w = W / bg.width
        ratio_h = H / bg.height
        ratio = max(ratio_w, ratio_h)
        new_size = (int(bg.width * ratio), int(bg.height * ratio))
        bg = bg.resize(new_size, Image.LANCZOS)
        
        # Centraliza o crop
        left = (bg.width - W) / 2
        top = (bg.height - H) / 2
        img = bg.crop((left, top, left + W, top + H))
    except:
        img = Image.new('RGBA', (W, H), color=(240, 240, 240, 255))

    draw = ImageDraw.Draw(img)

    # --- PALETA ---
    LARANJA = (243, 112, 33, 255)
    AZUL_LEGACY = (0, 35, 95, 255)
    PRETO = (30, 30, 30, 255)
    CINZA_TEXTO = (60, 60, 60, 255)
    BRANCO = (255, 255, 255, 255)
    VERDE = (0, 180, 0, 255)
    VERMELHO = (200, 0, 0, 255)

    # --- FONTES ---
    try:
        # Ajustei tamanhos para o novo formato
        f_titulo = ImageFont.truetype("bold.ttf", 55)
        f_sub = ImageFont.truetype("bold.ttf", 40)
        f_norm = ImageFont.truetype("regular.ttf", 32)
        f_bold = ImageFont.truetype("bold.ttf", 32)
        f_small = ImageFont.truetype("regular.ttf", 26) # Para o rodapé
        f_check = ImageFont.truetype("bold.ttf", 40)
    except:
        f_titulo = f_sub = f_norm = f_bold = f_small = f_check = ImageFont.load_default()

    # ==============================================================================
    # O "CARD" FLUTUANTE (A MÁGICA)
    # ==============================================================================
    # Margem do Card em relação à borda da imagem
    PAD = 40 
    # Cabeçalho do Card (Logo)
    CARD_TOP = 180 
    
    # Desenha o Retângulo Branco (O "Papel")
    # Deixa um espaço em cima para o Logo "flutuar" ou ficar no topo
    draw.rectangle([(PAD, CARD_TOP), (W - PAD, H - PAD)], fill=BRANCO)
    
    # Borda fina laranja no card (opcional, fica chique)
    draw.rectangle([(PAD, CARD_TOP), (W - PAD, H - PAD)], outline=LARANJA, width=3)

    # --- LOGO (Fora do Card ou no Topo) ---
    try:
        logo = Image.open("logo.png").convert("RGBA")
        # Logo um pouco maior
        ratio = 220 / logo.height
        logo = logo.resize((int(logo.width * ratio), 220))
        # Posiciona centralizado no TOPO da imagem (sobre o fundo, invadindo um pouco o card)
        img.paste(logo, ((W - logo.width)//2, 60), logo)
    except:
        draw.text((W//2, 100), "LEGACY", font=f_titulo, fill=BRANCO, anchor="mm")

    # ==============================================================================
    # CONTEÚDO DENTRO DO CARD
    # ==============================================================================
    # Cursor Y começa dentro do card
    y = CARD_TOP + 120 
    MARGIN_INT = PAD + 40 # Margem interna do texto

    # 1. DADOS CLIENTE E CARRO
    draw.text((MARGIN_INT, y), f"Proposta para:", font=f_norm, fill=CINZA_TEXTO)
    draw.text((MARGIN_INT + 230, y), f"{dados['cliente']}", font=f_sub, fill=AZUL_LEGACY)
    
    y += 50
    draw.text((MARGIN_INT, y), f"Consultor(a): {dados['consultor']}", font=f_bold, fill=LARANJA)
    
    y += 70
    # Linha divisória suave
    draw.line([(MARGIN_INT, y), (W - MARGIN_INT, y)], fill=(220,220,220,255), width=2)
    y += 30

    # Carro (Destaque)
    carro_txt = f"{dados['modelo']} ({dados['ano']})"
    fipe_txt = f"FIPE: {dados['fipe']}"
    
    # Centralizado no Card
    center_x = W // 2
    draw.text((center_x, y), carro_txt, font=f_sub, fill=PRETO, anchor="ma", align="center")
    y += 50
    draw.text((center_x, y), fipe_txt, font=f_titulo, fill=AZUL_LEGACY, anchor="ma", align="center")

    y += 90

    # 2. ADESÃO (Destaque Box)
    # Caixa cinza claro para a adesão
    draw.rectangle([(center_x - 200, y), (center_x + 200, y + 60)], fill=(240,240,240,255))
    draw.text((center_x, y+15), f"Adesão: R$ {dados['adesao']}", font=f_sub, fill=PRETO, anchor="ma")

    y += 100

    # 3. TABELA DE PREÇOS
    # Ajuste fino da largura das colunas para não cortar
    largura_util = W - (MARGIN_INT * 2)
    col_w = largura_util // 4
    colunas = ["Econ.", "Básico", "Plus", "Prem."]

    # Cabeçalho Laranja
    for i, col in enumerate(colunas):
        cx = MARGIN_INT + (i * col_w) + (col_w // 2)
        draw.text((cx, y), col, font=f_bold, fill=LARANJA, anchor="ma")
    
    y += 45
    draw.line([(MARGIN_INT, y), (W - MARGIN_INT, y)], fill=PRETO, width=2)
    y += 20

    # Preços
    for i, p in enumerate(dados['precos']):
        cx = MARGIN_INT + (i * col_w) + (col_w // 2)
        val = p.replace("R$ ", "")
        draw.text((cx, y), f"R$\n{val}", font=f_sub, fill=PRETO, anchor="ma", align="center")

    y += 130

    # 4. BENEFÍCIOS (Compacto)
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

    for nome, stats in itens:
        # Nome menorzinho à esquerda
        draw.text((MARGIN_INT, y+8), nome, font=f_norm, fill=CINZA_TEXTO)
        
        for i, s in enumerate(stats):
            cx = MARGIN_INT + (i * col_w) + (col_w // 2)
            desenhar_icone(draw, cx, y+20, s, f_check, VERDE, VERMELHO, PRETO)
        
        y += 60 # Linhas mais compactas

    # 5. RODAPÉ (DISCLAIMER)
    y_final = H - PAD - 60 # Perto da borda inferior do card branco
    aviso = "A COTAÇÃO PODE SOFRER ALTERAÇÕES BASEADAS NOS VALORES VIGENTES"
    draw.text((center_x, y_final), aviso, font=f_small, fill=AZUL_LEGACY, anchor="mm", align="center")
    
    # Aviso Promoção (Acima do disclaimer)
    draw.text((center_x, y_final - 40), "⚠ PAGAMENTO ANTECIPADO GERA DESCONTO ⚠", font=f_bold, fill=LARANJA, anchor="mm")

    return img.convert("RGB")

# --- LÓGICA DE NEGÓCIO ---
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

# --- APP STREAMLIT ---
st.title("🛡️ Gerador Legacy Pro (Card)")
c1, c2 = st.columns(2)
cliente = c1.text_input("Nome do Cliente")
consultor = c2.text_input("Nome do Consultor")
modelo = st.text_input("Modelo do Veículo")
c3, c4, c5 = st.columns(3)
ano = c3.text_input("Ano")
fipe = c4.number_input("Valor FIPE", step=100.0)
regiao = c5.selectbox("Região", ["Capital", "Serrana"])
adesao = st.text_input("Valor da Adesão (R$)", value="300,00")

if st.button("GERAR COTAÇÃO OFICIAL", type="primary"):
    if fipe > 0 and cliente and consultor:
        with st.spinner("Gerando documento..."):
            precos = calcular_mensalidades(fipe, regiao)
            if precos:
                dados = {"cliente": cliente, "consultor": consultor, "modelo": modelo, "ano": ano, "fipe": f"R$ {fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "precos": precos, "adesao": adesao}
                img = criar_proposta(dados)
                st.image(img, caption="Layout Card Proteção", width=400)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 BAIXAR IMAGEM", buf.getvalue(), f"Cotacao_{cliente}.png", "image/png")
    else:
        st.warning("Preencha todos os campos.")
