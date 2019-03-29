class TaskServicePriceTable {
  /**
   * Classe generica para a tabela de precos da task
   * @param {string} taskId - ID da task
   * @param {string} typeServiceName - Nome do tipo de servico da task
   * @param {object|null} parentInstance - Instancia de quem instanciou esta classe
   * @param {Function|null} handleCallback - Funcao de calback utilizado no metodo handle
   */

  constructor(taskId, typeServiceName, parentInstance, handleCallback) {
    this.taskId = taskId
    this.notes = notes
    this.parentInstance = parentInstance
    this.handleCallback = handleCallback
    this.bestPrice = {}
    this.prices = []
    this.priceSelected = {}
    this.elModal = $('#modal-service-price-table')
    this.elTypeService = $('#modal-service-price-table-type-service')
    this.typeServiceName = typeServiceName
    this.idPriceTableElement = '#price-table'
    this.elPriceTable = $(this.idPriceTableElement)
    this.elPriceDefined = $('#price-defined')
    this.elBtnAction = $('#btn-action')
  }

  get priceDefined() {
    return this.elPriceDefined.maskMoney('unmasked')[0]
  }

  set priceDefined(value) {
    this.elPriceDefined.val(parseFloat(value).toLocaleString('pt-BR'))
    this.elPriceDefined.focus()
  }

  getPriceObject(priceTableId) {
    return this.prices
      .filter(price => price.id == priceTableId)
      .reduce(item => item)
  }

  hideModal() {
    this.elBtnAction.unbind()
    this.elModal.modal('hide')
  }

  showModal() {
    this.elBtnAction.unbind()
    this.initOnBtnAction()
    return this.elModal.modal('show')
  }

  initOnBtnAction() {
    return new Promise((resolve) => {
      this.elBtnAction.on('click', () => {
        this.handle()
      })
      resolve(true)
    })
  }

  unBindBtnAction() {
    this.elBtnAction.unbind()
  }

  initOnClickRowEvent() {
    return new Promise((resolve) => {
      let self = this
      $(`${this.idPriceTableElement} tbody`).on('click', 'tr', function () {
        let row = self.elPriceTable.row(this)
        self.priceSelected = self.getPriceObject(row.node().id)
        self.priceDefined = self.priceSelected.value
        $(row.node()).siblings().removeClass('row-selected')
        $(row.node()).addClass('row-selected')
        resolve(true)
      })
    })
  }

  requestPayload() {
    return $.ajax({
      method: 'GET',
      url: `/providencias/${this.taskId}/service_price_table_of_task`,
      success: (response => {
        return response
      })
    })
  }

  populateTable() {
    return new Promise((resolve) => {
      this.requestPayload()
        .then(prices => {
          this.prices = prices;
          for (let price of prices) {
            this.elPriceTable.row.add(
              [
                `<a href="/office_profile/${price.office_correspondent.id}" target="_blank" class="price-table-link-to-office">${price.office_correspondent.legal_name}</a>`,
                price.type_task.name,
                price.office_network ? price.office_network : '-',
                price.state || '-',
                price.court_district ? price.court_district.name : '-',
                price.court_district_complement ? price.court_district_complement.name : '-',
                price.city || '-',
                price.client ? price.client.legal_name : '-',
                parseFloat(price.value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }),
                price.office_rating,
                price.office_return_rating
              ]
            ).node().id = price.id;
            this.elPriceTable.draw(false);
          }
          resolve(true)
        })
    })
  }

  setTrCheapstPrice() {
    return new Promise(resolve => {
      this.priceDefined = this.bestPrice.value
      this.elPriceDefined.maskMoney({ 'prefix': 'R$ ', 'decimal': ',', 'thousands': '.', 'allowZero': true })
      // Recurso utilizado para poder setar a mascara no campo 
      // Infelizmente o plugin maskMoney so e setadi a partir do primeiro focus
      // no campo. Assim Se deu a necessidade de fazer este ajuste tecnico. 
      setTimeout(() => this.elPriceDefined.focus, 100)
      setTimeout(() => $(`${this.idPriceTableElement} tbody tr[id=${this.bestPrice.id}]`).click(), 200)
      setTimeout(() => $(`#modal-service-price-table-body`).scrollTop(0), 300)
      resolve(true)
    })
  }

  static getBestPrice(taskId) {
    return new Promise(resolve => {
      $.ajax({
        method: 'GET',
        url: `/providencias/${taskId}/service_price_table_cheapest_of_task`,
        success: (response => {
          response.taskId = taskId
          return resolve(response)
        })
      })
    })
  }

  destroyTable() {
    return new Promise(resolve => {
      if ($.fn.DataTable.isDataTable(this.idPriceTableElement)) {
        try {
          $(this.idPriceTableElement).empty()
        } catch (e) {
          console.error(e)
        }
      }
      resolve(true)
    })
  }

  initTable() {
    return new Promise((resolve) => {
      this.destroyTable().then(() => {
        resolve(this.elPriceTable = $(this.idPriceTableElement).DataTable(
          {
            paging: false,
            order: [[8, 'asc'], [9, 'desc'], [10, 'asc'], [0, 'asc']],
            dom: 'frti',
            buttons: [],
            destroy: true,
            rowID: 'id',
            language: {
              "url": "//cdn.datatables.net/plug-ins/1.10.16/i18n/Portuguese-Brasil.json"
            },
            "fnRowCallback": function (nRow, aData, iDisplayIndex, iDisplayIndexFull) {
              if (aData[1] === '-' || aData[1] === '—') {
                $("td:eq(1)", nRow).text(typeTask);
              }
              return nRow;
            },
          }
        ))
      })
    })
  }

  setTypeServiceName() {
    this.elTypeService.text(this.typeServiceName)
  }

  clearNotes() {
    $('#notes').val('')
  }

  bootstrap() {
    $('#processing').show()
    // Inicializa a tabela com as configuacoes de dataTables
    this.initTable()
      .then(() => {
        // Busca os dados no backend e popula a tabela
        this.populateTable()
          .then(() => {
            //Busca o preco mais barato e define como preco selecionado
            this.constructor.getBestPrice(this.taskId)
              .then((result) => {
                // Seta a linha da tabela que representa o preco mais barato
                this.bestPrice = this.priceSelected = result
                this.setTrCheapstPrice(this.bestPrice.id)
                // Inicializa o evento de click na linha
                this.initOnClickRowEvent()
                  // Inicializa o evento de click no botao da acao
                  .then(this.initOnBtnAction()
                    .then(() => {
                      this.showModal()
                      this.setTrCheapstPrice()
                        .then(() => {
                          this.setTypeServiceName()
                          this.clearNotes()
                        })
                      $('#processing').hide()
                    }))
              })
          })
      })
  }

  handle() {
    console.log(this.taskId)
    if (this.handleCallback) {
      this.priceSelected.value = Number(this.priceDefined).toFixed('2')
      this.handleCallback(this.parentInstance, this)
      this.hideModal()
    }
  }
}

