window.survey = new Survey.Model(
    {
        pages: [
            {
                name: "page3",
                elements: [
                    {   isRequired: true,
                        type: "radiogroup",
                        name: "protocoloRealizado",
                        title: "Protocolo realizado ?",
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
                    {   isRequired: true,
                        type: "text",
                        name: "dataProtocolo",
                        visible: false,
                        visibleIf: "{protocoloRealizado} = 'S'",
                        title: "Data de protocolo",
                        inputType: "date"
                    },
                    {   isRequired: true,
                        type: "radiogroup",
                        name: "question1",
                        visible: false,
                        visibleIf: "{protocoloRealizado}= 'S'",
                        title: "Despesas reembolsáveis ?",
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
                    {  isRequired: false,
                        type: "text",
                        name: "obsRelevantes",
                        visible: false,
                        visibleIf: "{protocoloRealizado} = 'S'",
                        title: "Observações Relevantes: "
                    },
                    {   isRequired: true,
                        type: "text",
                        name: "justificativaNProtocolo",
                        visible: false,
                        visibleIf: "{protocoloRealizado} = 'N'",
                        title: "Justificativa"
                    }
                ]
            }
        ]
    }
);
