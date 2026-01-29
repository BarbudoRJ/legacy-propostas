import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

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
    LARANJA_LEGACY = (243, 112, 33) 
    CINZA_ESCURO = (50, 50, 50)
    CINZA_CLARO = (240, 240, 240)
    BRANCO = (255, 255, 255)
    VERDE = (0, 180, 0)
    VERMELHO = (200, 0, 0)

    # --- FONTES ---
    try:
        base_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans"
        font_h1 = ImageFont.truetype(f"{base_path}-Bold.ttf", 80)
        font_h2 = ImageFont.truetype(f"{base_path}-Bold.ttf", 50)
        font_body = ImageFont.truetype(f"{base_path}.ttf", 40)
        font_bold = ImageFont.truetype(f"{base_path}-Bold.ttf", 40)
        font_small = ImageFont.truetype(f"{base_path}.ttf", 30)
        font_check = ImageFont.truetype(f"{base_path}.ttf", 50)
    except:
        font_h1 = font_h2 = font_body = font_bold = font_small = font_check = ImageFont.load_default()

    # --- 1. CABEÇALHO ---
    draw.rectangle([(0, 0), (W, 250)], fill=LARANJA_LEGACY)
    
    try:
        logo = Image.open("logo.png")
        if logo.mode != 'RGBA': logo = logo.convert('RGBA')
        
        # Redimensionar logo (max altura 200)
        ratio = 200 / logo.height
        new_size = (int(logo.width * ratio), 200)
        logo = logo.resize(new_size)
        
        # Centralizar
        logo_x = (W - new_size[0]) // 2
        img.paste(logo, (logo_x, 25), logo)
    except:
        draw.text((W//2 - 200, 80), "LOGO LEGACY (Faltando)", font=font_h2, fill=BRANCO)

    # --- 2. DADOS DO CLIENTE E CARRO ---
    cursor_y = 280
    
    texto_cliente = f"Proposta para: {dados['cliente']}"
    # Centralização manual simples para fallback
    draw.text((50, cursor_y), texto_cliente, font=font_h2, fill=CINZA_ESCURO)
    
    cursor_y += 80
    
    # Caixa cinza
    draw.rectangle([(50, cursor_y), (W-50, cursor_y + 250)], fill=CINZA_CLARO)
    
    # Detalhes do Carro
    info_carro = f"{dados['modelo']}\n{dados['ano']}"
    draw.text((W//2 - 150, cursor_y + 30), info_carro, font=font_h2, fill=LARANJA_LEGACY)
    
    draw.text((W//2 - 250, cursor_y + 160), f"FIPE: {dados['fipe_texto']}", font=font_h1, fill=CINZA_ESCURO)

    cursor_y += 300

    # --- 3. TABELA DE PLANOS ---
    colunas = ["Econômico", "Básico", "Plus", "Premium"]
    largura_col = W // 4
    
    for i, col in enumerate(colunas):
        x_pos = i * largura_col + 20
        # Apenas as 3 primeiras letras se for mobile mto pequeno ou nome completo
        nome_col = col if i == 3 else col[:3] + "."
        draw.text((x_pos, cursor_y), nome_col, font=font_h2, fill=LARANJA_LEGACY)
    
    cursor_y += 60
    draw.line([(50, cursor_y), (W-50, cursor_y)], fill=CINZA_ESCURO, width=2)
    cursor_y += 20

    # Preços
    precos = dados['lista_precos']
    for i, preco in enumerate(precos):
        x_pos = i * largura_col + 10
        valor_limpo = preco.replace("R$ ", "")
        draw.text((x_pos, cursor_y), valor_limpo, font=font_bold, fill=CINZA_ESCURO)
    
    cursor_y += 100

    # --- GRID DE BENEFÍCIOS ---
    beneficios = [
        ("Rastreamento", ["✔", "✔", "✔", "✔"]),
        ("Reboque", ["200", "400", "1mil", "1mil"]),
        ("Roubo/Furto", ["✖", "✔", "✔", "✔"]),
        ("Colisão/PT", ["✖", "✖", "✔", "✔"]),
        ("Terceiros", ["✖", "✖", "✔", "✔"]),
        ("Vidros", ["✖", "✖", "✔", "✔"]),
        ("Carro Res.", ["✖", "✖", "10d", "30d"]),
        ("Cob. GNV", ["✖", "✖", "✖", "✔"]),
    ]

    for nome, status_lista in beneficios:
        # Nome do benefício na esquerda (pequeno)
        draw.text((30, cursor_y + 10), nome, font=font_small, fill=CINZA_ESCURO)
        
        # Ícones
        for i, status in enumerate(status_lista):
            x_pos = i * largura_col + (largura_col // 2) + 20
            
            cor = CINZA_ESCURO
            fonte_uso = font_bold
            
            if status == "✔": 
                cor = VERDE
                fonte_uso = font_check
            elif status == "✖": 
                cor = VERMELHO
                fonte_uso = font_check
            
            draw.text((x_pos, cursor_y), status, font=fonte_uso, fill=cor)
        
        cursor_y += 80

    # --- 4. RODAPÉ ---
    y_aviso = H - 250
    draw.rectangle([(0, y_aviso), (W, H)], fill=LARANJA_LEGACY)
    
    aviso_texto = "⚠ PAGAMENTO ANTECIPADO ⚠\nGARANTE DESCONTO NA MENSALIDADE!"
    draw.text((100, y_aviso + 100), aviso_texto, font=font_h2, fill=BRANCO)

    return img

# --- INTERFACE ---
st.title("📱 Gerador Automático (Story)")

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
            
            st.image(img_final, caption="Visualização", width=300)
            
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
