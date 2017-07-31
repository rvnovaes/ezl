window.survey = new Survey.Model(
    {
        pages: [
            {
                name: "page2",
                elements: [
                    {
                        type: "radiogroup",
                        name: "cumprimento",
                        title: "Cumprimento de Ordem de Serviço do tipo Diligência",
                        isRequired: true,
                        choices: [
                            {
                                value: "item1",
                                text: "Diligência Cumprida"
                            },
                            {
                                value: "item2",
                                text: "Parcialmente Cumprida"
                            },
                            {
                                value: "item3",
                                text: "Não Cumprida"
                            }
                        ]
                    },
                    {
                        type: "radiogroup",
                        name: "docLegivel",
                        visible: false,
                        visibleIf: "{cumprimento}='item1' or {cumprimento}='item2'",
                        title: "Documento Legível?",
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
                        type: "radiogroup",
                        name: "despReembolsaveis",
                        visible: false,
                        visibleIf: "{cumprimento}='item1' or {cumprimento}='item2'",
                        title: "Despesas reembolsáveis?",
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
                        visibleIf: "{cumprimento}='item1' or {cumprimento}='item2'",
                        title: "Debite"
                    },
                    {
                        type: "text",
                        name: "obsRelevantes",
                        visible: false,
                        visibleIf: "{cumprimento} = 'item1'",
                        title: "Observações relevantes"
                    },
                    {
                        type: "radiogroup",
                        name: "motivoCumprimentoParcial",
                        visible: false,
                        visibleIf: " {cumprimento}='item2'",
                        title: "Por qual motivo a diligência foi parcialmente cumprida?",
                        choices: [
                            {
                                value: "item1",
                                text: "Autos indisponíveis"
                            },
                            {
                                value: "item2",
                                text: "Outro(a)"
                            }
                        ]
                    },
                    {
                        type: "text",
                        name: "Outro(a)",
                        visible: false,
                        visibleIf: "{motivoCumprimentoParcial}='item2'"
                    },
                    {
                        type: "file",
                        name: "gedDiligencia",
                        visible: false,
                        visibleIf: "{cumprimento}='item1' or {cumprimento}='item2'",
                        title: "GED"
                    },
                    {
                        type: "text",
                        name: "justificativaNCumprir",
                        visible: false,
                        visibleIf: "{cumprimento} ='item3'",
                        title: "Justificativa de não Cumprimento"
                    }
                ]
            }
        ]
    }
);
