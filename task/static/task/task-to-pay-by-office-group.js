
// Aproveita em qualquer forma de agrupamento
var getBtnBilling = function() {
    return `
        <div class="text-center" style="padding-top: 10px">
            <button class="btn btn-success" id="btn-faturar">Faturar</button>
        </div>            
    `
}

var getTrfoot = function(total) {
    return `
        <tr class="total-container">
            <th colspan="10" class="text-right" >Total Geral (R$)</th>
            <th colspan="2" class="text-right">${total}</th>
        </tr>`
};   

var getBillingDate = function(billingData) {
    if (!billingData) {
        return ''
    }
    return billingData
}

var setDefaultOfNull = function(value){
    if (!value) {
        return ''
    }
}

var formatLocalDateTime = function(strDate) {
    let date = new Date(strDate);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
}

var getTrTask = function(task) {    
    let elBilling = '';
    if (task.task_id === '22929') {
        console.log(task)
    }
    if (!task.billing_date) {
        elBilling = `<input type="checkbox" value="${task.task_id}"/>`;
    } 
    return `
          <tr role="row" id="${task.task_id}">
                <td></td>
                <td></td>
                <td>
                    ${elBilling}
                </td>
                <td>
                    <a href="" target="_new">
                        ${task.parent_task_number}
                    </a>
                </td>
                <td>${formatLocalDateTime(task.finished_date)}</td>
                <td>${task.type_task}</td>
                <td>${task.lawsuit_number}</td>
                <td>${task.court_district}</td>
                <td>${task.opposing_party}</td>
                <td>${setDefaultOfNull(task.task_legacy_code)}</td>
                <td>${getBillingDate(task.billing_date)}</td>
                <td class="text-center"><center>${task.amount}</center></td>
            </tr>            `
}

// Aproveita no agrupamento por office
var getTrOffice = function(officeName, officeId) {
    return `
        <tr>
            <th colspan="10">${officeName}</th>
            <th></th>
            <th><center><span office-id="${officeId}">|office=${officeId}|</span></center></th>
        </tr>
    `            
}

var getTrClient = function(clientName, clientRefunds, officeId, clientId){
    return `
        <tr>
            <th></th>
            <th colspan="10">
                <div class="col-xs-10">
                    ${clientName}                            
                </div>
                <div class="col-xs-2">                    
                    <!--<span class="badge badge-danger pull-right"><i class="fa fa-check"></i> Reembolsa valor</span>-->                    
                </div>
            </th>
            <th><center><span client-id=${officeId}-${clientId}>|client=${officeId}-${clientId}|<span></center></th>
        </tr>
    `
}
        

var totalToPay = 0.0;
var currentOffice;
var currentClient;
var totalOffice = 0.0;
var totalClient = 0.0;
var totalOffices = {};
var totalClientsByOffice = {};
var count = 0;
var total = 0;
var isLoaging = false;
var elTableBody = ``;

var writeTable = function() {
    swal({
        title: 'Montando tabela', 
        html: '<h3>Aguarde</h3>', 
        onOpen: () => {
            swal.showLoading()
            setTimeout(function() {
                $('#os-table-body').append(elTableBody);
                $('#os-table-foot').append(getTrfoot(totalToPay.toFixed(2)));
                $('#btn-billing').append(getBtnBilling);
                activeOnClickBtnFaturar();
                swal.close();
            }, 500)
        }
    })                                    
};

var mountTableClientByOffice = function(){
    swal({
        title: 'Totalizando Clientes', 
        html: '<h3>Aguarde</h3>', 
        onOpen: () => {
            swal.showLoading()
            setTimeout(function() {
                Object.keys(totalClientsByOffice).forEach(function(key) {
                    elTableBody = elTableBody.replace(`|client=${key}|`, `${totalClientsByOffice[key].toFixed(2)}`)
                }, 500)                        
                writeTable()                        
            })
        }
    })            
}

var mountTotalOffices = function() {
    swal({
        title: 'Totalizando Escritórios', 
        html: '<h3>Aguarde</h3>', 
        onOpen: () => {
            swal.showLoading()
            setTimeout(function() {
                Object.keys(totalOffices).forEach(function(key){
                    elTableBody = elTableBody.replace(`|office=${key}|`, `${totalOffices[key].toFixed(2)}`)
                })
                mountTableClientByOffice();
            }, 500)
        }
    });                                     
};

var mountTable = function(data) {                        
    swal({
        title: 'Carregando Ordens', 
        html: '<h3>Carregando <strong></strong></h3>',
        onOpen: () => {
            swal.showLoading() 
            total = data.length;  
            setTableInterval = setInterval(function() {                        
                if (data.length < 1) {
                    clearInterval(setTableInterval)                            
                    setTimeout(function(){                                
                        mountTotalOffices()                                                                                        
                    }, 500)                            
                }                        
                data.splice(0, 1).forEach(function(task){                                                                       
                    swal.getContent().querySelector('strong')
                        .textContent = `${count} de ${total}`;                                                             
                    if (currentOffice !== task.office_name) {                     
                        currentOffice = task.office_name; 
                        currentClient = null;
                        elTableBody += getTrOffice(task.office_name, task.office_id);
                        totalOffice = 0.0;      
                        totalClient = 0.0; 
                    };
                    if(currentClient !== task.client_name){
                        currentClient = task.client_name;
                        elTableBody += getTrClient(task.client_name, false, task.office_id, task.client_id);
                        totalClient = 0.0;
                    }        
                    count += 1;   
                    totalToPay += parseFloat(task.amount);
                    totalOffice += parseFloat(task.amount);
                    totalClient += parseFloat(task.amount);  
                    totalOffices[task.office_id] = totalOffice;
                    totalClientsByOffice[task.office_id + '-' + task.client_id] = totalClient;

                    elTableBody += getTrTask(task);
                    allTaskIds.push(task.task_id);
                });
            }, 0)
         }
    })             
};

function getTasks () {
    $('#os-table-body').empty();
    $('#os-table-foot').empty();
    $('#btn-billing').empty();                
    count = 0;
    totalToPay=0;
    currentOffice = null;
    currentClient = null;	
    tasksToPay = [];
    allTaskIds = [] ;  
    elTableBody = ``;
    var formdata = $("form").serializeArray();
    var data = {};
    $(formdata ).each(function(index, obj){
        data[obj.name] = obj.value;
    });                        
    $.ajax({
        method: 'GET', 
        url: `/relatorios/os-a-pagar-data`, 
        data: data, 
        success: function(response) {
            let responseData = JSON.parse(response) ;                                                    
            mountTable(responseData);
        },                
        error: function(error) {
          console.log('DEU ERRADO');
          console.log(error)
        },
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", '{{ csrf_token }}');
        },
        dataType: 'json'                 
    }); 

};