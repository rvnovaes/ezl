PARAMETERS = {
    'type': 'object',
    'title': 'Parâmetros de configuração',
    'required': [
        'is_required'
    ],
    'properties': {
        'is_required': {
            'title': 'Obrigatório',
            'type': 'boolean',
            'format': 'checkbox'
        },
        "model": {
            "type": "array",
            "format": "select",
            "title": "Tabelas de chave estrangeira",
            "uniqueItems": True,
            "items": {
                "type": "object",
                "title": "Modelo",
                "properties": {
                    "table": {
                        "title": "Classe",
                        "type": "string",
                        "enum": [
                            "Person",
                        ],
                        "default": "Person"
                    },
                    "extra_params": {
                        "title": "Parâmetros extra",
                        "type": "string",
                        "format": "python",
                        "options": {
                            "ace": {
                              "theme": "ace/theme/vibrant_ink",
                              "tabSize": 4,
                              "useSoftTabs": True,
                              "wrap": True
                            }
                        }
                    }
                }
            },
        },
    },
}
