CARD = {
    "title": "string",
    "subtitle": "string",
    "value": "string",
    "percent": "string",
    "direction": "string"
}

DOUGHNUT = {
	"title": "string",
	"labels": "list", 
	"values": "list",
}

LINE = {
  	'labels': ["PONTOS DA LINHA EX: [JANEIRO, FEVEREIRO, MARCO]"],
  	'datasets': [
    	{
          'label': 'LABEL DO INDICADOR EX: (AUDIÊCIAS POR MÊS)', 
          'data': ['VALORES DO INDICADOR EX: 20, 47, 50'],           
          'backgroundColor': 'COR DO BACKGROUND DE FUNDO CASO FILL = True, EX: blue', 
          'borderColor': 'COR DA BORDA DA LINHA EX: blue', 
          'fill': False
        },      	     
    ]
}