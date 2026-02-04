const legacyConfig = {
    // ... Seu JSON completo entra aqui
};

class MotorCotacaoLegacy {
    constructor(config) {
        this.config = config;
    }

    // Método principal para gerar a cotação
    gerar(tipoVeiculo, regiao, valorFipe) {
        try {
            // 1. Validação de Limites
            const limite = this.config.regras_gerais.limite_fipe[tipoVeiculo];
            if (valorFipe > limite) {
                return { 
                    erro: true, 
                    msg: this.config.regras_gerais.comportamento_acima_do_limite.mensagem 
                };
            }

            // 2. Busca da Faixa de Preço
            const faixas = this.config.matriz_precos[tipoVeiculo][regiao];
            const faixaEncontrada = faixas.find(f => 
                valorFipe >= f.faixa.min && valorFipe <= f.faixa.max
            );

            if (!faixaEncontrada || this._isFaixaVazia(faixaEncontrada)) {
                return { 
                    erro: true, 
                    msg: "Valores para esta faixa ainda não mapeados no sistema (Aguardando PDF)." 
                };
            }

            // 3. Construção do Objeto de Saída (Planos e Coberturas)
            const planosDisponiveis = {};
            
            Object.keys(faixaEncontrada.planos).forEach(planoNome => {
                const precoBase = faixaEncontrada.planos[planoNome];
                
                if (precoBase !== null) {
                    planosDisponiveis[planoNome] = {
                        valor: precoBase,
                        coberturas: this._obterCoberturas(tipoVeiculo, regiao, planoNome),
                        status: this.config.ui.output_style.icon_ok
                    };
                }
            });

            return {
                erro: false,
                dados: {
                    veiculo: tipoVeiculo.toUpperCase(),
                    regiao: regiao.toUpperCase(),
                    fipe: valorFipe.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }),
                    planos: planosDisponiveis
                }
            };

        } catch (e) {
            return { erro: true, msg: "Erro interno ao processar cotação. Verifique os domínios." };
        }
    }

    // Auxiliar: Filtra as coberturas ativas no catálogo para aquele plano
    _obterCoberturas(tipo, regiao, plano) {
        const matriz = this.config.matriz_coberturas_por_tipo[tipo][regiao][plano];
        const catalogo = this.config.coberturas_catalogo;

        return Object.keys(matriz)
            .filter(key => matriz[key] === true)
            .map(key => catalogo[key]?.label || key);
    }

    _isFaixaVazia(faixa) {
        return Object.values(faixa.planos).every(v => v === null);
    }
}

// --- EXEMPLO DE USO ---

const motor = new MotorCotacaoLegacy(legacyConfig);

// Simulação: Carro na Capital com FIPE de 25k
const resultado = motor.gerar("carro", "capital", 25000);

if (resultado.erro) {
    console.error(`❌ STATUS: ${resultado.msg}`);
} else {
    console.log(`✅ COTAÇÃO GERADA - ${resultado.dados.veiculo}`);
    console.log(`Valor FIPE: ${resultado.dados.fipe}`);
    console.table(resultado.dados.planos);
}
