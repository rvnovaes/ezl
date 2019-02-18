class TaskFilter {
	constructor() {		
		this.elExportResults = $('#export-result');
		this.elExportAnswers = $('#export-answers');
        this.startOnClickElExportResults();
        this.startOnClickElExportAnswers();
	}	

	get formData() {
		return $("form").serializeArray();
	}

	get query() {
		let formData = this.formData;
		let data = {};
		data['task_status'] = [];
		$(formData).each(function(index, obj){
		    let element = $('form [name=' + obj.name);
			let value = obj.value;
		    if (element.hasClass('twitter-typeahead')){
			    value = element.attr('data-value');
		    }
		    if (obj.name === 'task_status'){
				data[obj.name].push(value);
			} else {
				data[obj.name] = value;
			}
		});
		return data;
	}

    getXlsx(fileName='task-filter', typeXls='export_result') {
		let request = new XMLHttpRequest();
		fileName += '.xlsx';
		let params = $.param(this.query, true);
		params += `&${typeXls}=true`;
		let url = `/dashboard/filtrar/?${params}`;
		request.open('GET', url, true);
		request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
		request.responseType = 'blob';
		request.onload = function(e) {
		    if (this.status === 200) {
		        var blob = this.response;
		        if(window.navigator.msSaveOrOpenBlob) {
		            window.navigator.msSaveBlob(blob, fileName);
		        }
		        else{
		            var downloadLink = window.document.createElement('a');
		            var contentTypeHeader = request.getResponseHeader("Content-Type");
		            downloadLink.href = window.URL.createObjectURL(new Blob([blob], { type: contentTypeHeader }));
		            downloadLink.download = fileName;
		            document.body.appendChild(downloadLink);
		            downloadLink.click();
		            document.body.removeChild(downloadLink);
		           }
		       }
		       swal.close();
		   };
       request.send();
	}

	startOnClickElExportResults() {
        this.elExportResults.on('click', () => {
            this.swalLoading("as OS's");
            this.getXlsx('resultados_da_pesquisa');
        });
    }

	startOnClickElExportAnswers() {
        this.elExportAnswers.on('click', () => {
            this.swalLoading('as respostas dos formulários');
            this.getXlsx('respostas_dos_formularios', 'export_answers');
        });
    }

    swalLoading(title) {
	    swal({
			title: `Exportação para o Excel`,
			html: '<h4>Aguarde... Exportando ' + title + '.</h4>',
			onOpen: ()=>{
				swal.showLoading();
			}
		});
    }
}