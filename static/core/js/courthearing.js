window.survey = new Survey.Model(
    {
        pages: [
            {
                name: "page1",
                elements: [
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ],
                        isRequired: true,
                        name: "comparecimentoAudiencia",
                        title: "Houve comparecimento na audiência?"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ],
                        isRequired: true,
                        name: "audienciaRealizada",
                        title: "Audiência Realizada?",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='S'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "SA",
                                text: "Advogado"
                            },
                            {
                                value: "AP",
                                text: "Advogado + Preposto"
                            },
                            {
                                value: "SP",
                                text: "Preposto"
                            }
                        ],
                        isRequired: true,
                        name: "tipoComparecimento",
                        title: "Tipo de comparecimento:",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='S'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            },
                            {
                                value: "PC",
                                text: "Proposta Condicionada"
                            }
                        ],
                        isRequired: true,
                        name: "orientacaoAcordo",
                        title: "Orientações para realização do acordo:",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='S'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ],
                        isRequired: true,
                        name: "acordoRealizado",
                        title: "Acordo realizado?",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='S'"
                    },
                    {
                        type: "text",
                        inputType: "number",
                        name: "valorDanoMoral",
                        title: "Valor dano Moral",
                        visible: false,
                        visibleIf: "{acordoRealizado}='S'"
                    },
                    {
                        type: "text",
                        inputType: "number",
                        name: "valorDanoMaterial",
                        title: "Valor dano material:",
                        visible: false,
                        visibleIf: "{acordoRealizado}='S'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ],
                        isRequired: true,
                        name: "devolucaoProduto",
                        title: "Devolução de Produtos?",
                        visible: false,
                        visibleIf: "{acordoRealizado}='S'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ],
                        isRequired: true,
                        name: "reparo",
                        title: "Reparo?",
                        visible: false,
                        visibleIf: "{acordoRealizado}='S'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ],
                        isRequired: true,
                        name: "trocaProduto",
                        title: "Troca de Produto?",
                        visible: false,
                        visibleIf: "{acordoRealizado}='S'"
                    },
                    {
                        type: "text",
                        name: "justificativaNAcordo",
                        title: "Justificativa do não acordo:",
                        visible: false,
                        visibleIf: "{acordoRealizado}='N'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "FIS",
                                text: "Físico"
                            },
                            {
                                value: "DIG",
                                text: "Digital"
                            }
                        ],
                        isRequired: true,
                        name: "tipoProcesso",
                        title: "Processo",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='S'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ],
                        isRequired: true,
                        name: "temAdvHabilitado",
                        title: "Advogado Habilitado?",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='S'"
                    },
                    {
                        isRequired: true,
                        type: "text",
                        name: "advHabilitado",
                        title: "Qual Advogado?",
                        visible: false,
                        visibleIf: "{temAdvHabilitado}='S'"
                    },
                    {
                        isRequired: true,
                        type: "text",
                        name: "obsRelevantes",
                        title: "Observações Relevantes",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='S'"
                    },
                    {
                        type: "radiogroup",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ],
                        isRequired: true,
                        name: "despReembolsaveis",
                        title: "Despesas reembolsáveis?",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='S'"
                    }, {
                        type: "file",
                        name: "debiteDiligencia",
                        visible: false,
                        visibleIf: "{despReembolsaveis} = 'S'",
                        title: "Debite de Diligência",
                        storeDataAsText: true, showPreview: true,imageWidth: 150
                    },
                    {
                        type: "file",
                        name: "gedDiligencia",
                        title: "GED",
                        storeDataAsText: true, showPreview: true,imageWidth: 150
                    },
                    {
                        isRequired: true,
                        type: "text",
                        name: "justNCompAudiencia",
                        title: "Justificativa do não comparecimento",
                        visible: false,
                        visibleIf: "{comparecimentoAudiencia}='N'"
                    }
                ]
            }
        ]
    }
);


