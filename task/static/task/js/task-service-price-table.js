class TaskServicePriceTable {
  constructor(taskId, typeServiceId, typeServiceName) {    
    this.taskId = taskId
    this.typeServiceId = typeServiceId    
    this.elModal = $('#modal-service-price-table')
    this.elTypeService = $('#type-service')
    this.typeServiceName = typeServiceName
    this.idPriceTableElement = '#price-table'
    this.elPriceTable = $(this.idPriceTableElement)    
    this.priceTableIdSelected = null
    this.elPriceSelected = $('#price-selected')    
  }
  
  get typeServiceName() {
    return this.elTypeService.text()
  }

  set typeServiceName(value) {
    this.elTypeService.text(value)
  }

  get priceSelected() {
    return this.elPriceSelected.val()
  }

  set priceSelected(value) {
    this.elPriceSelected.val(value)
  }

  hideModal() {
    this.elModal.modal('hide')
  }
  
  showModal() {
    return this.elModal.modal('show')
  }  

  initOnClickRowEvent() {
    return new Promise((resolve)=>{
      let self = this
      $(`${this.idPriceTableElement} tbody`).on('click', 'tr', function(){        
        let row = self.elPriceTable.row(this)                      
        self.priceTableIdSelected = row.node().id
        self.priceSelected = row.data()[8]
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
    this.initTable()
      .then(() => {
        this.populateTable()
          .then(() => {
            this.initOnClickRowEvent().then(this.showModal())
          })          
      })
  }  
}

