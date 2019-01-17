class CheckinReport {
	constructor() {
		this.form = $("form");
		this.btnDownloadXlsx = $('#btn-download-xlsx');
		this.btnFilter = $('#btn-filter');
		this.elTableBody = $('#os-table-body');
		this.elTableFoot = $('#os-table-foot');
	    this.count = 0;
	    this.htmlTable = ``;
	    this.elTaskExecutedBy = $('#id_task_executed_by');
	    this.elTaskCompanyRepresentative = $('#id_task_company_representative');
	    this.elFinishedDate0 = $("#finished_date_0");
	    this.elFinishedDate1 = $("#finished_date_1");
	    this.elExecutionDate0 = $("#execution_date_0");
	    this.elExecutionDate1 = $("#execution_date_1");
		this.onClickBtnFilter();
	}

	static setDefaultOfNull(value){
	    if (!value) {
	        return '';
	    }
	    return value;
	}

	static getDateFromString(strDate){
		return new Date(strDate);
	}

	static formatLocalDateTime(strDate) {
		let date = CheckinReport.setDefaultOfNull(strDate);
		if (date !== '') {
            date = CheckinReport.getDateFromString(date);
            return `${date.toLocaleString('pt-BR')}`;
        }
        return date;
	}

	static isCheckinLate(strTaskDate, strCheckinDate){
		let taskDate = CheckinReport.setDefaultOfNull(strTaskDate);
		let checkinDate = CheckinReport.setDefaultOfNull(strCheckinDate);
		let isLate = true;
		if(taskDate !== '' && checkinDate !== ''){
			taskDate = CheckinReport.getDateFromString(taskDate);
			checkinDate = CheckinReport.getDateFromString(checkinDate);
			if (Math.abs(Math.floor((taskDate - checkinDate)/60000)) <= 30){
				isLate = false;
			}
		}
		if(checkinDate === ''){
			isLate = false;
		}
		return isLate;
	}

	static getCheckinClass(task, field=''){
		if(field !== '') {
            if (CheckinReport.isCheckinLate(task.final_deadline_date, task[field])) {
                return 'label-danger';
            } else if(task[field]){
            	return 'label-success';
			}
        }
		return '';
	}

	get formData() {
		return this.form.serializeArray();
	}

	get query() {
		let formData = this.formData;
		let data = {};
		$(formData ).each(function(index, obj){
			data[obj.name] = obj.value;
		});
		return data;
	}

	onClickBtnFilter() {
		this.btnFilter.on('click', () => {
			this.start();
		});
	}

	async search() {
		const response = await this.getData().then((data)=>{
			this.data = data;
			return data;
		});
		return response;
	}

	async getData() {
		const response = await $.ajax({
	        method: 'GET', 
	        url: window.location.href,
	        data: this.query, 
	        dataType: 'json', 	        
		});
		return response;
	}

	getTrTask(task) {
		let finalDeadlineDate = CheckinReport.formatLocalDateTime(task.final_deadline_date);
		let dateExecutedByCheckin = CheckinReport.formatLocalDateTime(task.date_executed_by_checkin);
        let dateCompanyRepresentativeCheckin = CheckinReport.formatLocalDateTime(task.date_company_representative_checkin);
	    return `
	          <tr role="row" id="${task.task_id}">
	                <td>${task.task_number}</td>
					<td>${task.type_task_name}</td>
					<td>${finalDeadlineDate}</td>
					<td>${CheckinReport.setDefaultOfNull(task.os_executor)}</td>
					<td><span class="font-12 label ${CheckinReport.getCheckinClass(task, 'date_executed_by_checkin')}">
						${dateExecutedByCheckin}</span></td>
					<td>${CheckinReport.setDefaultOfNull(task.task_company_representative)}</td>
					<td><span class="font-12 label ${CheckinReport.getCheckinClass(task, 'date_company_representative_checkin')}">
						${dateCompanyRepresentativeCheckin}</span></td>
					<td>Diferença entre marcações</td>
					<td>${CheckinReport.setDefaultOfNull(task.person_customer)}</td>
					<td>${CheckinReport.setDefaultOfNull(task.law_suit_number)}</td>
	            </tr>`;
	}


	async mountTable(data){		
		this.mountTrTask(data);
	}	


	async mountTrTask(task){
		this.htmlTable += this.getTrTask(task);
	}

	writeTable(){
		this.elTableBody.append(this.htmlTable);
	}

	async start(){
		this.clear();
		swal({
	        title: "Carregando OS's",
	        html: '<h3>Aguarde...</h3>',
	        onOpen: ()=> {
	        	swal.showLoading()
	        }
		});
		const data = await this.search();
		await this.makeReport(data);
		swal.close();
	}

	clear() {
		this.elTableBody.empty();
	    this.htmlTable = ``;		
	}

	async makeReport(data) {
		while (data.length > 0) {
		    data.splice(0, 1).forEach((task)=>{
		    	this.mountTable(task);
		    });
		}
		this.writeTable();
	}
}