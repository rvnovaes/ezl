class ServicePriceTable {
  constructor(typeServiceId) {
    this.typeServiceId = typeServiceId
    this.elModal = $('#modal-service-price-table')
    this.elTypeService = $('#type-service')
        
  }

  get typeServiceName() {
    return this.elTypeService.text()
  }

  set typeServiceName(value) {
    this.elTypeService.text(value)
  }

  showModal() {
    this.elModal.modal('show')
  }

  hideModal() {
    this.elModal.modal('hide')
  }
}