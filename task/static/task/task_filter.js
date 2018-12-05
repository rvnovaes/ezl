class TaskFilter {
	constructor() {		
		this.elExportResults = $('#export-result');
        this.startOnClickElExportResults();
	}	

	get formData() {
		return $("form").serializeArray();
	}

	get query() {
		let formData = this.formData;
		let data = {};
		$(formData ).each(function(index, obj){
		    let element = $('form [name=' + obj.name);
			let value = obj.value;
		    if (element.hasClass('twitter-typeahead')){
			    value = element.attr('data-value')
		    }
			data[obj.name] = value;
		});
		return data;
	}

    getXlsx(fileName='task-filter') {
		let request = new XMLHttpRequest();
		fileName += '.xlsx';
		let params = $.param(this.query);
		params += '&export_result=true';
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
            this.swalLoading('os resultados da pesquisa');
            this.getXlsx('resultados_da_pesquisa');
        });
    }

    swalLoading(title) {
	    swal({
			title: `Exportando ${title} para o Excel`,
	        html: '<h3>Aguarde...</h3>',
			onOpen: ()=>{
				swal.showLoading();
			}
		});
    }
}