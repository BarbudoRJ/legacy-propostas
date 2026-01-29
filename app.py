import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Proposta Legacy", page_icon="🧡", layout="centered")

# --- 2. DADOS E REGRAS DE NEGÓCIO (Baseado no Legacyto) ---
def calcular_mensalidades(fipe, regiao):
    # Tabela de Preços (Capital vs Serrana)
    # Formato: (Limite_Superior, [Eco, Basico, Plus, Premium])
    # Capital = Indice 0, Serrana = Indice 1 (nos arrays de preços)
    
    # Estrutura: chaves são os tetos da FIPE. Valores são tuplas (Preços Capital, Preços Serrana)
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

    # Selecionar lista correta
    idx_regiao = 0 if regiao == "Capital" else 1
    
    valores = None
    for teto, precos in tabela.items():
        if fipe <= teto:
            valores = precos[idx_regiao]
            break
            
    if not valores:
        return None # Acima de 100k
    
    # Formata para string de moeda
    return [f"R$ {v:.2f}".replace('.', ',') for v in valores]

# --- 3. FUNÇÃO DE DESENHO NA IMAGEM ---
def gerar_imagem(dados, template_path="TAMPLATE PROPOSTA.jpg"): # Certifique-se que o nome do arquivo está correto na pasta
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Tente carregar fontes (padrão do sistema ou arquivo ttf na pasta)
    try:
        # Recomendo baixar uma fonte Arial ou Roboto e colocar na pasta do projeto
        font_padrao = ImageFont.truetype("arial.ttf", 28) 
        font_bold = ImageFont.truetype("arialbd.ttf", 28)
        font_grid = ImageFont.truetype("arialbd.ttf", 24) # Fonte menor para o grid
        font_check = ImageFont.truetype("arial.ttf", 40) # Para o X e Check
    except:
        font_padrao = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_grid = ImageFont.load_default()
        font_check = ImageFont.load_default()

    # Cores
    cor_texto = (0, 0, 0) # Preto
    cor_verde = (0, 150, 0) # Verde Legacy
    cor_vermelho = (200, 0, 0) # Vermelho
    cor_branco = (255, 255, 255)

    # --- MAPEAMENTO DE COORDENADAS (AJUSTE FINO NECESSÁRIO) ---
    # As coordenadas abaixo são estimativas baseadas na imagem. 
    # Você precisará testar e ajustar os números (X, Y).
    
    # Cabeçalho
    draw.text((180, 185), dados['cliente'], font=font_padrao, fill=cor_texto)
    draw.text((180, 215), datetime.now().strftime("%d/%m/%Y"), font=font_padrao, fill=cor_texto)
    draw.text((220, 245), dados['consultor'], font=font_padrao, fill=cor_texto)

    # Bloco Laranja Esquerdo (Carro)
    draw.text((50, 310), dados['modelo'], font=font_bold, fill=cor_texto) # Modelo
    draw.text((50, 370), dados['ano'], font=font_bold, fill=cor_texto) # Ano
    draw.text((50, 430), dados['fipe_texto'], font=font_bold, fill=cor_texto) # Valor Fipe
    
    # Bloco Laranja Direito (Valores Finais Sugeridos)
    draw.text((700, 290), dados['adesao_final'], font=font_bold, fill=cor_texto) 
    draw.text((700, 330), dados['mensalidade_final'], font=font_bold, fill=cor_texto)

    # Checkboxes (App vs Particular)
    # X, Y do quadrado
    if dados['uso'] == "Aplicativo":
        draw.text((860, 375), "X", font=font_check, fill=cor_texto) # Checkbox App
    else:
        draw.text((860, 435), "X", font=font_check, fill=cor_texto) # Checkbox Particular

    # --- GRID DE BENEFÍCIOS ---
    # Colunas X (Estimadas):
    col_x = [380, 520, 660, 800] # Econômico, Básico, Plus, Premium
    
    # Altura inicial Y da primeira linha (Mensalidade) e incremento
    y_start = 535 
    y_step = 42 # Distância entre linhas

    mensalidades = dados['lista_precos'] # [Eco, Bas, Plus, Prem]

    # Linha 1: Mensalidades (Texto)
    if mensalidades:
        for i, valor in enumerate(mensalidades):
            draw.text((col_x[i], y_start), valor, font=font_grid, fill=cor_branco) # Texto Branco no fundo azul? Ajustar cor

    # Configuração do Grid (Conteúdo de cada célula)
    # V = Check Verde, X = Cruz Vermelha, T = Texto Personalizado
    grid_config = [
        # Rastreador
        ["V", "V", "V", "V"], 
        # Reboque
        ["200 km", "400 km", "1000 km", "1000 km"],
        # Roubo e Furto
        ["X", "V", "V", "V"],
        # Incêndio
        ["X", "X", "V", "V"],
        # Colisão / PT
        ["X", "X", "V", "V"],
        # Fenômenos
        ["X", "X", "V", "V"],
        # Carro Reserva
        ["X", "X", "10 dias", "30 dias"],
        # Proteção Vidros
        ["X", "X", "V", "V"],
        # Danos Terceiros
        ["X", "X", "V", "V"],
        # Cobertura GNV
        ["X", "X", "X", "V"]
    ]

    # Loop para desenhar o Grid
    current_y = y_start + y_step # Começa na linha do Rastreador
    
    for row in grid_config:
        for i, content in enumerate(row):
            pos_x = col_x[i] + 15 # Ajuste fino para centralizar
            
            if content == "V":
                draw.text((pos_x, current_y), "✔", font=font_check, fill=cor_verde)
            elif content == "X":
                draw.text((pos_x + 5, current_y), "✖", font=font_check, fill=cor_vermelho) # X um pouco deslocado
            else:
                # Texto personalizado (Ex: 200km)
                draw.text((pos_x - 10, current_y + 5), content, font=ImageFont.truetype("arialbd.ttf", 20), fill=(100,100,100))
        
        current_y += y_step

    return img

