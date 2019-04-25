PARAMETERS = {
    'type': 'object',
    'options': {
        'disable_edit_json': True,
    },
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
        "boolean_default": {
            "title": "Valor padrão",
            "type": "string",
            "enum": [
                "True",
                "False"
            ],
            "enum_titles": [
                True,
                False
            ],
            "default": "core.Person"
        },
        "integer_default": {
            "title": "Valor padrão",
            "type": "integer",
        },
        "decimal_default": {
            "title": "Valor padrão",
            "type": "number",
        },
        "foreign_key_default": {
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
                            "auth.User"
                        ],
                        "default": "core.Person"
                    },
                    "field_list": {
                        "title": "Campo utilizado para a lista de opções",
                        "type": "string",
                        "enum": [
                            "legal_name",
                            "name",
                            "username",
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
        "list_default": {
            "type": "array",
            "format": "table",
            "title": "Lista de opções disponíveis",
            "uniqueItems": True,
            "items": {
                "type": "object",
                "title": "Opção",
                "properties": {
                    "value": {
                        "title": "Valor",
                        "type": "string",
                    },
                    "text": {
                        "title": "Texto",
                        "type": "string",
                    },
                    "is_default": {
                        "title": "Valor padrão",
                        "type": "boolean",
                        "format": "checkbox",
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