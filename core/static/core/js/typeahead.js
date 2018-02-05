$(document).ready(function () {
    $('.twitter-typeahead').each(function (el) {
        console.debug($(this).attr('data-url'));
        var module = $(this).attr('data-module');
        var model = $(this).attr('data-model');
        var field = $(this).attr('name');
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
                    console.debug(data);
                    return data;
                },
                replace: function (url, query) {
                    var params = '?module=' + module + '&model=' + model + '&field=' + field + '&q=' + query;
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
            display: 'value',
            limit: 10,
            source: getTypeaheadData
        }).on('typeahead:selected', function (el, data) {
            $(this).attr('value', data.id);
        });
    });
});