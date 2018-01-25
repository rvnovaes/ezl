function getSearchParams(k){
    var p={};
    location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi,function(s,k,v){p[k]=v})
    return k?p[k]:p;
}

TaskForm = (function($){
    var self;

    function TaskForm(){
        this.$folder = $("#id_folder");
        this.$lawsuit = $("#id_lawsuit");
        this.$movement = $("#id_movement");
    }

    function addOption($el, text, value) {
        value = value | ''; 
        $el.html('<option value="' + value + '">'+ text +'</option>');
    }

    TaskForm.prototype.init = function() {
        var params = getSearchParams();
        self.loadEvents();
        self.task_list = new Vue({
            el: '#app_task_list',
            data: {
                tasks: []
            }
        });
        if(params.movement != undefined) {
            self.loadTasks(params.movement);
        }
        self.fillForm(params);
    };

    TaskForm.prototype.loadEvents = function() {
        self.$folder.change(function(){
            $('#btn_add').addClass('hide');
            var folder = $(this).val();
            if (folder == "" || folder == null){
                addOption(self.$lawsuit, 'Selecione a pasta');
                addOption(self.$movement, 'Selecione o processo');
                return
            }
            addOption(self.$lawsuit, 'Carregando...');
            addOption(self.$movement, 'Selecione o processo');

            $.get("/v1/lawsuit/lawsuit?folder=" + folder, function(data){
                var choices;
                if (data.data.length == 0) {
                    choices = ['<option value="">Sem registros</option>'];
                } else {
                    choices = ['<option value="">Selecione...</option>'];
                }
                $(data.data).each(function(i, item){
                    choices.push('<option value="' + item.id + '">' + item.law_suit_number + ' - ' + item.person_lawyer.name + '</option>');
                });
                self.$lawsuit.html(choices.join(''))
            });

        });

        self.$lawsuit.change(function(){
            $('#btn_add').addClass('hide');
            var lawsuit = $(this).val();
            if (lawsuit == "" || lawsuit == null){
                addOption(self.$movement, 'Selecione o processo');
                return
            }
            addOption(self.$movement, 'Carregando...');

            $.get("/v1/lawsuit/movement?lawsuit=" + lawsuit, function(data){
                var choices;
                if (data.data.length == 0) {
                    choices = ['<option value="">Sem registros</option>'];
                } else {
                    choices = ['<option value="">Selecione...</option>'];
                }
                $(data.data).each(function(i, item){
                    choices.push('<option value="' + item.id + '">' + item.type_movement_name + '</option>');
                });
                self.$movement.html(choices.join(''))
            });

        });

        self.$movement.change(function(){
            var movement = $(this).val();
            self.loadTasks(movement);
            $('#btn_add').removeClass('hide');
        });

    };

    TaskForm.prototype.loadTasks = function(movement){
        self.task_list.$data.tasks = [];
        $.get("/v1/lawsuit/task?movement=" + movement, function(data){
            self.task_list.$data.tasks = data.data;
            setTimeout(addLinkOnRows, 1000);
        });
    };

    TaskForm.prototype.fillForm = function(params){
        if (params.movement != undefined && params.movementLabel != undefined)
            addOption(self.$movement, decodeURI(params.movementLabel), params.movement);
            $('#btn_add').removeClass('hide');
        if (params.lawsuit != undefined && params.lawsuitLabel != undefined)
            addOption(self.$lawsuit, decodeURI(params.lawsuitLabel), params.lawsuit);
        if (params.folder != undefined && params.folderLabel != undefined){
            $('#select2-id_folder-container').append(decodeURI(params.folderLabel));
            $('.select2-selection__placeholder').text('');
            self.$folder.val(params.folder);
        }
    };

    self = new TaskForm();
    return self;
})(jQuery);


$(document).ready(function(){
    TaskForm.init();
});
