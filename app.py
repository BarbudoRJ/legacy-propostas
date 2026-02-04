import streamlit as st
import requests
from datetime import date
import difflib # Biblioteca para tentar achar textos parecidos (Fuzzy Matching)

st.set_page_config(page_title="Cotação Legacy", layout="centered")

# -------------------------------
# CONFIG: provedores FIPE gratuitos
# -------------------------------
BASE_A = "https://parallelum.com.br/fipe/api/v1"

TYPE_MAP = {
    "Carro": "carros",
    "Moto": "motos",
    "Utilitário": "caminhoes",
}

# -------------------------------
# 1. API DE PLACA (MOCK / PLACEHOLDER)
# -------------------------------
def consultar_placa(placa_texto):
    """
    Tenta buscar dados da placa.
    IMPORTANTE: Como não existe API gratuita oficial, aqui você deve
    inserir a chamada para um serviço pago (ex: APIBrasil, Infosimples)
    ou um scraper próprio.
    
    Abaixo, simulo um retorno para teste.
    """
    placa_limpa = placa_texto.replace("-", "").upper().strip()
    
    # --- SIMULAÇÃO (Remova isso quando tiver uma API Real) ---
    if not placa_limpa:
        return None
        
    # Simulando que a API encontrou um Honda Civic 2021
    # Em produção, você faria: requests.get(f"https://sua-api-paga.com/{placa_limpa}")
    return {
        "marca": "Honda",
        "modelo": "Civic",
        "ano": "2021",
        "cor": "Prata",
        "chassi": "93H**************",
        "situacao": "Sem restrições"
    }

# -------------------------------
# 2. HELPERS FIPE + CACHE
# -------------------------------
@st.cache_data(ttl=60 * 60)
def api_get_json(url: str):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return []

@st.cache_data(ttl=60 * 60)
def listar_marcas(tipo_api: str):
    return api_get_json(f"{BASE_A}/{tipo_api}/marcas")

@st.cache_data(ttl=60 * 60)
def listar_modelos(tipo_api: str, marca_id: int):
    return api_get_json(f"{BASE_A}/{tipo_api}/marcas/{marca_id}/modelos")

@st.cache_data(ttl=60 * 60)
def listar_anos(tipo_api: str, marca_id: int, modelo_id: int):
    return api_get_json(f"{BASE_A}/{tipo_api}/marcas/{marca_id}/modelos/{modelo_id}/anos")

def buscar_valor_fipe(tipo_api: str, marca_id: int, modelo_id: int, ano_codigo: str):
    return api_get_json(f"{BASE_A}/{tipo_api}/marcas/{marca_id}/modelos/{modelo_id}/anos/{ano_codigo}")

def brl_to_float(valor_brl: str) -> float:
    if not valor_brl: return 0.0
    v = valor_brl.replace("R$", "").strip()
    v = v.replace(".", "").replace(",", ".")
    return float(v)

# Função para tentar achar a string mais parecida (Fuzzy Match)
def encontrar_melhor_match(texto_buscado, lista_opcoes):
    # Retorna a opção mais parecida se a similaridade for alta (> 0.6)
    matches = difflib.get_close_matches(str(texto_buscado), list(lista_opcoes), n=1, cutoff=0.5)
    return matches[0] if matches else None

# -------------------------------
# STATE MANAGEMENT
# -------------------------------
if "fipe_valor_float" not in st.session_state: st.session_state.fipe_valor_float = None
if "fipe_valor_str" not in st.session_state: st.session_state.fipe_valor_str = None
if "veiculo_desc" not in st.session_state: st.session_state.veiculo_desc = None

# States para a busca de placa preencher os campos
if "dados_placa" not in st.session_state: st.session_state.dados_placa = None

# -------------------------------
# UI
# -------------------------------
st.title("🚗 Gerador de Cotação Inteligente")

# --- BUSCA DE PLACA ---
with st.container():
    st.markdown("### 1. Identificação do Veículo")
    c_placa, c_btn = st.columns([3, 1])
    placa_input = c_placa.text_input("Digite a Placa", placeholder="ABC-1234")
    
    if c_btn.button("🔍 Buscar Placa", type="secondary", use_container_width=True):
        with st.spinner("Consultando base de dados..."):
            dados = consultar_placa(placa_input)
            if dados:
                st.session_state.dados_placa = dados
                st.success("Veículo identificado!")
            else:
                st.warning("Placa não encontrada ou API indisponível.")

# Se tiver dados da placa, mostra um resumo visual
if st.session_state.dados_placa:
    dp = st.session_state.dados_placa
    st.info(f"📋 **Retorno da Placa:** {dp['marca']} {dp['modelo']} | Ano {dp['ano']} | Cor {dp['cor']}")

