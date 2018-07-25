var getColumns = function(status) {

    var columnDefs = [];
    var columns = [
        {'data': 'pk', 'name': 'pk'},
        {'data': 'task_number', 'name': 'task_number'},
        {'data': 'final_deadline_date', 'name': 'final_deadline_date'},
        {'data': 'type_task__name', 'name': 'type_task__name'},
        {'data': 'movement__law_suit__law_suit_number', 'name': 'movement__law_suit__law_suit_number'},
        {'data': 'movement__law_suit__court_district__name', 'name': 'movement__law_suit__court_district__name'},
        {'data': 'movement__law_suit__court_district__state__initials', 'name': 'movement__law_suit__court_district__state__initials'},
        {'data': 'movement__law_suit__folder__person_customer__legal_name', 'name': 'movement__law_suit__folder__person_customer__legal_name'},
        {'data': 'movement__law_suit__opposing_party', 'name': 'movement__law_suit__opposing_party'},
        {'data': 'delegation_date', 'name': 'delegation_date'},
        {'data': 'task_original', 'name': 'task_original'},
        {'data': 'task_original', 'name': 'task_original'},
        {'data': 'task_original', 'name': 'task_original'},
    ];
    if (status === 'Erro no sistema de origem') {
        columnDefs = [{ 'targets': [ 0 ], 'visible': false, 'searchable': false, 'orderable': false  }];
        columns[11] = {'data': 'inconsistencyetl__inconsistency', 'name': 'inconsistencyetl__inconsistency'};
        columns[12] = {'data': 'inconsistencyetl__solution', 'name': 'inconsistencyetl__solution'};
    } else {
        columnDefs = [
            { 'targets': [ 0 ], 'visible': false, 'searchable': false, 'orderable': false  },
            { 'targets': [ 11 ], 'visible': false, 'searchable': false, 'orderable': false  },
            { 'targets': [ 12 ], 'visible': false, 'searchable': false, 'orderable': false  },
            { 'targets': [ 2, 9 ],
                render: function ( data, type, row, meta ) {
                    if(type === 'display'){
                        data = moment(data).format('DD/MM/YYYY HH:mm');
                    }

                    return data;
                }
            }
        ];
    }
    return {
        columnDefs: columnDefs,
        columns: columns
    };
};