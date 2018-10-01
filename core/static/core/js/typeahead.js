var typeaheadAditionalParams;
$(document).ready(function () {
    typeaheadAditionalParams = {};
    $('.twitter-typeahead').each(function (el) {        
        var module = $(this).attr('data-module');
        var model = $(this).attr('data-model');
        var field = $(this).attr('name');
        var forward = $(this).attr('data-forward');
        var forwardValue = '';
        if ($(this).attr('search-field')){
            field = $(this).attr('search-field');
        }
        var getTypeaheadData = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('id'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: {
                url: $(this).attr('data-url'),
                wildcard: '%QUERY',
                filter: function (data) {                    
                    return data;
                },
                replace: function (url, query) {
                    if (forward && forward !== 'None'){
                        forwardValue = $("[name=" + forward + "]").val();
                        if (forwardValue == ''){
                            forwardValue = 0;
                        }
                    }                    
                    var form = $('form')
                    var params = '?module=' + module + '&model=' + model + '&field=' + field + '&forward=' + forward + '&forwardValue=' + forwardValue + '&q=' + query + '&extra_params=' + JSON.stringify(typeaheadAditionalParams);
                    return url + params;
                }
            }
        });

        $(this).typeahead({
            hint: true,
            highlight: true,
            minLength: 1,
        }, {
            name: $(this).attr('id'),
            value: 'id',
            display: 'data-value-txt',
            limit: 15,
            source: getTypeaheadData
        }).on('typeahead:asyncrequest', function() {
            $(this).addClass('loading');
        }).on('typeahead:asynccancel typeahead:asyncreceive', function() {
            $(this).removeClass('loading');
        }).on('typeahead:selected', function (el, data) {
            $(this).attr('value', data.id);
            $(this).attr('data-value', data.id);
            $(this).attr('data-value-txt', data['data-value-txt']);
            $(this).attr('data-forward-id', data['data-forward-id']);
            $(this).attr('data-extra-params', data['data-extra-params']);
        }).on('typeahead:autocomplete', function (el, data) {
            $(this).attr('value', data.id);
            $(this).attr('data-value', data.id);
            $(this).attr('data-value-txt', data['data-value-txt']);
            $(this).attr('data-forward-id', data['data-forward-id']);
            $(this).attr('data-extra-params', data['data-extra-params']);
        }).on('typeahead:close', function (el) {
            if (!$(this).val()){
                $(this).attr('value', '');
                $(this).attr('data-value', '');
                $(this).attr('data-value-txt', '');
                $(this).attr('data-forward-id', '');
                $(this).attr('data-extra-params', '');
            }
        });
    });

    $("form").submit(function( event ) {
      $("[data-typeahead=true]").each(function () {
          if($(this).val() && $(this).attr('data-value')){
              $(this).val($(this).attr('data-value'))
          }else{
              $(this).typeahead('val','');
          }
      });
    });
    $("[data-typeahead=true]").each(function () {
        if ($(this).attr('data-value-txt') !== 'None') {
            $(this).val($(this).attr('data-value-txt'))
        }
    });

    // funcao responsavel por limpar um campo typeahead
    var clearTypeaheadField = function(field){
        field.attr('value', '');
        field.attr('data-value', '');
        field.attr('data-value-txt', '');
        field.attr('data-forward-id', '');
        field.attr('data-extra-params', '');
        field.typeahead('val', '');
    };

    // tenta localizar o campo de complemento
    var complement = $('[name=court_district_complement]');

    // limpa o campo de complemento de acordo com a comarca selecionada, caso exista o campo de comarca e complemento
    var courtDistrict = $('[name=court_district]');
    if (courtDistrict.length > 0 && complement.length > 0) {
        var courtDistrictSelect = courtDistrict.attr('data-value');
        courtDistrict.on('change', function () {
            if (courtDistrict.attr('data-value') !== courtDistrictSelect && courtDistrict.attr('data-value') !== complement.attr('data-forward-id')) {
                clearTypeaheadField(complement);
                courtDistrictSelect = courtDistrict.attr('data-value');
            }
        });
    }

    // limpa o campo de complemento de acordo com a uf selecionada, caso exista o campo de uf e complemento
    var stateField = $('#id_state');
    if (stateField.length > 0 && complement.length > 0) {
        typeaheadAditionalParams.state = stateField.val();
        stateField.on('change', function(){
            typeaheadAditionalParams.state = $(this).val();
            if(complement.attr('data-extra-params') !== $(this).val()){
                clearTypeaheadField(complement);
            }
        });
    }

    if (stateField.length > 0 && courtDistrict.length > 0) {
        var stateSelect = stateField.prop('selectedIndex');
        stateField.on('change', function () {
            if (stateSelect !== stateField.prop('selectedIndex') && stateField.val() !== courtDistrict.attr('data-forward-id')) {
                clearTypeaheadField(courtDistrict);
                stateSelect = $('#id_state').prop('selectedIndex');
            }
        });
    }
});