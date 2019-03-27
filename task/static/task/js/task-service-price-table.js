class TaskServicePriceTable {
  constructor(taskId, typeServiceId, typeServiceName, billing = null, csrfToken = null) {
    this.csrfToken = csrfToken
    this.billing = billing
    this.taskId = taskId
    this.typeServiceId = typeServiceId
    this.prices = []
    this.priceSelected = {}
    this.elModal = $('#modal-service-price-table')
    this.elTypeService = $('#type-service')
    this.typeServiceName = typeServiceName
    this.idPriceTableElement = '#price-table'
    this.elPriceTable = $(this.idPriceTableElement)
    this.elPriceDefined = $('#price-defined')
    this.elBtnAction = $('#btn-action')
  }

  get typeServiceName() {
    return this.elTypeService.text()
  }

  set typeServiceName(value) {
    this.elTypeService.text(value)
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
    this.elModal.modal('hide')
  }

  showModal() {
    return this.elModal.modal('show')
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

  makeAction() {
    return new Promise((resolve) => {
      if (!this.priceSelected) {
        alert('Não selecionou preço')
      } else {
        $('<input />').attr('type', 'hidden')
          .attr('name', 'action')
          .attr('value', 'OPEN')
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

  initOnBtnAction() {
    return new Promise((resolve) => {
      this.elBtnAction.on('click', () => {        
        this.makeAction()
      })
      resolve(true)
    })
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
      this.priceDefined = this.cheapestPrice.value
      this.elPriceDefined.maskMoney({ 'prefix': 'R$ ', 'decimal': ',', 'thousands': '.', 'allowZero': true })
      // Recurso utilizado para poder setar a mascara no campo 
      // Infelizmente o plugin maskMoney so e setadi a partir do primeiro focus
      // no campo. Assim Se deu a necessidade de fazer este ajuste tecnico. 
      setTimeout(() => this.elPriceDefined.focus, 100)
      setTimeout(() => $(`${this.idPriceTableElement} tbody tr[id=${this.cheapestPrice.id}]`).click(), 200)
      setTimeout(() => $(`#modal-service-price-table-body`).scrollTop(0), 300)
      resolve(true)
    })
  }

  getCheapestPrice() {
    return new Promise(resolve => {
      $.ajax({
        method: 'GET',
        url: `/providencias/${this.taskId}/service_price_table_cheapest_of_task`,
        success: (response => {
          this.cheapestPrice = this.priceSelected = response
          this.setTrCheapstPrice(this.cheapestPrice.id)
          return resolve(true)
        })
      })
    })
  }

  destroyTable() {
    return new Promise(resolve => {
      if ($.fn.DataTable.isDataTable(this.idPriceTableElement)) {
        this.elPriceTable.empty()
      }
      resolve(true)
    })
  }

  initTable() {
    return new Promise((resolve) => {
      this.destroyTable().then(() => {
        resolve(this.elPriceTable = this.elPriceTable.DataTable(
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

  bootstrap() {
    $('#processing').show()
    // Inicializa a tabela com as configuacoes de dataTables
    this.initTable()
      .then(() => {
        // Busca os dados no backend e popula a tabela
        this.populateTable()
          .then(() => {
            //Busca o preco mais barato e define como preco selecionado
            this.getCheapestPrice()
              .then(() => {
                // Seta a linha da tabela que representa o preco mais barato
                // Inicializa o evento de click na linha
                this.initOnClickRowEvent()
                  // Inicializa o evento de click no botao da acao
                  .then(this.initOnBtnAction()
                    .then(() => {
                      this.showModal()
                      this.setTrCheapstPrice()
                        .then(() => {
                        })
                      $('#processing').hide()
                    }))
              })
          })
      })
  }
}

