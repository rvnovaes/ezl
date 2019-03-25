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
                    "model": {
                        "title": "Classe",
                        "type": "string",
                        "enum": [
                            "core.Person",
                        ],
                        "default": "core.Person"
                    },
                    "field_list": {
                        "title": "Campo utilizado para a lista de opções",
                        "type": "string",
                        "enum": [
                            "auth_user__username",
                            "legal_name",
                            "name",
                        ]
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

DEFAULT_VALUE = {
    'office_id': None,
    'template_key': None,
    'template_type': None,
    'value': None,
}
