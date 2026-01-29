import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Legacy Mobile", page_icon="📱", layout="centered")

# --- REGRAS DE NEGÓCIO ---
def calcular_mensalidades(fipe, regiao):
    # Tabela de Preços (Capital vs Serrana)
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

# --- GERADOR DE IMAGEM 9:16 (DESENHO DO ZERO) ---
def criar_proposta_automatica(dados):
    # 1. Criar Canvas em Branco (1080x1920 - Full HD Vertical)
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # --- CORES ---
    LARANJA_LEGACY = (243, 112, 33) # Cor aproximada
    CINZA_ESCURO = (50, 50, 50)
    CINZA_CLARO = (240, 240, 240)
    BRANCO = (255, 255, 255)
    VERDE = (0, 180, 0)
    VERMELHO = (200, 0, 0)

    # --- FONTES ---
    try:
        # Caminhos Linux (Streamlit Cloud)
        base_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans"
        font_h1 = ImageFont.truetype(f"{base_path}-Bold.ttf", 80) # Títulos Grandes
        font_h2 = ImageFont.truetype(f"{base_path}-Bold.ttf", 50) # Subtítulos
        font_body = ImageFont.truetype(f"{base_path}.ttf", 40)    # Texto normal
        font_bold = ImageFont.truetype(f"{base_path}-Bold.ttf", 40) # Texto negrito
        font_small = ImageFont.truetype(f"{base_path}.ttf", 30)   # Texto pequeno
        font_check = ImageFont.truetype(f"{base_path}.ttf", 50)   # Checks
    except:
        # Fallback simples
        font_h1 = font_h2 = font_body = font_bold = font_small = font_check = ImageFont.load_default()

    # --- 1. CABEÇALHO ---
    # Barra Laranja no topo
    draw.rectangle([(0, 0), (W, 250)], fill=LARANJA_LEGACY)
    
    # Tentar colocar o Logo
    try:
        logo = Image.open("logo.png") # O NOME DO ARQUIVO DEVE SER ESSE
        # Redimensionar logo mantendo proporção (altura max 200)
        ratio = 200 / logo.height
        new_size = (int(logo.width * ratio), 200)
        logo = logo.resize(new_size)
        # Centralizar logo
        logo_x = (W - new_size[0]) // 2
        img.paste(logo, (logo_x, 25), logo if logo.mode == 'RGBA' else None)
    except:
        draw.text((W//2 - 100, 80), "LOGO LEGACY", font=font_h1, fill=BRANCO)

    # --- 2. DADOS DO CLIENTE E CARRO ---
    cursor_y = 280
    
    # Texto de Saudação
    texto_cliente = f"Proposta para: {dados['cliente']}"
    w_text = draw.textlength(texto_cliente, font=font_h2)
    draw.text(((W - w_text)/2, cursor_y), texto_cliente, font=font_h2, fill=CINZA_ESCURO)
    
    cursor_y += 80
    
    # Caixa cinza com dados do carro
    draw.rectangle([(50, cursor_y), (W-50, cursor_y + 250)], fill=CINZA_CLARO, outline=None)
    
    # Detalhes do Carro (Centralizado na caixa cinza)
    info_carro = f"{dados['modelo']}\n{dados['ano']}"
    draw.multiline_text((W//2, cursor_y + 30), info_carro, font=font_h2, fill=LARANJA_LEGACY, anchor="ma", align="center")
    
    # Valor FIPE grande
    draw.text((W//2, cursor_y + 160), f"FIPE: {dados['fipe_texto']}", font=font_h1, fill=CINZA_ESCURO, anchor="ma")

    cursor_y += 300

    # --- 3. TABELA DE PLANOS ---
    # Cabeçalho da Tabela
    colunas = ["Econômico", "Básico", "Plus", "Premium"]
    largura_col = W // 4
    
    for i, col in enumerate(colunas):
        x_pos = i * largura_col + (largura_col // 2)
        draw.text((x_pos, cursor_y), col, font=font_bold, fill=LARANJA_LEGACY, anchor="ma")
    
    cursor_y += 60
    draw.line([(50, cursor_y), (W-50, cursor_y)], fill=CINZA_ESCURO, width=2) # Linha separadora
    cursor_y += 20

    # Linha: MENSALIDADE (Destaque)
    precos = dados['lista_precos']
    for i, preco in enumerate(precos):
        x_pos = i * largura_col + (largura_col // 2)
        # Limpar "R$ " para caber melhor se precisar
        valor_limpo = preco.replace("R$ ", "")
        draw.text((x_pos, cursor_y), f"R$\n{valor_limpo}", font=font_h2, fill=CINZA_ESCURO, anchor="ma", align="center")
    
    cursor_y += 140

    # --- GRID DE BENEFÍCIOS ---
    # Configuração: (Nome do Benefício, [Eco, Bas, Plus, Prem])
    beneficios = [
        ("Rastreamento", ["✔", "✔", "✔", "✔"]),
        ("Reboque", ["200km", "400km", "1000km", "1000km"]),
        ("Roubo/Furto", ["✖", "✔", "✔", "✔"]),
        ("Colisão/PT", ["✖", "✖", "✔", "✔"]),
        ("Terceiros", ["✖", "✖", "✔", "✔"]),
        ("Vidros", ["✖", "✖", "✔", "✔"]),
        ("Carro Reserva", ["✖", "✖", "10d", "30d"]),
        ("Cob. GNV", ["✖", "✖", "✖", "✔"]),
    ]

    for nome, status_lista in beneficios:
        # Desenhar fundo alternado para facilitar leitura
        # draw.rectangle([(0, cursor_y-10), (W, cursor_y+50)], fill=CINZA_CLARO)
        
        # Nome do benefício (pequeno no centro ou lateral?) 
        # Vamos colocar os ícones alinhados nas colunas
        
        for i, status in enumerate(status_lista):
            x_pos = i * largura_col + (largura_col // 2)
            
            cor = CINZA_ESCURO
            fonte_uso = font_bold
            
            if status == "✔": 
                cor = VERDE
                fonte_uso = font_check
            elif status == "✖": 
                cor = VERMELHO
                fonte_uso = font_check
            
            draw.text((x_pos, cursor_y), status, font=fonte_uso, fill=cor, anchor="ma")
        
        # Nome do benefício (centralizado em cima dos ícones ou na lateral esquerda bem pequeno)
        draw.text((50, cursor_y + 10), nome, font=font_small, fill=CINZA_ESCURO, anchor="lm")
        
        cursor_y += 80 # Próxima linha

    # --- 4. RODAPÉ (AVISO) ---
    y_aviso = H - 250
    draw.rectangle([(0, y_aviso), (W, H)], fill=LARANJA_LEGACY)
    
    aviso_texto = "⚠ PAGAMENTO ANTECIPADO ⚠\nGARANTE DESCONTO NA MENSALIDADE!\n\nConsulte condições com seu consultor."
    draw.multiline_text((W//2, y_aviso + 125), aviso_texto, font=font_bold, fill=BRANCO, anchor="mm", align="center")

    return img

# --- INTERFACE ---
st.title("📱 Gerador Automático (Story)")

# Formulário Simplificado
col1, col2 = st.columns(2)
nome_consultor = col1.text_input("Nome do Consultor")
nome_cliente = col2.text_input("Nome do Cliente")

modelo = st.text_input("Modelo do Veículo")
c1, c2 = st.columns(2)
ano = c1.text_input("Ano")
valor_fipe = c2.number_input("Valor FIPE", step=100.0)
regiao = st.selectbox("Região", ["Capital", "Região Serrana"])

if st.button("GERAR PROPOSTA 9:16", type="primary"):
    if not valor_fipe:
        st.warning("Digite o valor da FIPE")
    else:
        precos = calcular_mensalidades(valor_fipe, regiao)
        if precos:
            dados = {
                "cliente": nome_cliente,
                "modelo": modelo,
                "ano": ano,
                "fipe_texto": f"R$ {valor_fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "lista_precos": precos
            }
            
            img_final = criar_proposta_automatica(dados)
            
            # Mostrar e Baixar
            st.image(img_final, caption="Visualização", width=300) # Mostra menor pra caber na tela
            
            buf = io.BytesIO()
            img_final.save(buf, format="PNG")
            
            st.download_button(
                "📥 BAIXAR IMAGEM (HD)",
                data=buf.getvalue(),
                file_name=f"proposta_{nome_cliente}.png",
                mime="image/png"
            )
        else:
            st.error("Valor FIPE fora da tabela.")