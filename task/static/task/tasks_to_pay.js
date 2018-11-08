class ReportToPay {
	constructor() {				
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

	startOnCheckAllItems() {
		this.elCheckAllItems.on('change', function() {
			$('#os-table input:checkbox').not(this).prop('checked', this.checked);
		})
	}

	startOnCheckItem(){
		let self = this;
        $('#os-table input:checkbox').on('change', function(){
            if ($(this).attr('id') === 'checkAll') {
                if ($(this).is(':checked')) {
                    self.tasksToPay = self.allTaskIds
                } else {
                    self.tasksToPay = [];
                }
            } else {
                if ($(this).is(':checked')) {
                    self.tasksToPay.push($(this).val())    
                } else {
                    self.tasksToPay.splice(self.tasksToPay.indexOf($(this).val(), 1))
                }                            
            }
        })		
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
            }
            $('#modal-billing').modal();
            $('#action-billing').click(()=>{                
                $('#modal-billing').modal('hide');
                this.billingTasks();
            });                        			
		})
	}

	billingTasks(){
        let data = {tasks: this.tasksToPay};
        $.ajax({
            type: 'POST',
            url: location.href,
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
		})			
		return response		
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

	getTrTask(task) {    
	    let elBilling = '';
	    if (!task.billing_date) {
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
	                <td>${formatLocalDateTime(task.finished_date)}</td>
	                <td>${task.type_task}</td>
	                <td>${task.lawsuit_number}</td>
	                <td>${task.court_district}</td>
	                <td>${task.opposing_party}</td>
	                <td>${setDefaultOfNull(task.task_legacy_code)}</td>
	                <td>${getBillingDate(task.billing_date)}</td>
	                <td class="text-center"><center>${task.amount}</center></td>
	            </tr>            `
	}

	getTrfoot() {
	    return `
	        <tr class="total-container">
	            <th colspan="10" class="text-right" >Total Geral (R$)</th>
	            <th colspan="2" class="text-right">${this.totalToPay.toFixed(2)}</th>
	        </tr>`
		};   	

	getBtnBilling() {
	    return `
	        <div class="text-center" style="padding-top: 10px">
	            <button class="btn btn-success" id="btn-faturar">Faturar</button>
	        </div>            
	    `
	}		

	addAmount(instance, key, value){
		if (!instance[key]) {
			instance[key] = parseFloat(value)
		} else {
			instance[key] += parseFloat(value)
		}
	}

	async mountTable(data){		
		// Implementado nas classes que herdam
	}	


	async mountTrTask(task){
		this.htmlTable += getTrTask(task)
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
	        title: 'Carregando Ordens', 
	        html: '<h3>Carregando <strong></strong></h3>',
	        onOpen: ()=> {
	        	swal.showLoading()
	        }
		})		
		const data = await this.search();
		await this.makeReport(data);		
		swal.close()		
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
}

class ReportToPayGroupByOffice extends ReportToPay {
	constructor() {
		super()
		this.currentOffice;
		this.currentClient;
		this.totalByOffice = {};
		this.totalClientByOffice = {};
	}

	getTrOffice(officeId, officeName, clientName, clientRefunds){
	    return `
	        <tr>
	            <th colspan="10">${officeName}</th>
	            <th></th>
	            <th><center><span office-id="${officeId}">|office=${officeId}|</span></center></th>
	        </tr>
	    `
	}

	getTrClient(officeId, clientId, clientName, clientRefunds){
	    return `
	        <tr>
	            <th></th>
	            <th colspan="10">
	                <div class="col-xs-10">
	                    ${clientName}                            
	                </div>
	                <div class="col-xs-2">                    
	                    <!--<span class="badge badge-danger pull-right"><i class="fa fa-check"></i> Reembolsa valor</span>-->                    
	                </div>
	            </th>
	            <th><center><span client-id=${officeId}-${clientId}>|client=${officeId}-${clientId}|<span></center></th>
	        </tr>
	    `
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
			this.htmlTable += this.getTrClient(task.office_id, task.client_id, task.client_name, false)
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
			this.htmlTable = this.htmlTable.replace(`|office=${key}|`, `${this.totalByOffice[key].toFixed(2)}`)			
		})
	}

	async replaceTotalClientByOffice(){
		Object.keys(this.totalClientByOffice).forEach((key)=>{
			this.htmlTable = this.htmlTable.replace(`|client=${key}|`, `${this.totalClientByOffice[key].toFixed(2)}`)			
		})
	}	

	computeTotalOffice(task){
		this.addAmount(this.totalByOffice, task.office_id, task.amount)
	}

	computeTotalOfficeByClient(task){
		this.addAmount(this.totalClientByOffice, `${task.office_id}-${task.client_id}`, task.amount)
	}

	async computeTotals(task){
		this.computeTotalOffice(task)
		this.computeTotalOfficeByClient(task)
		this.computeTotalToPay(task)
	}

	async makeReport(data) {
		while (data.length > 0) {			
		    data.splice(0, 1).forEach((task)=>{	
		    	this.allTaskIds.push(task.task_id);
		    	this.mountTable(task);		    	
		    	this.computeTotals(task);
		    });	
		};
		await this.replaceTotalByOffice();
		await this.replaceTotalClientByOffice();
		await this.writeTable();	
		this.startOnCheckAllItems();
		this.startOnCheckItem();
		this.startOnClickBtnBilling();
	}


}

class ReportToPayGroupByClient extends ReportToPay {

}