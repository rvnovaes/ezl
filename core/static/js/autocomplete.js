$("input[data-provide='typeahead']").each(function () {
    var element = $(this);
    $(this).typeahead({
        ajax: {
            url: "/generic_autocomplete_foreignkey",
            items: [100],
            element: element,
            preDispatch: function (query) {
                return {
                    q: query,
                    name: $(this.element).attr('name'),
                    model: $(this.element).attr('model'),
                    module: $(this.element).attr('module')
                }
            },
            preProcess: function (data) {
                data.results.forEach(function (d) {
                    d.name = d.text;
                    console.log(d)
                });
                console.log(data.results);
                return data.results
            }
        }
    })
});