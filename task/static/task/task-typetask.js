$(document).ready(function() {
  var table;
  var previusSelected = null;

  var addOptionPlus = function(option) {
    var selectEl = document.getElementById('id_type_task');
    if (selectEl.length > 1) {
      selectEl.remove(selectEl.length - 1);
    }
    if (option) {
      selectEl.add(option);
    }
    plusOption = new Option("Selecionar serviço EZLog...", 'plus');
    selectEl.add(plusOption);
  }


  var addToSession = function(id, text) {
    sessionStorage.setItem('type_task', JSON.stringify({
      id: id,
      text: text
    }))
  };

  $("#modal-type-task").on('show.bs.modal', function(event) {
    if (!table) {
      table = $('#table-type-task').DataTable({
        pageLength: 10,
        language: {
          "url": "//cdn.datatables.net/plug-ins/1.10.16/i18n/Portuguese-Brasil.json"
        },
      })
      table = $('#table-type-task tbody').on('click', 'tr', function() {
        var typeTaskId = $(this).attr('id');
        var typeTaskName = $(this).attr('data-label')
        var optionExist = [];
        optionExist = $('#id_type_task option').filter(function(el) {
          if ($(this).val() == typeTaskId) {
            return el
          }
        })
        if (!optionExist.length) {
          var opt = new Option(typeTaskName, typeTaskId)
          addOptionPlus(opt)
        }
        $('#id_type_task').val(typeTaskId)
        previusSelected = typeTaskId
        $("#modal-type-task").modal('hide')
      })
    }
  })

  // Mostra apenas listagem simples
  typeTaskList.forEach(function(typeTask) {
    if (typeTask.simple_service === 'True') {
      var opt = new Option(typeTask.name, typeTask.pk)
      addOptionPlus(opt);
    } else if (typeTask.pk === selectedItem) {
      var opt = new Option(typeTask.name, typeTask.pk)
      addOptionPlus(opt);
    }
    if (typeTask.pk === selectedItem) {
      $('#id_type_task').val(typeTask.pk)
    }
  })
  addOptionPlus();
  $('#id_type_task').change(function() {
    if ($(this).val() == 'plus') {
      if (!previusSelected) {
        $(this).val(null)
      } else {
        $(this).val(previusSelected)
      }
      $("#modal-type-task").modal('show')
    } else {
      previusSelected = $(this).val()
    }
  })
})
