// Classe base do relatorio que deve ser herdada
class ReportToPay {
	constructor() {
		this.btnDownloadXlsx = $('#btn-download-xlsx');
		this.elTableBody = $('#os-table-body');
		this.elTableFoot = $('#os-table-foot');
		this.elBtnBilling = $('#btn-billing');		
		this.elCheckAllItems = $('#checkAll');
	    this.count = 0;
	    this.totalToPay=0;
	    this.currentOffice = null;
	    this.currentClient = null;	
	    this.tasksToPay = [];
	    this.allTaskIds = [] ;  
	    this.htmlTable = ``;
	    this.elInputClient = $('[name=client]');
	    this.elFinishedDate0 = $("#finished_in_0");
	    this.elFinishedDate1 = $("#finished_in_1");
	    this.unsetOnClickDownloadXls();
	    this.startOnClickDownloadXls();
	}	

	showBtnDownloadXlsxFile() {
		this.btnDownloadXlsx.show();
	}

	getBillingDate(billingData) {
	    if (!billingData) {
	        return '';
	    }
	    return this.formatLocalDateTime(billingData)
	}

	setDefaultOfNull(value){
	    if (!value) {
	        return '';
	    }
	    return value;
	}

	formatLocalDateTime(strDate) {
	    let date = new Date(strDate);
	    return `${date.toLocaleString("pt-BR")}`;
	}

	get formData() {
		return $("form").serializeArray();
	}

	get query() {
		let formData = this.formData;
		let data = {};
		$(formData ).each(function(index, obj){
			data[obj.name] = obj.value;
		});
		return data;
	}

	get finishedDate0() {
		return this.elFinishedDate0.val()
	}

	get finishedDate1() {
		return this.elFinishedDate1.val()
	}

	unsetOnClickDownloadXls() {
		this.btnDownloadXlsx.prop("onclick", null).off("click");
	}

	startOnClickDownloadXls() {
		this.btnDownloadXlsx.on('click', ()=>{
			this.disableBtnDownloadXlsx();
			this.getXlsx();
		});
	}

	startOnCheckAllItems() {
		this.elCheckAllItems.on('change', function() {
			$('#os-table input:checkbox').not(this).prop('checked', this.checked);
		});
	}

	startOnCheckItem(){
		let self = this;
        $('#os-table input:checkbox').on('change', function(){
            if ($(this).attr('id') === 'checkAll') {
                if ($(this).is(':checked')) {
                    self.tasksToPay = self.allTaskIds;
                } else {
                    self.tasksToPay = [];
                }
            } else {
                if ($(this).is(':checked')) {
                    self.tasksToPay.push($(this).val());
                } else {
                    self.tasksToPay.splice(self.tasksToPay.indexOf($(this).val(), 1));
                }                            
            }
        });
	}

	startOnClickBtnBilling() {
		this.elBtnBilling.on('click', ()=>{
            if (this.tasksToPay.length == 0){
                swal({
                    title: "Importante",
                    text: "Você deve selecionar pelo menos uma OS para ser faturada.",
                    type: "warning",
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Ok"
                });
                return false;
            } else {        	
	            $('#modal-billing').modal();
	            $('#action-billing').click(()=>{                
	                $('#modal-billing').modal('hide');
	                this.billingTasks();
	            });                        			
            }
		});
	}

