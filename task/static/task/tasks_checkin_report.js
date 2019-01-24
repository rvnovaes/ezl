class CheckinReport {
	constructor() {
		this.form = $("form");
		this.btnFilter = $('#btn-filter');
		this.elTableBody = $('#os-table-body');
		this.elFilterContent = $('#filter_content');
	    this.count = 0;
	    this.htmlTable = ``;
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

	static getDateDiff(fromdate, todate, datepart='n', absolute=true) {
		datepart = datepart.toLowerCase();
  		let diff = todate - fromdate;
  		let divideBy = { w:604800000,
			d:86400000,
			h:3600000,
			n:60000,
			s:1000
  		};
  		return (absolute) ? Math.abs(Math.floor( diff/divideBy[datepart])) : Math.floor( diff/divideBy[datepart]);
	}

	static formatLocalDateTime(strDate) {
		let date = this.setDefaultOfNull(strDate);
		if (date !== '') {
            date = this.getDateFromString(date);
            return `${date.toLocaleString('pt-BR')}`;
        }
        return date;
	}

	static formatTimeDiff(timeList){
		if (timeList[1] >= 60){timeList[1] = timeList[1] % 60}
		if (timeList[2] >= 60){timeList[2] = timeList[2] % 60}
		let i = 0;
		for (i = 0; i < timeList.length; i++) {
		  timeList[i] = (`${timeList[i]}`.length === 1) ? `0${timeList[i]}` : `${timeList[i]}`;
		}
		return timeList
	}

	static isCheckinLate(baseDate, compareDate, diffLimit=30, datePart='n'){
		baseDate = this.setDefaultOfNull(baseDate);
		compareDate = this.setDefaultOfNull(compareDate);
		let isLate = true;
		if(baseDate !== '' && compareDate !== ''){
			baseDate = this.getDateFromString(baseDate);
			compareDate = this.getDateFromString(compareDate);
			if (this.getDateDiff(baseDate, compareDate, datePart) <= diffLimit){
				isLate = false;
			}
		}
		if(compareDate === ''){
			isLate = false;
		}
		return isLate;
	}

	static getCheckinClass(baseCheckin, compareCheckin){
		if(compareCheckin !== '') {
            if (this.isCheckinLate(baseCheckin, compareCheckin)) {
                return 'label label-danger';
            } else if(compareCheckin){
            	return 'label label-success';
			}
        }
		return '';
	}

	static compareCheckins(task){
		let strExecutedByCheckin = this.setDefaultOfNull(task.date_executed_by_checkin);
		let strCompanyRepresentativeCheckin = this.setDefaultOfNull(task.date_company_representative_checkin);
		if(strExecutedByCheckin && strCompanyRepresentativeCheckin){
			let hour = this.getDateDiff(this.getDateFromString(strExecutedByCheckin),
				this.getDateFromString(strCompanyRepresentativeCheckin), 'h');
			let minutes = this.getDateDiff(this.getDateFromString(strExecutedByCheckin),
				this.getDateFromString(strCompanyRepresentativeCheckin));
			let seconds = this.getDateDiff(this.getDateFromString(strExecutedByCheckin),
				this.getDateFromString(strCompanyRepresentativeCheckin), 's');
			let timeList = this.formatTimeDiff([hour, minutes, seconds]);
			return `${timeList[0]}:${timeList[1]}:${timeList[2]}`;
		} else {
			return '--';
		}
	}

	get finishedDate0() {
		return this.elFinishedDate0.val();
	}

	get finishedDate1() {
		return this.elFinishedDate1.val();
	}

	get executionDate0() {
		return this.elExecutionDate0.val();
	}

	get executionDate1() {
		return this.elExecutionDate1.val();
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
			if(this.checkDates()){
				this.start();
			}
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
	          <tr role="row" id="${task.pk}">
	                <td><a href="/dashboard/${task.pk}" target="_blank">${task.task_number}</a></td>
					<td>${task.type_task_name}</td>
					<td>${finalDeadlineDate}</td>
					<td>${CheckinReport.setDefaultOfNull(task.os_executor)}</td>
					<td><span class="font-12 ${CheckinReport.getCheckinClass(task.final_deadline_date, 
																			 task.date_executed_by_checkin)}">
						${dateExecutedByCheckin}</span></td>
					<td>${CheckinReport.setDefaultOfNull(task.task_company_representative)}</td>
					<td><span class="font-12 ${CheckinReport.getCheckinClass(task.final_deadline_date, 
																			 task.date_company_representative_checkin)}">
						${dateCompanyRepresentativeCheckin}</span></td>
					<td><span class="font-12 ${CheckinReport.getCheckinClass(task.date_executed_by_checkin, 
																			 task.date_company_representative_checkin)}">
						${CheckinReport.compareCheckins(task)}</span></td>
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

	openFilters(){
		this.clear();
		this.elFilterContent.collapse('show');
	}

	checkDates(){
		if (!(this.finishedDate0 && this.finishedDate1) && !(this.executionDate0 && this.executionDate1)){
			swal({
				 type: 'error',
				title: "Filtros por data",
				html: '<h3>Favor informar um período de Finalização ou de Cumprimento para filtrar o relatório</h3>'
			});
			return false
		}
		return true
	}
}