# --- 4. INTERFACE DO USUÁRIO (FRONT-END) ---
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

# Opção de selecionar qual plano o cliente quer (para destacar no topo)
st.divider()
st.subheader("Valores da Proposta")
col_adesao, col_plano = st.columns(2)

with col_adesao:
    adesao_input = st.text_input("Valor da Adesão (R$)", value="300,00")

with col_plano:
    plano_sugerido = st.selectbox("Qual plano destacar no topo?", ["Econômico", "Básico", "Plus", "Premium"])

# Botão de Ação
if st.button("GERAR IMAGEM AGORA", type="primary"):
    if valor_fipe > 100000:
        st.error("⚠️ Veículo acima de R$ 100.000,00 não permitido pelo regulamento.")
    elif valor_fipe == 0:
        st.warning("Preencha o valor da FIPE.")
    else:
        # Calcular Tabela
        lista_precos = calcular_mensalidades(valor_fipe, regiao)
        
        if lista_precos:
            # Pegar o preço do plano escolhido para o topo
            mapa_planos = {"Econômico": 0, "Básico": 1, "Plus": 2, "Premium": 3}
            mensalidade_destaque = lista_precos[mapa_planos[plano_sugerido]]

            # Montar dados
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

            # Gerar
            with st.spinner("Desenhando proposta..."):
                imagem_final = gerar_imagem(dados)
                
                # Exibir
                st.image(imagem_final, caption="Proposta Gerada", use_column_width=True)
                
                # Botão Download
                buf = io.BytesIO()
                imagem_final.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="📥 BAIXAR IMAGEM PARA WHATSAPP",
                    data=byte_im,
                    file_name=f"Proposta_{cliente}_{modelo}.png",
                    mime="image/png"
                )
        else:
            st.error("Erro ao calcular valores. Verifique a FIPE.")