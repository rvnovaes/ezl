class TaskDelegateBatch {
  constructor(PriceClass, csrfToken) {
    this.PriceClass = PriceClass
    this.csrfToken = csrfToken
    this.priceInstances = {}
    this.bestPrices = []
    this.taskIds = []
    this.tasksToDelegate = []
    this._elTable = $('#table-batch-change-tasks')
    this.initOnCheckAll()
    this.initOnCheck()
    this.initOnClickChangePrice()
    this.initOnClickDelegate()
  }

  initOnCheckAll() {
    // Seta ou nao todas as tasks a serem delegadas ao clicar em marcar todos
    let self = this
    $('#check-all-tasks').on('change', function () {
      if ($(this).is(':checked')) {
        $('.checkbox-delegate').prop('checked', true)
        $('.checkbox-delegate').each(function () {
          self.tasksToDelegate.push($(this).attr('id'))
        })
      } else {
        $('.checkbox-delegate').prop('checked', false)
        self.tasksToDelegate = [];
      }
    })
  }

  initOnCheck() {
    // Seta task selecionada para ser delegada
    let self = this
    $('.checkbox-delegate').on('change', function () {
      if ($(this).is(':checked')) {
        self.tasksToDelegate.push($(this).attr('id'))
      } else {
        self.tasksToDelegate.splice(self.tasksToDelegate.indexOf($(this).attr('id')), 1)
      }
    })
  }

  getTaskIds() {
    return new Promise(resolve => {
      let taskIds = []
      $(`#table-batch-change-tasks tbody tr`).each(function () {
        taskIds.push($(this).attr('data-id'))
      })
      return resolve(taskIds)
    })
  }

  // Formata preco para padrao Brasileiro, trocar para toLocaleString
  formatPrice(price) {
    return `R$${price.replace(".", ",")}`
  }

  // Atualiza o elemento da tabela
  setElTr(obj, taskId, price) {
    let elTr = obj._elTable.find(`[data-id=${taskId}]`)
    elTr.attr('service-price-id', price.id);
    elTr.find('td [td-correspondent]').text(price.office_correspondent.legal_name);
    elTr.find('td [td-correspondent-value]').text(obj.formatPrice(price.value))
  }

  initOnClickChangePrice() {
    //Funcao de chamada ao clicar no botao trocar
    let self = this
    $('.btn-change-office-correspondent').on('click', function () {
      self.priceInstances[$(this).attr('btn-data-id')].bootstrap()
    });
  }

  delegateTask(taskId, price, notes) {
    return new Promise(resolve => {
      return $.ajax({
        method: 'POST',
        url: `/providencias/${taskId}/batch/delegar`,
        data: {
          task_id: taskId,
          servicepricetable_id: price.id,
          amount: price.value,
          notes: notes
        },        
        success: response => resolve(response),
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", self.csrfToken);
        },
        dataType: 'json'
      })
    })
  }

  async delegateTasks() {
    let total = this.tasksToDelegate.length
    let current = 0
    let delegateInterval;
    swal({
      title: 'Delegando ordens de serviço',
      html: '<h3>Delegando <strong></strong></h3>',
      onOpen: () => {
        swal.showLoading(),
          delegateInterval = setInterval(() => {
            swal.getContent().querySelector('strong')
              .textContent = `${current} de ${total}`
          }, 100)
      },
    })
    let self = this
    let requests = []
    for (let taskId of this.tasksToDelegate) {
      current += 1      
      let bestPrice = await this.PriceClass.getBestPrice(taskId)
      let selectedPrice = this.priceInstances[taskId].priceSelected
      let price = Object.keys(selectedPrice).length ? selectedPrice : bestPrice
      let notes = this.priceInstances[taskId].notes || ''
      this.delegateTask(taskId, price, notes)      
    }
    Promise.all(requests).then(result => {
      console.log(result)
      clearInterval(delegateInterval)
      swal({
        type: 'success',
        title: `${total} ordens de serviço foram delegadas!`,
        onClose: () => {          
          location.reload();
        }
      })      
    })
  }

  initOnClickDelegate() {
    // Acao ao clicar no botao delegar
    self = this
    $('#btn-delegate').on('click', function () {
      if (self.tasksToDelegate.length === 0) {
        swal({
          type: 'error',
          title: 'Você precisa selecionar no mínimo uma Ordem de serviço!'
        })
      } else {
        swal({
          title: 'Tem certeza que deseja delegar?',
          html: "Se você já fez todos os ajustes necessários clique em <br/><strong>Sim, quero delegar!</strong>",
          type: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          cancelButtonText: 'Cancelar',
          confirmButtonText: 'Sim, quero delegar'
        }).then((result) => {
          if (result.value) {
            self.delegateTasks()
          }
        })
      }
    })
  }

  getTypeServiceName(taskId) {    
    return this._elTable.find(`[data-id=${taskId}] td.type_task`).text()   
  }

  async pupulatePriceInstances(PriceClass, taskIds) {
    for (let taskId of taskIds) {
      let typeServiceName = this.getTypeServiceName(taskId)      
      let priceInstance = new PriceClass(taskId, typeServiceName, this, this.callbackChangePrice)
      this.priceInstances[taskId] = priceInstance
      let bestPrice = await PriceClass.getBestPrice(taskId)
      this.setElTr(this, taskId, bestPrice)
    }
  }

  callbackChangePrice(obj, priceInstance) {
    obj.setElTr(obj, priceInstance.taskId, priceInstance.priceSelected)
  }

  async bootstrap() {
    return new Promise(async resolve => {
      let taskIds = await this.getTaskIds()
      this.pupulatePriceInstances(this.PriceClass, taskIds)
      return resolve(true)
    })
  }
}





