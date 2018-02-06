var EditableList = (function(){
    var EditableList = {};
    EditableList.init = function(){
        $('[editable-list-btn-edit]').click(function(){
            EditableList.enable();
            $(this).hide();
            $('[editable-list-btn-save]').show();
        });
        $('[editable-list-btn-save]').click(function(){
            $(this).hide();
            EditableList.save(function(data){
                EditableList.disable();
                $('[editable-list-btn-edit]').show();
                showToast('success', 'Dados salvos com sucesso', '', 3000, true);
            }, function(error){
                EditableList.disable();
                $('[editable-list-btn-edit]').show();
                showToast('error', 'Ocorreu um erro. Verifique os dados informados e tente novamente', 'Erro', 3000, true);
            });
        });
    };

    EditableList.enable = function(){
        $('[editable-list] tr').each(function(){
            var tr = $(this);

            removeLinkFromRows();

            tr.find('td[editable-list-enabled]').each(function(){
                var td = $(this),
                    mask = td.attr('input-mask') || "",
                    text = td.text(),
                    input = $('<input type="text" value="' + text +'" editable-list-input mask="' + mask +'"/>');
                    td.html(input),
                    input.attr('default-value', text);

                $(input).change(function(){
                    input.css('color', '#006900');
                    input.css('font-weight', 'bold');
                });
                loadInputsMask();
            });
        });
    };

    EditableList.disable = function(){
        $('[editable-list] tr td[editable-list-enabled]').each(function(){
            var td = $(this),
                input = td.find('input'),
                text = input.val();
            td.html(text);
        });
        addLinkOnRows();
    };

    EditableList.getData = function(){
        data = [];
        $('[editable-list] tr').each(function(){
            var tr = $(this),
                model = tr.attr('editable-list-model'),
                id = tr.attr('editable-list-object');
                item = {
                    model: model,
                    id: id,
                    fields: []
                };
            if (model === undefined)
                return

            data.push(item);
            tr.find('[editable-list-input]').each(function(){
                var input = $(this),
                    value = input.val();
                    td = $(input.parent()),
                    field = td.attr('editable-list-column-name'),
                    mask = td.attr('input-mask') || false;

                if (mask && mask == "money")
                    value = value.replace(".", '').replace(',', '.')
                item.fields.push({
                    field: field,
                    value: value
                });
            });
        });
        return data;
    };

    EditableList.save = function(success, error){
        var data = {"items": JSON.stringify(EditableList.getData())};
        $.ajax({
            url: '/editable-list/save',
            data: data,
            dataType: 'json',
            method: "POST",
            success: success,
            error: error
        });
    };

    return EditableList;
})();

$(document).ready(function(){
    EditableList.init();
});
