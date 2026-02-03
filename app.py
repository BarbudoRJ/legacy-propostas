import urllib.parse

def montar_mensagem_whatsapp(dados):
    # mensagem curta e operacional (sem parágrafo gigante)
    msg = (
        f"Olá, {dados['cliente']}! Segue sua cotação LEGACY.\n\n"
        f"Veículo: {dados['modelo']} | Ano: {dados['ano']}\n"
        f"FIPE: {dados['fipe']} | Adesão: R$ {dados['adesao']}\n\n"
        f"Planos (mensal):\n"
        f"Econ: {dados['precos'][0]}\n"
        f"Básico: {dados['precos'][1]}\n"
        f"Plus: {dados['precos'][2]}\n"
        f"Premium: {dados['precos'][3]}\n\n"
        f"*Pagamento antecipado gera desconto.*\n"
        f"A cotação pode sofrer alterações baseadas nos valores vigentes."
    )
    return msg

# Inicializa states
if "cotacao_gerada" not in st.session_state:
    st.session_state.cotacao_gerada = False
if "img_bytes" not in st.session_state:
    st.session_state.img_bytes = None
if "whatsapp_link" not in st.session_state:
    st.session_state.whatsapp_link = None

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

# Se você tiver telefone do cliente no app, o envio fica perfeito.
telefone = st.text_input("WhatsApp do Cliente (DDD + número)", placeholder="Ex: 21999998888")

if st.button("GERAR COTAÇÃO", type="primary"):
    if fipe > 0 and cliente and modelo and ano:
        precos = calcular_mensalidades(fipe, regiao)
        if precos:
            dados = {
                "cliente": cliente,
                "consultor": consultor,
                "modelo": modelo,
                "ano": ano,
                "fipe": f"R$ {fipe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "precos": precos,
                "adesao": adesao,
            }
            img = criar_proposta(dados)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.session_state.img_bytes = buf.getvalue()
            st.session_state.cotacao_gerada = True

            # monta link do WhatsApp
            msg = montar_mensagem_whatsapp(dados)
            msg_enc = urllib.parse.quote(msg)

            if telefone.strip():
                st.session_state.whatsapp_link = f"https://wa.me/55{telefone.strip()}?text={msg_enc}"
            else:
                # sem telefone: abre WhatsApp e deixa o consultor escolher contato
                st.session_state.whatsapp_link = f"https://wa.me/?text={msg_enc}"

            st.image(img, caption="Cotação gerada (confira antes de enviar)", width=420)
            st.download_button(
                "📥 BAIXAR IMAGEM",
                st.session_state.img_bytes,
                file_name=f"Cotacao_{cliente}.png",
                mime="image/png"
            )
        else:
            st.warning("Não encontrei faixa de preço para esse FIPE.")
    else:
        st.warning("Preencha Cliente, Modelo, Ano e FIPE.")

# Botão verde só aparece depois da geração
if st.session_state.cotacao_gerada and st.session_state.whatsapp_link:
    st.markdown(
        f"""
        <a href="{st.session_state.whatsapp_link}" target="_blank" style="text-decoration:none;">
            <button style="
                background-color:#16a34a;
                color:white;
                border:none;
                padding:14px 18px;
                font-size:16px;
                border-radius:12px;
                cursor:pointer;
                width:100%;
                font-weight:700;">
                ✅ ENVIAR COTAÇÃO (WhatsApp)
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )
    st.caption("Dica: ao abrir o WhatsApp, anexe a imagem gerada (baixada) e envie.")
