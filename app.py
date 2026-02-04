import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Legacy - Cotador Oficial", page_icon="🛡️", layout="centered")

# --- ESTILIZAÇÃO GLASSMORPHISM / SKEUOMORPHISM ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #001529 0%, #003366 100%);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF8C00;
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS (JSON ESTRUTURADO) ---
CONFIG = {
    "regras": {"limite_fipe": {"carro": 100000, "utilitario": 100000, "moto": 30000}},
    "precos": {
        "carro": {
            "capital": [
                {"min": 0, "max": 10000, "planos": {"Econômico": 75.0, "Básico": 86.6, "Plus": 110.4, "Premium": 151.5}},
                {"min": 10001, "max": 20000, "planos": {"Econômico": 75.0, "Básico": 110.6, "Plus": 137.49, "Premium": 170.49}},
                {"min": 20001, "max": 30000, "planos": {"Econômico": 75.0, "Básico": 126.8, "Plus": 172.69, "Premium": 202.5}},
            ]
        }
    },
    "coberturas": {
        "Econômico": "✅ Assistência 24h • ✅ Reboque • ✅ Clube Certo",
        "Básico": "✅ Assistência 24h • ✅ Reboque • ✅ Colisão • ✅ Roubo/Furto • ✅ Incêndio • ✅ Clube Certo",
        "Plus": "✅ Assistência 24h • ✅ Reboque • ✅ Colisão • ✅ Roubo/Furto • ✅ Danos Terceiros • ✅ Incêndio • ✅ Clube Certo",
        "Premium": "✅ Assistência 24h • ✅ Reboque • ✅ Colisão • ✅ Roubo/Furto • ✅ Danos Terceiros (Top) • ✅ Incêndio • ✅ Clube Certo"
    }
}

# --- INTERFACE ---
st.title("🛡️ Legacy Cotador")
st.write("Sistema Estrutural de Marketing e Vendas")

with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        cliente = st.text_input("Nome do Cliente")
        consultor = st.text_input("Nome do Consultor")
        contato = st.text_input("Contato do Consultor")
        
    with col2:
        modelo = st.text_input("Modelo do Veículo (ex: Golf 2014)")
        tipo = st.selectbox("Tipo", ["carro", "moto", "utilitario"])
        regiao = st.selectbox("Região", ["capital", "serrana"])
        valor_fipe = st.number_input("Valor FIPE (R$)", min_value=0.0, step=500.0)
        adesao = st.number_input("Valor da Adesão (R$)", min_value=0.0, step=50.0)
    
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE CÁLCULO ---
if st.button("GERAR COTAÇÃO PROFISSIONAL"):
    limite = CONFIG["regras"]["limite_fipe"].get(tipo, 0)
    
    if valor_fipe > limite:
        st.error(f"⚠️ Valor FIPE excede o limite de R$ {limite:,.2f} para este tipo de veículo.")
    elif valor_fipe == 0:
        st.warning("Por favor, insira um valor FIPE válido.")
    else:
        # Busca a faixa de preço
        faixas = CONFIG["precos"].get(tipo, {}).get(regiao, [])
        faixa = next((f for f in faixas if f["min"] <= valor_fipe <= f["max"]), None)
        
        if faixa:
            st.markdown("### 📋 Resultado da Cotação")
            
            # Tabela Visual
            resultados = []
            for p, preco in faixa["planos"].items():
                resultados.append({
                    "PLANO": p,
                    "MENSALIDADE": f"R$ {preco:.2f}",
                    "COBERTURAS": CONFIG["coberturas"][p]
                })
            
            df = pd.DataFrame(resultados)
            st.table(df)

            # --- TEXTO PARA WHATSAPP (FORMATO PREMIUM) ---
            st.markdown("### 📱 Copie para o WhatsApp")
            texto_wa = f"""*🛡️ LEGACY CLUBE DE BENEFÍCIOS*
---
*DADOS DA COTAÇÃO*
👤 *Cliente:* {cliente}
👨‍💼 *Consultor:* {consultor}
📅 *Data:* {data_hoje}
📱 *Contato:* {contato}
🚗 *Veículo:* {modelo}
💰 *Adesão:* R$ {adesao:.2f}
---
*OPÇÕES DE PLANOS:*
"""
            for res in resultados:
                texto_wa += f"\n⭐ *{res['PLANO']}*: {res['MENSALIDADE']}\n_{res['COBERTURAS']}_\n"

            st.text_area("Texto formatado:", texto_wa, height=300)
            st.info("Dica: Tire um print da tabela acima para um visual mais 'Glass' no envio!")
        else:
            st.error("Faixa de valor não encontrada na base de dados (Verificar PDF).")
