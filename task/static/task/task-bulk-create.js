class TaskBulkCreate {
	constructor() {
		this.elInputPersonCustomer = $('[name=person_customer]');

	}

	get personCustomer() {
	    return this.elInputPersonCustomer.val();
    }

    set personCustomer(data) {
	    if(data.id && data.dataValueTxt) {
            this.elInputPersonCustomer.attr('value', data.id);
            this.elInputPersonCustomer.attr('data-value', data.id);
            this.elInputPersonCustomer.attr('data-value-txt', data.dataValueTxt);
            this.elInputPersonCustomer.val(data.dataValueTxt);
        }
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
                success: function (result) {
                    console.log(result);
                    swal.close();
                    task.personCustomer = result;
                },
                error: function (request, status, error) {
                    swal.close();
                    showToast('error', 'Atenção', result.errors, 0, false);
                },
                beforeSend: function (xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                dataType: 'json'
            });
        }
    };
}
