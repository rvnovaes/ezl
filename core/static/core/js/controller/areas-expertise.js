class AreasOfExpertise{
    constructor(csrfToken){
        this.csrfToken = csrfToken;
		this._elDivAreasOfExpertise = $('#office-areas-of-expertise');
        AreasOfExpertise.onClickTdArea();
        this.onClickUpdateButton();
    }

    get form() {
		return $('#form-areas-expertise');
	}

	get formData(){
		return this.form.serializeArray();
	}

	get query() {
		let formData = this.formData;
		let data = {};
		$(formData ).each((index, obj) =>{
            data[obj.name] = obj.value;
        });
		return data;
	}

    static onClickTdArea(){
        $('td[id^=area_text_]').on('click', function () {
            let areaID = $(this).data('id');
            let areaCheckbox = $(`#id_area_${areaID}`);
            areaCheckbox.prop('checked', !areaCheckbox.prop('checked'));
        });
    }

    static getHTMLAreasList(areas){
    	let i;
    	let htmlList = '';
		for (i = 0; i < areas.length; i++) {
		  htmlList += `<div class="col col-md-12" style="margin: 3px"><li>${areas[i]}</li></div>`;
		}
		return htmlList;
	}

	updateDivAreasOfExpertise(htmlList){
    	this._elDivAreasOfExpertise.html('');
    	this._elDivAreasOfExpertise.html(htmlList);
	}

    onClickUpdateButton(){
        $('#btn-add-areas').on('click', () => {
            let data = this.query;
            console.log(data)
            swal({
				title: 'Aguarde',
				onOpen: ()=> {
					swal.showLoading();
					$.ajax({
                        method: 'POST',
						url: '/office_profile_areas_of_expertise/',
						data: data,
						success: (response)=> {
                        	let areasHTMLList = AreasOfExpertise.getHTMLAreasList(response.areas);
                        	this.updateDivAreasOfExpertise(areasHTMLList);
							swal.close();
						},
						error: (request, status, error)=> {
                        	let errorList = [];
							Object.keys(request.responseJSON.errors).forEach((key)=>{
								request.responseJSON.errors[key].forEach((e)=>{
									errorList.push(`error: ${e}`);
								});
							});
                        	let htmlList = `<ul class='font-15 text-left'>${Office.createListItens(errorList)}</ul>`;
							let html = `<h4>Ocorreram os seguintes erros ao atualizar as áreas de atuação do `+
                                        `escritório:</h4><br />${htmlList}`;
                        	swal.close();
                        	swal({
								type: 'error',
								title: 'Áreas de atuação',
								html: html,
							});
						},
                        beforeSend: (xhr, settings) => {
                            xhr.setRequestHeader('X-CSRFToken', this.csrfToken);
                        },
					});
				}
			});
        });
    }
}