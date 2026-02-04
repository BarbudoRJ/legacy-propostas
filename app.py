import json

class CotadorApp:
    def __init__(self, config_json):
        self.config = config_json
        self.regras = config_json['regras_gerais']
        self.matriz = config_json['matriz_precos']
        self.coberturas_matriz = config_json['matriz_coberturas_por_tipo']
        self.catalogo = config_json['coberturas_catalogo']

    def calcular_cotacao(self, tipo_veiculo, regiao, valor_fipe):
        # 1. Validar Limite FIPE
        limite = self.regras['limite_fipe'].get(tipo_veiculo)
        if valor_fipe > limite:
            return {"erro": self.regras['comportamento_acima_do_limite']['mensagem']}

        # 2. Encontrar a Faixa de Preço
        faixas = self.matriz.get(tipo_veiculo, {}).get(regiao, [])
        faixa_ativa = None
        for f in faixas:
            if f['faixa']['min'] <= valor_fipe <= f['faixa']['max']:
                faixa_ativa = f
                break
        
        if not faixa_ativa or all(v is None for v in faixa_ativa['planos'].values()):
            return {"erro": "Preços não configurados para esta faixa/região (Verificar PDF)."}

        # 3. Construir Resultado por Plano
        resultado_planos = {}
        coberturas_por_plano = {}
        
        precos_planos = faixa_ativa['planos']
        
        for plano, preco in precos_planos.items():
            if preco is not None:
                resultado_planos[plano] = preco
                # Busca coberturas no catálogo filtrando pelo que é 'true' na matriz de coberturas
                mapa_cob = self.coberturas_matriz[tipo_veiculo][regiao].get(plano, {})
                
                coberturas_por_plano[plano] = [
                    self.catalogo[cob_id]['label'] 
                    for cob_id, ativo in mapa_cob.items() if ativo
                ]

        return {
            "status": "sucesso",
            "veiculo": tipo_veiculo,
            "regiao": regiao,
            "fipe": valor_fipe,
            "cotacao": resultado_planos,
            "coberturas": coberturas_por_plano,
            "icones": self.config['ui']['output_style']
        }

# --- TESTE DO CÓDIGO ---
# (Assumindo que a variável 'data' contém o seu JSON)
# data = json.loads(''' seu json aqui ''')

app = CotadorApp(data)
resultado = app.calcular_cotacao("carro", "capital", 25000)

if "erro" in resultado:
    print(f"❌ Erro: {resultado['erro']}")
else:
    print(f"--- COTAÇÃO PARA VEÍCULO DE R$ {resultado['fipe']} ---")
    for plano, valor in resultado['cotacao'].items():
        print(f"\nPlano {plano.upper()}: R$ {valor:.2f}")
        print(f"Coberturas: {', '.join(resultado['coberturas'][plano])}")
