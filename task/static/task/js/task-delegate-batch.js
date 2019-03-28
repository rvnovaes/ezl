class TaskDelegateBatch {
  constructor(PriceClass) {
    this.PriceClass = PriceClass
    this.priceInstances = {}
    this.bestPrices = []
    this.taskIds = []
    this._elTable = $('#table-batch-change-tasks')
    this.initOnCheckAll()
    this.initOnCheck()
    this.initOnClickChangePrice()
    this.initOnClickDelegate()
  }

  initOnCheckAll() {
    // Seta ou nao todas as tasks a serem delegadas ao clicar em marcar todos
    $('#check-all-tasks').on('change', function () {
      if ($(this).is(':checked')) {
        $('.checkbox-delegate').prop('checked', true)
        $('.checkbox-delegate').each(function () {
          tasksToDelegate.push($(this).attr('id'))
        })
      } else {
        $('.checkbox-delegate').prop('checked', false)
        tasksToDelegate = [];
      }
    })
  }

  initOnCheck() {
    // Seta task selecionada para ser delegada
    $('.checkbox-delegate').on('change', function () {
      if ($(this).is(':checked')) {
        tasksToDelegate.push($(this).attr('id'))
      } else {
        tasksToDelegate.splice(tasksToDelegate.indexOf($(this).attr('id')), 1)
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

  populatTaskIds() {
    // Alimenta a lista de ids existentes
    $(`#table-batch-change-tasks tbody tr`).each(function () {
      $('#check-all-tasks').attr('disabled', false);
      this.taskIds.push($(this).attr('data-id'))
    }).promise().done(function () {
      var tasksToGetPrice = true;
      while (tasksToGetPrice) {
        this.setCorrespondents(taskIds.splice(0, 2));
        // tasksToGetPrice = false;
        if (taskIds.length === 0) {
          tasksToGetPrice = false;
        }
      }
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


  // Alimenta todos os melhores precos ao carregar a tela
  async setCorrespondents(taskIds) {
    for (let taskId of taskIds) {
      cheapestPrice = await TaskServicePriceTableBatch.getCheapestPrice(taskId)
      let chosenPrice = {
        taskId: taskId,
        servicePriceTableId: cheapestPrice.id,
        correspondenteName: cheapestPrice.office_correspondent.legal_name, // Nome
        correspondenteValue: cheapestPrice.value,
        note: ''
      };
      setChosenPrice(chosenPrice);
      servicePrices[taskId] = chosenPrice;
      $(`td [btn-data-id=${taskId}]`).attr('disabled', false);
    }
  }

  initOnClickChangePrice() {
    //Funcao de chamada ao clicar no botao trocar
    let self = this
    $('.btn-change-office-correspondent').on('click', function () {
      self.priceInstances[$(this).attr('btn-data-id')].bootstrap()      
    });
  }

  // Funcao de delega todas as Tasks selecionadas
  async sendTasksToDelegate() {
    var current = 0;
    var total = tasksToDelegate.length;
    var delegateTasks = function () {
      tasksToDelegate.forEach(function (taskId) {        
        var chosenPrice = servicePrices[taskId];
        $.ajax({
          method: 'post',
          url: `/providencias/${taskId}/batch/delegar`,
          data: {
            task_id: taskId,
            servicepricetable_id: chosenPrice.servicePriceTableId,
            amount: chosenPrice.correspondenteValue,
            note: chosenPrice.note,
          },
          success: function (response) {
            current += 1            
          },
          error: function (request, status, error) {
          },
          beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", '{{ csrf_token }}');
          },
          dataType: 'json'
        })
      });
      return;
    };

    // Separa em outra funcao
    swal({
      title: 'Delegando ordens de serviço',
      html: '<h3>Delegando <strong></strong></h3>',
      onOpen: () => {
        swal.showLoading(),
          delegateInterval = setInterval(() => {
            swal.getContent().querySelector('strong')
              .textContent = `${current} de ${total}`
            if (current == total) {
              swal({
                type: 'success',
                title: `${total} ordens de serviço foram delegadas!`,
                onClose: () => {
                  tasksToDelegate = [];
                  location.reload();
                }
              })
            }
          }, 0),
          delegateTasks();
      },
      onClose: () => {
        clearInterval(delegateInterval);
      }

    }).then((result) => {
      if (result.dismiss === swal.DismissReason.timer) {
        
      }
    });
  }

  initOnClickDelegate() {
    // Acao ao clicar no botao delegar
    $('#btn-delegate').on('click', function () {
      if (tasksToDelegate.length === 0) {
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
            sendTasksToDelegate();
          }
        })
      }
    })
  }

  async pupulatePriceInstances(PriceClass, taskIds) {
    for (let taskId of taskIds) {                  
      let priceInstance = new PriceClass(taskId, "", this, this.callbackChangePrice)      
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





