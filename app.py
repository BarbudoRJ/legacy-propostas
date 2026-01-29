import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Proposta Legacy", page_icon="🧡", layout="centered")

# --- 2. DADOS E REGRAS DE NEGÓCIO ---
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
            
    if not valores:
        return None 
    
    return [f"R$ {v:.2f}".replace('.', ',') for v in valores]

# --- 3. FUNÇÃO DE DESENHO NA IMAGEM ---
def gerar_imagem(dados, template_path="TAMPLATE PROPOSTA.jpg"): 
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # --- CORREÇÃO DAS FONTES (USANDO FONTE DO SISTEMA LINUX) ---
    try:
        # Tenta pegar a fonte DejaVuSans que existe no servidor
        path_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        path_font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        font_padrao = ImageFont.truetype(path_font, 28) 
        font_bold = ImageFont.truetype(path_font_bold, 28)
        font_grid = ImageFont.truetype(path_font_bold, 24) 
        font_check = ImageFont.truetype(path_font, 40)
        font_small_bold = ImageFont.truetype(path_font_bold, 20)
    except:
        # Se der erro, tenta carregar Arial local ou fallback
        try:
            font_padrao = ImageFont.truetype("arial.ttf", 28)
            font_bold = ImageFont.truetype("arialbd.ttf", 28)
            font_grid = ImageFont.truetype("arialbd.ttf", 24)
            font_check = ImageFont.truetype("arial.ttf", 40)
            font_small_bold = ImageFont.truetype("arialbd.ttf", 20)
        except:
            font_padrao = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_grid = ImageFont.load_default()
            font_check = ImageFont.load_default()
            font_small_bold = ImageFont.load_default()

    cor_texto = (0, 0, 0)
    cor_verde = (0, 150, 0)
    cor_vermelho = (200, 0, 0) 
    cor_branco = (255, 255, 255)

    # Preenchimento Cabeçalho
    draw.text((180, 185), dados['cliente'], font=font_padrao, fill=cor_texto)
    draw.text((180, 215), datetime.now().strftime("%d/%m/%Y"), font=font_padrao, fill=cor_texto)
    draw.text((220, 245), dados['consultor'], font=font_padrao, fill=cor_texto)

    # Bloco Laranja Esquerdo
    draw.text((50, 310), dados['modelo'], font=font_bold, fill=cor_texto)
    draw.text((50, 370), dados['ano'], font=font_bold, fill=cor_texto)
    draw.text((50, 430), dados['fipe_texto'], font=font_bold, fill=cor_texto)
    
    # Bloco Laranja Direito
    draw.text((700, 290), dados['adesao_final'], font=font_bold, fill=cor_texto) 
    draw.text((700, 330), dados['mensalidade_final'], font=font_bold, fill=cor_texto)

    # Checkboxes
    if dados['uso'] == "Aplicativo":
        draw.text((860, 375), "X", font=font_check, fill=cor_texto)
    else:
        draw.text((860, 435), "X", font=font_check, fill=cor_texto)

    # Grid
    col_x = [380, 520, 660, 800] 
    y_start = 535 
    y_step = 42 

    mensalidades = dados['lista_precos']

    if mensalidades:
        for i, valor in enumerate(mensalidades):
            draw.text((col_x[i], y_start), valor, font=font_grid, fill=cor_branco)

    grid_config = [
        ["V", "V", "V", "V"], # Rastreador
        ["200 km", "400 km", "1000 km", "1000 km"], # Reboque
        ["X", "V", "V", "V"], # Roubo
        ["X", "X", "V", "V"], # Incêndio
        ["X", "X", "V", "V"], # Colisão
        ["X", "X", "V", "V"], # Fenômenos
        ["X", "X", "10 dias", "30 dias"], # Carro Reserva
        ["X", "X", "V", "V"], # Vidros
        ["X", "X", "V", "V"], # Terceiros
        ["X", "X", "X", "V"]  # GNV
    ]

    current_y = y_start + y_step 
    
    for row in grid_config:
        for i, content in enumerate(row):
            pos_x = col_x[i] + 15
            
            if content == "V":
                draw.text((pos_x, current_y), "✔", font=font_check, fill=cor_verde)
            elif content == "X":
                draw.text((pos_x + 5, current_y), "✖", font=font_check, fill=cor_vermelho)
            else:
                draw.text((pos_x - 10, current_y + 5), content, font=font_small_bold, fill=(100,100,100))
        
        current_y += y_step

    return img

# --- 4. INTERFACE ---
st.title("🧡 Gerador de Proposta Legacy")
st.markdown("Preencha os dados abaixo para gerar a imagem oficial.")

col1, col2 = st.columns(2)
with col1:
    consultor = st.text_input("Consultor(a)")
    cliente = st.text_input("Nome do Cliente")
with col2:
    regiao = st.selectbox("Região de Circulação", ["Capital", "Região Serrana"])
    uso = st.radio("Uso do Veículo", ["Particular", "Aplicativo"])

st.divider()

c1, c2, c3 = st.columns(3)
with c1:
    modelo = st.text_input("Modelo do Carro")
with c2:
    ano = st.text_input("Ano/Modelo")
with c3:
    valor_fipe = st.number_input("Valor FIPE (R$)", min_value=0.0, step=100.0)

st.divider()
st.subheader("Valores da Proposta")
col_adesao, col_plano = st.columns(2)

with col_adesao:
    adesao_input = st.text_input("Valor da Adesão (R$)", value="300,00")

with col_plano:
    plano_sugerido = st.selectbox("Qual plano destacar no topo?", ["Econômico", "Básico", "Plus", "Premium"])

if st.button("GERAR IMAGEM AGORA", type="primary"):
    if valor_fipe > 100000:
        st.error("⚠️ Veículo acima de R$ 100.000,00 não permitido pelo regulamento.")
    elif valor_fipe == 0:
        st.warning("Preencha o valor da FIPE.")
    else:
        lista_precos = calcular_mensalidades(valor_fipe, regiao)
        
        if lista_precos:
            mapa_planos = {"Econômico": 0, "Básico": 1, "Plus": 2, "Premium": 3}
            mensalidade_destaque = lista_precos[mapa_planos[plano_sugerido]]

            dados = {
                "cliente": cliente,
                "consultor": consultor,
                "modelo": modelo,
                "ano": ano,
                "fipe_texto": f"R$ {valor_fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "uso": uso,
                "adesao_final": adesao_input,
                "mensalidade_final": mensalidade_destaque,
                "lista_precos": lista_precos
            }

            with st.spinner("Desenhando proposta..."):
                try:
                    imagem_final = gerar_imagem(dados)
                    st.image(imagem_final, caption="Proposta Gerada", use_column_width=True)
                    
                    buf = io.BytesIO()
                    imagem_final.save(buf, format="PNG")
                    byte_im = buf.getvalue()

                    st.download_button(
                        label="📥 BAIXAR IMAGEM PARA WHATSAPP",
                        data=byte_im,
                        file_name=f"Proposta_{cliente}.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"Erro ao desenhar imagem: {e}")
        else:
            st.error("Erro ao calcular valores.")