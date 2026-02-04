{
  "versao": "LEGACY_COTACAO_APP_v1",
  "moeda": "BRL",
  "fonte": {
    "descricao": "Tabela LEGACY (PDF) + ajustes solicitados no chat",
    "observacao": "Eu NÃO tenho aqui o PDF completo nesta conversa. Então só consigo preencher com 100% de certeza o trecho que você já colou (carro_capital nas 3 primeiras faixas). O restante vai como estrutura pronta + campos TODO para você colar os números."
  },
  "ui": {
    "output_style": {
      "tabela": "skeuomorphic",
      "icon_ok": "✅",
      "icon_no": "❌"
    },
    "itens_adicionados_na_cotacao": [
      "incendio",
      "clube_certo"
    ]
  },
  "dominios": {
    "tipos_veiculo": [
      "carro",
      "moto",
      "utilitario"
    ],
    "regioes": [
      "capital",
      "serrana"
    ],
    "planos": [
      "economico",
      "basico",
      "plus",
      "premium"
    ]
  },
  "regras_gerais": {
    "limite_fipe": {
      "carro": 100000,
      "utilitario": 100000,
      "moto": 30000
    },
    "comportamento_acima_do_limite": {
      "acao": "bloquear_cotacao",
      "mensagem": "Valor FIPE acima do limite para este tipo de veículo. Fale com um consultor para cotação personalizada."
    },
    "faixas_inclusivas": true
  },
  "coberturas_catalogo": {
    "assistencia_24h": {
      "label": "Assistência 24h",
      "tipo": "servico"
    },
    "reboque": {
      "label": "Reboque",
      "tipo": "servico"
    },
    "colisao": {
      "label": "Colisão",
      "tipo": "cobertura"
    },
    "roubo_furto": {
      "label": "Roubo e Furto",
      "tipo": "cobertura"
    },
    "terceiros": {
      "label": "Danos a Terceiros",
      "tipo": "cobertura"
    },
    "incendio": {
      "label": "Incêndio",
      "tipo": "cobertura",
      "observacao": "ADICIONADO por você na cotação"
    },
    "clube_certo": {
      "label": "Clube Certo",
      "tipo": "beneficio",
      "observacao": "ADICIONADO por você na cotação"
    }
  },
  "matriz_precos": {
    "carro": {
      "capital": [
        {
          "faixa": { "min": 0, "max": 10000 },
          "planos": {
            "economico": 75.0,
            "basico": 86.6,
            "plus": 110.4,
            "premium": 151.5
          }
        },
        {
          "faixa": { "min": 10001, "max": 20000 },
          "planos": {
            "economico": 75.0,
            "basico": 110.6,
            "plus": 137.49,
            "premium": 170.49
          }
        },
        {
          "faixa": { "min": 20001, "max": 30000 },
          "planos": {
            "economico": 75.0,
            "basico": 126.8,
            "plus": 172.69,
            "premium": 202.5
          }
        },
        {
          "faixa": { "min": 30001, "max": 40000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher a partir do PDF"
        },
        {
          "faixa": { "min": 40001, "max": 50000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher a partir do PDF"
        },
        {
          "faixa": { "min": 50001, "max": 60000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher a partir do PDF"
        },
        {
          "faixa": { "min": 60001, "max": 70000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher a partir do PDF"
        },
        {
          "faixa": { "min": 70001, "max": 80000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher a partir do PDF"
        },
        {
          "faixa": { "min": 80001, "max": 90000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher a partir do PDF"
        },
        {
          "faixa": { "min": 90001, "max": 100000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher a partir do PDF"
        }
      ],
      "serrana": [
        {
          "faixa": { "min": 0, "max": 10000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher tabela carro_serrana do PDF"
        }
      ]
    },
    "utilitario": {
      "capital": [
        {
          "faixa": { "min": 0, "max": 100000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher tabela utilitario_capital do PDF (com faixas reais)"
        }
      ],
      "serrana": [
        {
          "faixa": { "min": 0, "max": 100000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher tabela utilitario_serrana do PDF (com faixas reais)"
        }
      ]
    },
    "moto": {
      "capital": [
        {
          "faixa": { "min": 0, "max": 30000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher tabela moto_capital do PDF (com faixas reais até 30k)"
        }
      ],
      "serrana": [
        {
          "faixa": { "min": 0, "max": 30000 },
          "planos": {
            "economico": null,
            "basico": null,
            "plus": null,
            "premium": null
          },
          "TODO": "Preencher tabela moto_serrana do PDF (com faixas reais até 30k)"
        }
      ]
    }
  },
  "matriz_coberturas_por_tipo": {
    "carro": {
      "capital": {
        "economico": {
          "assistencia_24h": true,
          "reboque": true,
          "colisao": false,
          "roubo_furto": false,
          "terceiros": false,
          "incendio": false,
          "clube_certo": true
        },
        "basico": {
          "assistencia_24h": true,
          "reboque": true,
          "colisao": true,
          "roubo_furto": true,
          "terceiros": false,
          "incendio": true,
          "clube_certo": true
        },
        "plus": {
          "assistencia_24h": true,
          "reboque": true,
          "colisao": true,
          "roubo_furto": true,
          "terceiros": true,
          "incendio": true,
          "clube_certo": true
        },
        "premium": {
          "assistencia_24h": true,
          "reboque": true,
          "colisao": true,
          "roubo_furto": true,
          "terceiros": true,
          "incendio": true,
          "clube_certo": true
        }
      },
      "serrana": {
        "economico": { "TODO": "Definir coberturas do carro_serrana por plano" },
        "basico": { "TODO": "Definir coberturas do carro_serrana por plano" },
        "plus": { "TODO": "Definir coberturas do carro_serrana por plano" },
        "premium": { "TODO": "Definir coberturas do carro_serrana por plano" }
      }
    },
    "utilitario": {
      "capital": {
        "economico": { "TODO": "Definir coberturas utilitario_capital por plano" },
        "basico": { "TODO": "Definir coberturas utilitario_capital por plano" },
        "plus": { "TODO": "Definir coberturas utilitario_capital por plano" },
        "premium": { "TODO": "Definir coberturas utilitario_capital por plano" }
      },
      "serrana": {
        "economico": { "TODO": "Definir coberturas utilitario_serrana por plano" },
        "basico": { "TODO": "Definir coberturas utilitario_serrana por plano" },
        "plus": { "TODO": "Definir coberturas utilitario_serrana por plano" },
        "premium": { "TODO": "Definir coberturas utilitario_serrana por plano" }
      }
    },
    "moto": {
      "capital": {
        "economico": { "TODO": "Definir coberturas moto_capital por plano" },
        "basico": { "TODO": "Definir coberturas moto_capital por plano" },
        "plus": { "TODO": "Definir coberturas moto_capital por plano" },
        "premium": { "TODO": "Definir coberturas moto_capital por plano" }
      },
      "serrana": {
        "economico": { "TODO": "Definir coberturas moto_serrana por plano" },
        "basico": { "TODO": "Definir coberturas moto_serrana por plano" },
        "plus": { "TODO": "Definir coberturas moto_serrana por plano" },
        "premium": { "TODO": "Definir coberturas moto_serrana por plano" }
      }
    }
  },
  "saida_cotacao": {
    "campos": [
      "tipo_veiculo",
      "regiao",
      "valor_fipe",
      "faixa_encontrada",
      "planos_com_precos",
      "coberturas_por_plano",
      "itens_extras",
      "avisos"
    ],
    "itens_extras_fixos": [
      "incendio",
      "clube_certo"
    ]
  }
}
