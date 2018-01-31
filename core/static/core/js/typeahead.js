$(document).ready(function () {
    $('.twitter-typeahead').each(function (el) {
        console.debug($(this).attr('data-url'));
        var module = $(this).attr('data-module');
        var model = $(this).attr('data-model');
        var field = $(this).attr('name')
        var getTypeaheadData = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
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

        $(this).typeahead(null, {
            name: $(this).attr('id'),
            display: 'value',
            source: getTypeaheadData
        });

    });
});