	billingTasks(){
        let data = {tasks: this.tasksToPay};
        $.ajax({
            type: 'POST',
            url: '/relatorios/os-a-pagar-data',
            data: data,
            success: function (response) {
                location.reload();
            },
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
            },
            dataType: 'json'
        });				
	}	

	async search() {
		const response = await this.getData().then((data)=>{
			 return this.data = data
		});
		return response;
	}

	async getData() {
		const response = await $.ajax({
	        method: 'GET', 
	        url: `/relatorios/os-a-pagar-data`, 
	        data: this.query, 
	        dataType: 'json', 	        
		});
		return JSON.parse(response);
	}

	getXlsx() {
		swal({
			title: 'Exportando para o Excel',
	        html: '<h4>Aguarde...</h4>',
			allowOutsideClick: false,
			onOpen: ()=>{
				swal.showLoading();
			}
		});
		let request = new XMLHttpRequest();
		let fileName = 'os-a-pagar.xlsx';
		let params = $.param(this.query);
		let url = `/relatorios/os-a-pagar-xlsx?${params}`;
		request.open('GET', url, true);
		request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
		request.responseType = 'blob';
		request.onload = (e) => {
		    if (e.target.status === 200) {
		        let blob = e.target.response;
		        if(window.navigator.msSaveOrOpenBlob) {
		            window.navigator.msSaveBlob(blob, fileName);
		        } else {
		            let downloadLink = window.document.createElement('a');
		            let contentTypeHeader = request.getResponseHeader("Content-Type");
		            downloadLink.href = window.URL.createObjectURL(new Blob([blob], { type: contentTypeHeader }));
		            downloadLink.download = fileName;
		            document.body.appendChild(downloadLink);
		            downloadLink.click();
		            document.body.removeChild(downloadLink);
		            window.URL.revokeObjectURL(downloadLink.href);
		           }
		       	}
		       	swal.close();
				this.enableBtnDownloadXlsx();
		   };
		   request.send();				
	}

	getSpanClientRefunds(clientRefunds) {
		if (clientRefunds) {
			return `
                <div class="col-xs-2">                    
                    <span class="badge badge-danger pull-right"><i class="fa fa-check"></i> Reembolsa valor</span>
                </div>
			`;
		}
		return '';
	}

	getTrTask(task) {    
	    let elBilling = '';
	    if (!task.billing_date && this.elCheckAllItems.length > 0) {
	        elBilling = `<input type="checkbox" value="${task.task_id}"/>`;
	    } 
	    return `
	          <tr role="row" id="${task.task_id}">
	                <td></td>
	                <td></td>
	                <td>
	                    ${elBilling}
	                </td>
	                <td>
	                    <a href="" target="_new">
	                        ${task.parent_task_number}
	                    </a>
	                </td>
	                <td>${this.formatLocalDateTime(task.finished_date)}</td>
	                <td>${task.type_task}</td>
	                <td>${task.lawsuit_number}</td>
	                <td>${task.cost_center}</td>
	                <td>${task.court_district}</td>
	                <td>${task.opposing_party}</td>
	                <td>${this.setDefaultOfNull(task.task_legacy_code)}</td>
	                <td>${this.getBillingDate(task.billing_date)}</td>
	                <td>${task.charge_id}</td>
	                <td class="text-center"><center>${this.formatMoney(task.amount)}</center></td>
	            </tr>`;
	}

	getTrfoot() {
	    return `
	        <tr class="total-container">
	            <th colspan="12" class="text-right" >Total Geral (R$)</th>
	            <th colspan="2" class="text-right">${this.formatMoney(this.totalToPay.toFixed(2))}</th>
	        </tr>`;
		};   	

	getBtnBilling() {
	    return `
	        <div class="text-center" style="padding-top: 10px">
	            <button class="btn btn-success" id="btn-faturar">Faturar</button>
	        </div>            
	    `;
	}		

	addAmount(instance, key, value){
		if (!instance[key]) {
			instance[key] = parseFloat(value);
		} else {
			instance[key] += parseFloat(value);
		}
	}

	formatMoney(value) {
		return parseFloat(value).toLocaleString("pt-BR", { style: "currency" , currency:"BRL"});
	}

	async mountTable(data){		
		// Implementado nas classes que herdam
	}	


	async mountTrTask(task){
		this.htmlTable += this.getTrTask(task)
	}

	writeTable(){
		this.elTableBody.append(this.htmlTable)
		this.elTableFoot.append(this.getTrfoot())
		this.elBtnBilling.append(this.getBtnBilling())
	}

	async computeTotals(task){
		// Implementado nas classes que herdam
	}

	computeTotalToPay(task){
		this.totalToPay += parseFloat(task.amount)
	}	

	async makeReport(data) {
		// Implementado na classe que herda
	}

	async start(){
		swal({
	        title: "Carregando OS's",
	        html: '<h4>Aguarde...</h4>',
			allowOutsideClick: false,
	        onOpen: ()=> {
	        	swal.showLoading()
	        }
		});
		const data = await this.search();
		await this.makeReport(data);		
		swal.close()		
	}

	checkFinishedDate(){
		if (!(this.finishedDate0 || this.finishedDate1)){
			swal({
				 type: 'error',
				title: "Data de finalização",
				html: '<h3>Favor informar as datas de finalização para o filtro</h3>'
			});
			return false
		}
		return true
	}

	clear() {
		this.elTableBody.empty();
		this.elTableFoot.empty();
		this.elBtnBilling.empty();
	    this.count = 0;
	    this.totalToPay=0;
	    this.currentOffice = null;
	    this.currentClient = null;	
	    this.tasksToPay = [];
	    this.allTaskIds = [] ;  
	    this.htmlTable = ``;		
	}

	disableBtnDownloadXlsx(){
		this.btnDownloadXlsx.attr('disabled', true);
    }

	enableBtnDownloadXlsx(){
	    this.btnDownloadXlsx.attr('disabled', false);
    }
}

