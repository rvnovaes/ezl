class TaskBulkCreate {
	constructor() {
		this.elInputPersonCustomer = $('[name=person_customer]');
		this.elCourtDistrict = $('[name=court_district]');
		this.elCourtDistrictComplemt = $('[name=court_district_complement]');
		this.elCity = $('[name=city]');
		this.onChangeCity();
		this.onChangeCourtDistrict();

	}

	get personCustomer() {
	    return this.elInputPersonCustomer.val();
    }

    set personCustomer(data) {
	    if(data.id && data.text) {
	        var newOption = new Option(data.text, data.id, true, true);
            this.elInputPersonCustomer.append(newOption).trigger('change');
        }
    }

    get city() {
	    return this.elCity.val();
    }

    get courtDistrict() {
	    return this.elCourtDistrict.val();
    }

    async newPersonCustomer (csrfToken){
        const {value: personCustomerName} = await swal({
          title: 'Cadastro de Cliente/Parte',
          input: 'text',
          width: '30%',
          inputClass: 'form-control',
          inputPlaceholder: 'Nome',
          showCancelButton: true,
          inputValidator: (value) => {
            return new Promise((resolve) => {
              if (!value.trim()) {
                resolve('O nome é obrigatório!');
              } else {
                resolve();
              }

            });
          }
        });

        if (personCustomerName) {
            var data = {'legal_name': personCustomerName,
                     'name': personCustomerName,
                     'legal_type': 'J',
                     'is_customer': true
                };
            $.ajax({
                type: 'POST',
                url: '/person_customer/add/',
                data: data,
                success: (result)=>{
                    this.personCustomer = result;
                },
                error: (request, status, error)=>{
                    showToast('error', 'Atenção', error, 0, false);
                },
                beforeSend: (xhr, settings)=>{
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                dataType: 'json'
            });
        }
    };

	onChangeCity(){
	    this.elCity.on('change',()=>{
            if(this.city) {
                // a função clearTypeaheadField a seguir é definida como uma variável global no arquivo typeahead.js
                clearTypeaheadField(this.elCourtDistrict);
            }
        });
    }

	onChangeCourtDistrict(){
	    this.elCourtDistrict.on('change',()=>{
            if(this.courtDistrict) {
                // a função clearTypeaheadField a seguir é definida como uma variável global no arquivo typeahead.js
                clearTypeaheadField(this.elCity);
            }
        });
    }
}
