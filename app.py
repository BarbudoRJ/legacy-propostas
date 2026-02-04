import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Legacy - Sistema de Cotador", layout="centered")

# Estilização Glass/Skeuomorphic simples via CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .main-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Dados (O seu JSON de referência)
# Dica: No futuro, você pode colocar isso em um arquivo 'config.json' separado
CONFIG = {
    "regras_gerais": {"limite_fipe": {"carro": 100000, "utilitario": 100000, "moto": 30000}},
    "matriz_precos": {
        "carro": {
            "capital": [
                {"faixa": {"min": 0, "max": 10000}, "planos": {"economico": 75.0, "basico": 86.6, "plus": 110.4, "premium": 151.5}},
                {"faixa": {"min": 10001, "max": 20000}, "planos": {"economico": 75.0, "basico": 110.6, "plus": 137.49, "premium": 170.49}},
                {"faixa": {"min": 20001, "max": 30000}, "planos": {"economico": 75.0, "basico": 126.8, "plus": 172.69, "premium": 202.5}}
            ]
        }
    },
    "matriz_coberturas": {
        "economico": ["Assistência 24h", "Reboque", "Clube Certo"],
        "basico": ["Assistência 24h", "Reboque", "Colisão", "Roubo e Furto", "Incêndio", "Clube Certo"],
        "plus": ["Assistência 24h", "Reboque", "Colisão", "Roubo e Furto", "Danos a Terceiros", "Incêndio", "Clube Certo"],
        "premium": ["Assistência 24h", "Reboque", "Colisão", "Roubo e Furto", "Danos a Terceiros (Limite Maior)", "Incêndio", "Clube Certo"]
    }
}

# 3. Interface do Usuário
st.title("🛡️ Legacy Clube de Benefícios")
st.subheader("Simulador de Cotação v1")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Tipo de Veículo", ["carro", "moto", "utilitario"])
        regiao = st.selectbox("Região", ["capital", "serrana"])
    with col2:
        valor_fipe = st.number_input("Valor FIPE (R$)", min_value=0.0, step=1000.0)

# 4. Lógica de Cálculo
if st.button("Gerar Cotação Oficial"):
    limite = CONFIG["regras_gerais"]["limite_fipe"].get(tipo, 0)
    
    if valor_fipe > limite:
        st.error(f"❌ Valor acima do limite permitido para {tipo} (Limite: R$ {limite})")
    else:
        # Busca a faixa
        faixas = CONFIG["matriz_precos"].get(tipo, {}).get(regiao, [])
        faixa_ativa = next((f for f in faixas if f["faixa"]["min"] <= valor_fipe <= f["faixa"]["max"]), None)
        
        if faixa_ativa:
            st.success(f"Cotação encontrada para faixa R$ {faixa_ativa['faixa']['min']} - R$ {faixa_ativa['faixa']['max']}")
            
            # Montando a Tabela Visual (Skeuomorphic Style)
            dados_tabela = []
            for plano, preco in faixa_ativa["planos"].items():
                coberturas = " • ".join(CONFIG["matriz_coberturas"].get(plano, []))
                dados_tabela.append({
                    "PLANO": plano.upper(),
                    "MENSALIDADE": f"R$ {preco:.2f}",
                    "COBERTURAS": coberturas
                })
            
            df = pd.DataFrame(dados_tabela)
            st.table(df) # O 'st.table' é estático e limpo, combina com o estilo esquelmorfo
            
            st.info("💡 Clique nos três pontos acima da tabela para baixar como CSV se precisar enviar ao cliente.")
        else:
            st.warning("⚠️ Faixa de valor não encontrada. Por favor, verifique a tabela PDF.")

# 5. Rodapé
st.markdown("---")
st.caption("Legacy Clube de Benefícios - Sistema Estrutural de Marketing")