// Gera o relatorio agrupado por office
class ReportToPayGroupByOffice extends ReportToPay {
	constructor() {
		super();
		this.currentOffice;
		this.currentClient;
		this.totalByOffice = {};
		this.totalClientByOffice = {};
	}

	getTrOffice(officeId, officeName){
	    return `
	        <tr>
	            <th colspan="12">${officeName}</th>
	            <th></th>
	            <th><center><span office-id="${officeId}">|office=${officeId}|</span></center></th>
	        </tr>
	    `;
	}

	getTrClient(officeId, clientId, clientName, clientRefunds){
	    return `
	        <tr>
	            <th></th>
	            <th colspan="12">
	                <div class="col-xs-10">
	                    ${clientName}                            
	                </div>
	                ${this.getSpanClientRefunds(clientRefunds)}
	            </th>
	            <th><center><span client-id=${officeId}-${clientId}>|client=${officeId}-${clientId}|<span></center></th>
	        </tr>
	    `;
	}

	async mountTrOffice(task) {
		if(this.currentOffice !== task.office_id){
			this.currentOffice = task.office_id;
			this.currentClient = null;
			this.htmlTable += this.getTrOffice(task.office_id, task.office_name);
		}
	}

	async mountTrClient(task) {
		if(this.currentClient !== task.client_id) {
			this.currentClient = task.client_id; 
			this.htmlTable += this.getTrClient(task.office_id, task.client_id, task.client_name, task.client_refunds)
		}	
	}	

	async mountTable(task){				
    	// Monta <tr> do office
    	this.mountTrOffice(task);
    	// Monta <tr> do client
    	this.mountTrClient(task);
    	// Monta <tr> task
    	this.mountTrTask(task);
	}

	async replaceTotalByOffice(){
		Object.keys(this.totalByOffice).forEach((key)=>{
			this.htmlTable = this.htmlTable.replace(`|office=${key}|`, `${this.formatMoney(this.totalByOffice[key].toFixed(2))}`)			
		})
	}

	async replaceTotalClientByOffice(){
		Object.keys(this.totalClientByOffice).forEach((key)=>{
			this.htmlTable = this.htmlTable.replace(`|client=${key}|`, `${this.formatMoney(this.totalClientByOffice[key].toFixed(2))}`)			
		})
	}	

	computeTotalOffice(task){
		this.addAmount(this.totalByOffice, task.office_id, task.amount)
	}

	computeTotalClientByOffice(task){
		this.addAmount(this.totalClientByOffice, `${task.office_id}-${task.client_id}`, task.amount)
	}

