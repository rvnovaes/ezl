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
        }).on('typeahead:selected', function (el, data) {
            $(this).attr('value', data.id);
            $(this).attr('data-value', data.id);
            $(this).attr('data-value-txt', data['data-value-txt']);
        }).on('typeahead:autocomplete', function (el, data) {
            $(this).attr('value', data.id);
            $(this).attr('data-value', data.id);
            $(this).attr('data-value-txt', data['data-value-txt']);
        }).on('typeahead:close', function (el) {
            if (!$(this).val()){
                $(this).attr('value', '');
                $(this).attr('data-value', '');
                $(this).attr('data-value-txt', '');
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
});