class TaskDetailServicePriceTable extends TaskServicePriceTable {
  /**
   * Classe que herda da TaskServicePriceTable com costumizacoes pra ser utilizada
   * na TaskDetail
   * 
   * @param {string} taskId - ID da task
   * @param {string} typeServiceName - Nome do tipo de servico da task
   * @param {object|null} parentInstance - Instancia de quem instanciou esta classe
   * @param {Function|null} handleCallback - Funcao de calback utilizado no metodo handle
   */
  constructor(taskId, typeServiceName, parentInstance, handleCallback) {
    super(taskId, typeServiceName, parentInstance, handleCallback)
    this.billing = parentInstance.billing
    this.csrfToken = parentInstance.csrfToken
  }

  setBillingItem() {
    this.billing.item =
      {
        task_id: this.taskId,
        service_price_table_id: this.priceSelected.id,
        name: ' Para ' + this.officeToDelegateName,
        value: Number(this.priceDefined).toFixed(2).replace('.', '')
      };
  }

  handle() {
    return new Promise((resolve) => {
      if (!this.priceSelected) {
        alert('Não selecionou preço')
      } else {
        $('<input />').attr('type', 'hidden')
          .attr('name', 'action')
          .attr('value', 'OPEN')
          .appendTo('#task_detail');
        $('<input />').attr('type', 'hidden')
          .attr('name', 'notes')
          .attr('value', $('#notes').val() + " ")
          .appendTo('#task_detail');          
        $('[name=servicepricetable_id]').val(this.priceSelected.id)
        $('[name=amount]').val(this.priceDefined.toLocaleString('pt-BR'))
        if (this.priceSelected.policy_price.billing_moment === 'PRE_PAID') {
          this.hideModal();
          this.setBillingItem()
          this.billing.createCharge(this.csrfToken)
        } else {
          swal({
            title: 'Delegando',
            html: '<h4>Aguarde...</h4>',
            onOpen: () => {
              swal.showLoading();
              $('input[name=amount]').removeAttr('disabled');
              $('#task_detail').unbind('submit').submit();
            }
          });

        }
      }
      resolve(true)
    })
  }
}


class TaskServicePriceTableBatch extends TaskServicePriceTable {
  /**
   * Classe que herda da TaskServicePriceTable com costumizacoes pra ser utilizada
   * na TaskDetail
   * 
   * @param {string} taskId - ID da task
   * @param {string} typeServiceName - Nome do tipo de servico da task
   * @param {object|null} parentInstance - Instancia de quem instanciou esta classe
   * @param {Function|null} handleCallback - Funcao de calback utilizado no metodo handle
   */

  requestPayload() {
    return $.ajax({
      method: 'GET',
      url: `/providencias/${this.taskId}/service_price_table_of_task`,
      data: {
        billing_moment: 'POST_PAID'
      },
      success: (response => {
        return response
      })
    })
  }

  static getBestPrice(taskId) {
    return new Promise(resolve => {
      $.ajax({
        method: 'GET',
        url: `/providencias/${taskId}/service_price_table_cheapest_of_task`,
        data: {
          billing_moment: 'POST_PAID'
        },        
        success: (response => {
          response.taskId = taskId
          return resolve(response)
        })
      })
    })
  }  

  handle() {
    this.notes = $('#notes').val()
    super.handle()
  }
}