	async computeTotals(task){
		this.computeTotalOffice(task)
		this.computeTotalClientByOffice(task)
		this.computeTotalToPay(task)
	}

	async makeReport(data) {
		while (data.length > 0) {			
		    data.splice(0, 1).forEach((task)=>{	
		    	this.allTaskIds.push(task.task_id);
		    	this.mountTable(task);		    	
		    	this.computeTotals(task);
		    });	
		}
		await this.replaceTotalByOffice();
		await this.replaceTotalClientByOffice();
		await this.writeTable();	
		this.startOnCheckAllItems();
		this.startOnCheckItem();
		this.startOnClickBtnBilling();
		this.showBtnDownloadXlsxFile();
	}
}

// Gera o relatorio agrupado por cliente
class ReportToPayGroupByClient extends ReportToPay {
	constructor() {
		super();
		this.currentOffice;
		this.currentClient;
		this.totalByClient = {};
		this.totalOfficeByClient = {};
	}

	getTrClient(clientId, clientName, clientRefunds){
	    return `
	        <tr>
	            <th colspan="12">
	            	<div class="col-xs-10">
	            		${clientName}
	            	</div>	
	            	${this.getSpanClientRefunds(clientRefunds)}
	            </th>
	            <th></th>
	            <th><center><span office-id="${clientId}">|client=${clientId}|</span></center></th>
	        </tr>
	    `
	}

	getTrOffice(clientId, officeId, officeName){
	    return `
	        <tr>
	            <th></th>
	            <th colspan="12">
	                <div class="col-xs-10">
	                    ${officeName}                            
	                </div>
	            </th>
	            <th><center><span client-id=${clientId}-${officeId}>|office=${clientId}-${officeId}|<span></center></th>
	        </tr>
	    `
	}

	async mountTrClient(task) {
		if(this.currentClient !== task.client_id){
			this.currentClient = task.client_id;
			this.currentOffice = null;
			this.htmlTable += this.getTrClient(task.client_id, task.client_name, task.client_refunds);			
		}
	}

	async mountTrOffice(task) {
		if(this.currentOffice !== task.office_id) {
			this.currentOffice = task.office_id; 
			this.htmlTable += this.getTrOffice(task.client_id, task.office_id, task.office_name)
		}	
	}

	async mountTable(task){				
    	// Monta <tr> do client
    	this.mountTrClient(task);
    	// Monta <tr> do office
    	this.mountTrOffice(task);
    	// Monta <tr> task
    	this.mountTrTask(task);
	}

	async replaceTotalByClient(){
		Object.keys(this.totalByClient).forEach((key)=>{
			this.htmlTable = this.htmlTable.replace(`|client=${key}|`, `${this.formatMoney(this.totalByClient[key].toFixed(2))}`)			
		})
	}


	async replaceTotalOfficeByClient(){
		Object.keys(this.totalOfficeByClient).forEach((key)=>{
			this.htmlTable = this.htmlTable.replace(`|office=${key}|`, `${this.formatMoney(this.totalOfficeByClient[key].toFixed(2))}`)			
		})
	}

	computeTotalClient(task){
		this.addAmount(this.totalByClient, task.client_id, task.amount)
	}

	computeTotalOfficeByClient(task){
		this.addAmount(this.totalOfficeByClient, `${task.client_id}-${task.office_id}`, task.amount)
	}

	async computeTotals(task){
		this.computeTotalClient(task);
		this.computeTotalOfficeByClient(task);
		this.computeTotalToPay(task);
	}

	async makeReport(data) {
		while (data.length > 0) {			
		    data.splice(0, 1).forEach((task)=>{	
		    	this.allTaskIds.push(task.task_id);
		    	this.mountTable(task);		    	
		    	this.computeTotals(task);
		    });	
		}
		await this.replaceTotalByClient();
		await this.replaceTotalOfficeByClient();
		await this.writeTable();	
		this.startOnCheckAllItems();
		this.startOnCheckItem();
		this.startOnClickBtnBilling();
		this.showBtnDownloadXlsxFile();
	}	
}