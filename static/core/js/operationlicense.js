window.survey = new Survey.Model(
    {
        pages: [
            {
                name: "page1",
                elements: [
                    {
                        type: "radiogroup",
                        name: "alvaraRetiradoAutos",
                        title: "Alvará retirado dos autos?",
                        isRequired: true,
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ]
                    },
                    {
                        type: "text",
                        name: "Justificativa de Alvará não retirado: ",
                        visible: false,
                        visibleIf: "{alvaraRetiradoAutos} = 'N'"
                    },
                    {
                        type: "radiogroup",
                        name: "viaOriginalEnviada",
                        visible: false,
                        visibleIf: "{alvaraRetiradoAutos} = 'S'",
                        title: "Via original encaminhada ? ",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ]
                    },
                    {
                        type: "text",
                        name: "dataRetiradoAutos",
                        visible: false,
                        visibleIf: "{campo1} = 'S'",
                        title: "Data da retirada do Alvará : ",
                        inputType: "datetime"
                    },
                    {
                        type: "radiogroup",
                        name: "alvaraLevadoBanco",
                        title: "Alvará levantado junto ao banco ? ",
                        isRequired: true,
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ]
                    },
                    {
                        type: "text",
                        name: "vlrLevantadoBanco",
                        visible: false,
                        visibleIf: "{alvaraLevadoBanco} = 'S'",
                        title: "Valor levantado : ",
                        inputType: "number"
                    },
                    {
                        type: "text",
                        name: "contaLevantamento",
                        visible: false,
                        visibleIf: "{alvaraLevadoBanco} = 'S'",
                        title: "Conta Bancária : "
                    },
                    {
                        type: "text",
                        name: "justAlvaraNLevantado",
                        visible: false,
                        visibleIf: "{alvaraLevadoBanco} = 'N'",
                        title: "Justificativa Alvará não retirado: "
                    },
                    {
                        type: "radiogroup",
                        name: "despReembolsaveis",
                        title: "Despesas reembolsáveis ? ",
                        choices: [
                            {
                                value: "S",
                                text: "Sim"
                            },
                            {
                                value: "N",
                                text: "Não"
                            }
                        ]
                    },
                    {
                        type: "file",
                        name: "debiteDiligencia",
                        visible: false,
                        visibleIf: "{despReembolsaveis} = 'S'",
                        title: "Debite de Diligência"
                    },
                    {
                        type: "text",
                        name: "obsRelevante",
                        visible: false,
                        visibleIf: "{despReembolsaveis} = 'S'",
                        title: "Observações relevantes: "
                    },
                    {
                        type: "file",
                        name: "gedDiligencia",
                        visible: false,
                        visibleIf: "{despReembolsaveis} = 'S'",
                        title: "GED de Diligência "
                    }
                ]
            }
        ]
    }
);