CHARACTERISTICS = {
    'options': [
        {
            'name': 'acting_area',
            'title': 'Área de atuação',
            'options': ['Cível', 'Criminal', 'Trabalhista', 'Indiferente'],  # deixar apenas uma quando for o caso
            'multiple': False
        },
        {
            'name': 'participants',
            'title': 'Participantes',
            'options': ['Advogado', 'Preposto'],  # deixar todos os participantes
            'multiple': True
        },
        {
            'name': 'criticality',
            'title': 'Criticidade',
            'options': ['Urgente'],
            'multiple': False
        },
    ]
}
