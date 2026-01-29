import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerador Tabela Legacy", page_icon="📝", layout="centered")

# --- FUNÇÃO CHECKLIST (Ícones vetoriais desenhados) ---
def desenhar_icone(draw_obj, x, y, status, font_icon, verde, vermelho, cinza):
    if status == "✔":
        # Check verde limpo
        draw_obj.text((x, y), "✔", font=font_icon, fill=verde, anchor="mm")
    elif status == "✖":
        # X vermelho limpo
        draw_obj.text((x, y), "✖", font=font_icon, fill=vermelho, anchor="mm")
    else:
        # Texto (ex: 200, 10d)
        draw_obj.text((x, y), status, font=font_icon, fill=cinza, anchor="ma")

# --- MOTOR DE DESENHO ---
def criar_proposta(dados):
    # DIMENSÕES: 1080 x 1350 (4:5) - Melhor proporção para leitura e tabelas
    W, H = 1080, 1350
    
    # 1. CARREGAR SEU FUNDO (fundo.png)
    try:
        # Tenta carregar o fundo que você preparou
        bg = Image.open("fundo.png").convert("RGBA")
        
        # Ajusta o tamanho da imagem para caber no canvas sem distorcer (Crop Central)
        ratio = max(W / bg.width, H / bg.height)
        new_size = (int(bg.width * ratio), int(bg.height * ratio))
        bg = bg.resize(new_size, Image.LANCZOS)
        
        # Centraliza
        left = (bg.width - W) / 2
        top = (bg.height - H) / 2
        img = bg.crop((left, top, left + W, top + H))
    except:
        # Fundo branco de emergência se não achar o arquivo
        img = Image.new('RGBA', (W, H), color=(255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    # --- PALETA DE CORES ---
    LARANJA = (243, 112, 33, 255)
    AZUL_LEGACY = (0, 35, 95, 255)
    PRETO = (20, 20, 20, 255)       # Preto quase total para leitura
    CINZA_TEXTO = (80, 80, 80, 255)
    VERDE = (0, 180, 0, 255)
    VERMELHO = (200, 0, 0, 255)

    # --- FONTES (Carrega as que você subiu) ---
    try:
        f_titulo = ImageFont.truetype("bold.ttf", 55)
        f_subtitulo = ImageFont.truetype("bold.ttf", 40)
        f_texto = ImageFont.truetype("regular.ttf", 32)
        f_negrito = ImageFont.truetype("bold.ttf", 32)
        f_tabela_head = ImageFont.truetype("bold.ttf", 30) # Um pouco menor para caber 4 colunas
        f_tabela_val = ImageFont.truetype("bold.ttf", 36)
        f_aviso = ImageFont.truetype("regular.ttf", 26)
        f_check = ImageFont.truetype("bold.ttf", 38)
    except:
        f_titulo = f_subtitulo = f_texto = f_negrito = f_tabela_head = f_tabela_val = f_aviso = f_check = ImageFont.load_default()

    # ==============================================================================
    # DIAGRAMAÇÃO (ONDE O TEXTO VAI ENTRAR)
    # ==============================================================================
    # Defina aqui onde começa a área útil na sua imagem de fundo
    MARGEM_SUPERIOR = 250  # Pula o cabeçalho da sua imagem
    MARGEM_LATERAL = 50    # Espaço nas laterais
    # ==============================================================================

    y = MARGEM_SUPERIOR

    # --- 1. CABEÇALHO DA PROPOSTA ---
    # Cliente e Consultor
    draw.text((MARGEM_LATERAL, y), "Proposta para:", font=f_texto, fill=CINZA_TEXTO)
    draw.text((MARGEM_LATERAL + 220, y), dados['cliente'], font=f_subtitulo, fill=AZUL_LEGACY)
    
    y += 50
    draw.text((MARGEM_LATERAL, y), f"Consultor(a): {dados['consultor']}", font=f_negrito, fill=LARANJA)

    y += 80
    
    # Linha divisória fina
    draw.line([(MARGEM_LATERAL, y), (W - MARGEM_LATERAL, y)], fill=(200,200,200,255), width=2)
    y += 40

    # --- 2. DADOS DO VEÍCULO (Centralizado) ---
    centro_x = W // 2
    
    # Modelo do Carro
    draw.text((centro_x, y), dados['modelo'], font=f_subtitulo, fill=PRETO, anchor="ma", align="center")
    y += 50
    # Ano e Fipe
    info_fipe = f"Ano: {dados['ano']}  |  FIPE: {dados['fipe']}"
    draw.text((centro_x, y), info_fipe, font=f_titulo, fill=AZUL_LEGACY, anchor="ma", align="center")

    y += 100

    # --- 3. ADESÃO (Destaque) ---
    # Box cinza clarinho atrás da adesão para destacar
    draw.rectangle([(centro_x - 200, y), (centro_x + 200, y + 60)], fill=(245,245,245,255))
    draw.text((centro_x, y+12), f"Adesão: R$ {dados['adesao']}", font=f_subtitulo, fill=PRETO, anchor="ma")

    y += 100

    # --- 4. TABELA DE PREÇOS ---
    largura_util = W - (MARGEM_LATERAL * 2)
    largura_coluna = largura_util // 4
    colunas = ["Econ.", "Básico", "Plus", "Prem."]

    # Títulos das colunas
    for i, col in enumerate(colunas):
        cx = MARGEM_LATERAL + (i * largura_coluna) + (largura_coluna // 2)
        draw.text((cx, y), col, font=f_tabela_head, fill=LARANJA, anchor="ma")
    
    y += 45
    # Linha preta da tabela
    draw.line([(MARGEM_LATERAL, y), (W - MARGEM_LATERAL, y)], fill=PRETO, width=3)
    y += 20

    # Valores
    for i, p in enumerate(dados['precos']):
        cx = MARGEM_LATERAL + (i * largura_coluna) + (largura_coluna // 2)
        valor_limpo = p.replace("R$ ", "")
        draw.text((cx, y), f"R$\n{valor_limpo}", font=f_tabela_val, fill=PRETO, anchor="ma", align="center")

    y += 140

    # --- 5. BENEFÍCIOS (GRID) ---
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
        # Nome do benefício
        draw.text((MARGEM_LATERAL, y+5), nome, font=f_texto, fill=CINZA_TEXTO)
        
        # Ícones nas colunas
        for i, status in enumerate(status_lista):
            cx = MARGEM_LATERAL + (i * largura_coluna) + (largura_coluna // 2)
            desenhar_icone(draw, cx, y+5, status, f_check, VERDE, VERMELHO, PRETO)
        
        y += 60 # Espaçamento entre linhas

    # --- 6. RODAPÉ (Mensagens) ---
    # Calculando posição final (perto do fim da imagem)
    y_rodape = H - 120 
    
    # Aviso Promoção (Laranja)
    aviso_promo = "⚠ PAGAMENTO ANTECIPADO GERA DESCONTO ⚠"
    draw.text((centro_x, y_rodape - 40), aviso_promo, font=f_negrito, fill=LARANJA, anchor="mm")
    
    # Aviso Legal (Azul Legacy)
    aviso_legal = "A COTAÇÃO PODE SOFRER ALTERAÇÕES BASEADAS NOS VALORES VIGENTES"
    draw.text((centro_x, y_rodape), aviso_legal, font=f_aviso, fill=AZUL_LEGACY, anchor="mm", align="center")

    return img.convert("RGB")

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

# --- APP ---
st.title("📝 Gerador de Cotação")

c1, c2 = st.columns(2)
cliente = c1.text_input("Nome do Cliente")
consultor = c2.text_input("Nome do Consultor")

modelo = st.text_input("Modelo do Veículo")
c3, c4, c5 = st.columns(3)
ano = c3.text_input("Ano")
fipe = c4.number_input("Valor FIPE", step=100.0)
regiao = c5.selectbox("Região", ["Capital", "Serrana"])
adesao = st.text_input("Valor da Adesão (R$)", value="300,00")

if st.button("GERAR IMAGEM", type="primary"):
    if fipe > 0 and cliente:
        with st.spinner("Desenhando sobre o fundo..."):
            precos = calcular_mensalidades(fipe, regiao)
            if precos:
                dados = {
                    "cliente": cliente, "consultor": consultor, 
                    "modelo": modelo, "ano": ano, 
                    "fipe": f"R$ {fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
                    "precos": precos, "adesao": adesao
                }
                img = criar_proposta(dados)
                st.image(img, caption="Resultado Final", width=400)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 BAIXAR IMAGEM", buf.getvalue(), f"Cotacao_{cliente}.png", "image/png")
    else:
        st.warning("Preencha os dados principais.")
