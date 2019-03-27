class TaskServicePriceTable {
  constructor(taskId, typeServiceId, typeServiceName) {
    this.taskId = taskId
    this.typeServiceId = typeServiceId
    this.prices = []
    this.priceSelected = {}
    this.elModal = $('#modal-service-price-table')
    this.elTypeService = $('#type-service')
    this.typeServiceName = typeServiceName
    this.idPriceTableElement = '#price-table'
    this.elPriceTable = $(this.idPriceTableElement)
    this.elPriceSelected = $('#price-selected')
    this.elBtnAction = $('#btn-action')
  }

  get typeServiceName() {
    return this.elTypeService.text()
  }

  set typeServiceName(value) {
    this.elTypeService.text(value)
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
        if (this.priceSelected.policy_price.billing_moment === 'PRE_PAID') {
          this.hideModalAction();
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
                price.office_correspondent.legal_name,
                price.type_task.name,
                price.office_network ? price.office_network.legal_name : '-',
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

  initTable() {
    return new Promise((resolve) => {
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
  }

  bootstrap() {
    $('#processing').show()
    this.initTable()
      .then(() => {
        this.populateTable()
          .then(() => {
            this.initOnClickRowEvent()
              .then(this.initOnBtnAction().then(() => {
                this.showModal()
                $('#processing').hide()
              }))
          })
      })
  }
}

