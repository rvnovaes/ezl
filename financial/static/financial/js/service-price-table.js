class ServicePriceTable {
  constructor(taskId, typeServiceId) {
    this.taskId = taskId
    this.typeServiceId = typeServiceId
    this.elModal = $('#modal-service-price-table')
    this.elTypeService = $('#type-service')
    this.elPriceTable = $('#price-table')        
  }

  bootstrap() {
    this.initTable()
      .then(()=>{
        this.populateTable()
          .then(()=>{
            this.showModal()
          })
      })    
  }

  initTable() {
    return new Promise((resolve)=>{
      resolve(this.elPriceTable = this.elPriceTable.DataTable())
    })
  }

  requestPayload() {
    return $.ajax({
      method: 'GET', 
      url: `/financeiro/${this.taskId}/service_price_table_of_task`, 
      success: (response=>{
        return response
      })      
    })
  }

  populateTable() {
    return new Promise((resolve)=> {
      this.requestPayload()
        .then(prices => {
          for (let price of prices) {
            let row = this.elPriceTable.row.add(
              [
                  price.office_correspondent.legal_name,                  
                  price.type_task.name, 
                  price.office_network ? price.office_network.legal_name : '-', 
                  price.state || '-', 
                  price.court_district ? price.court_district.name : '-',
                  price.court_district_complement ? price.court_district_complement.name: '-', 
                  price.city || '-',
                  price.client ? price.client.legal_name : '-', 
                  parseFloat(price.value).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'}), 
                  price.office_rating, 
                  price.office_return_rating
              ]
          ).node();
          row.id = price.id;
          this.elPriceTable.draw(false);
          }
          resolve(true)          
        })
    })
  }

  showModal() {
    return this.elModal.modal('show')
  }

  get typeServiceName() {
    return this.elTypeService.text()
  }

  set typeServiceName(value) {
    this.elTypeService.text(value)
  }

  hideModal() {
    this.elModal.modal('hide')
  }
}