st.divider()

# --- SELEÇÃO FIPE (Tenta pré-selecionar) ---
st.markdown("### 2. Definição FIPE")
st.caption("Confirme os dados abaixo para obter o valor exato.")

tipo_label = st.selectbox("Tipo de Veículo", ["Carro", "Moto", "Utilitário"])
tipo_api = TYPE_MAP[tipo_label]

# 1) MARCAS
marcas = listar_marcas(tipo_api)
marca_opcoes = {m["nome"]: m["codigo"] for m in marcas}

# Tenta adivinhar a marca vinda da placa
index_marca = 0
if st.session_state.dados_placa:
    match_marca = encontrar_melhor_match(st.session_state.dados_placa['marca'], marca_opcoes.keys())
    if match_marca:
        index_marca = list(marca_opcoes.keys()).index(match_marca)

marca_nome = st.selectbox("Marca", list(marca_opcoes.keys()), index=index_marca)
marca_id = marca_opcoes.get(marca_nome)

# 2) MODELOS
# Só carrega se tiver marca
if marca_id:
    dados_modelos = listar_modelos(tipo_api, marca_id)
    modelos = dados_modelos.get("modelos", [])
    modelo_opcoes = {m["nome"]: m["codigo"] for m in modelos}
    
    # Tenta adivinhar o modelo (Muito difícil acertar exato, mas tenta aproximar)
    index_modelo = 0
    if st.session_state.dados_placa:
        # A placa retorna "CIVIC", a FIPE retorna "Civic Sedan LX 2.0..."
        # O fuzzy match aqui é arriscado, então deixamos o padrão ou tentamos algo genérico
        # Melhor estratégia: Se o nome da placa estiver CONTIDO no nome da FIPE
        termo_placa = st.session_state.dados_placa['modelo'].upper()
        for i, nome_fipe in enumerate(modelo_opcoes.keys()):
            if termo_placa in nome_fipe.upper():
                index_modelo = i
                break

    modelo_nome = st.selectbox("Modelo", list(modelo_opcoes.keys()), index=index_modelo)
    modelo_id = modelo_opcoes.get(modelo_nome)

    # 3) ANOS
    if modelo_id:
        anos = listar_anos(tipo_api, marca_id, modelo_id)
        ano_opcoes = {a["nome"]: a["codigo"] for a in anos}
        
        # Tenta adivinhar o ano
        index_ano = 0
        if st.session_state.dados_placa:
            ano_placa = str(st.session_state.dados_placa['ano'])
            # A FIPE retorna "2021 Gasolina", precisamos dar match no "2021"
            for i, nome_ano_fipe in enumerate(ano_opcoes.keys()):
                if ano_placa in nome_ano_fipe:
                    index_ano = i
                    break

        ano_nome = st.selectbox("Ano Modelo", list(ano_opcoes.keys()), index=index_ano)
        ano_codigo = ano_opcoes.get(ano_nome)

        # BOTÃO BUSCAR VALOR
        if st.button("💰 Obter Valor FIPE", type="primary", use_container_width=True):
            try:
                info = buscar_valor_fipe(tipo_api, marca_id, modelo_id, ano_codigo)
                valor_str = info.get("Valor")
                if valor_str:
                    st.session_state.fipe_valor_str = valor_str
                    st.session_state.fipe_valor_float = brl_to_float(valor_str)
                    st.session_state.veiculo_desc = f"{marca_nome} - {modelo_nome} ({ano_nome})"
                    st.success(f"Valor Tabela: {valor_str}")
                else:
                    st.error("Erro ao buscar valor.")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

st.divider()

# --- FORMULÁRIO DO CLIENTE ---
st.markdown("### 3. Dados do Cliente")
c1, c2 = st.columns(2)
cliente = c1.text_input("Nome do Cliente")
consultor = c2.text_input("Nome do Consultor")
contato = st.text_input("WhatsApp do Cliente")

# --- FINALIZAÇÃO ---
gerar_ok = st.session_state.fipe_valor_float is not None

if st.button("🚀 Gerar Cotação Final", disabled=not gerar_ok, type="primary"):
    dados_finais = {
        "cliente": cliente,
        "modelo": st.session_state.veiculo_desc,
        "fipe": st.session_state.fipe_valor_str,
        "placa": placa_input if placa_input else "N/A"
    }
    st.write("Dados prontos para o gerador de imagem:", dados_finais)
    # AQUI VOCÊ CHAMA SUA FUNÇÃO criar_proposta(dados_finais)
