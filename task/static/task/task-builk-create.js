function getSearchParams(k){
    var p={};
    location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi,function(s,k,v){p[k]=v})
    return k?p[k]:p;
}

function successPopup(field, value, label){
    TaskForm.successPopup(field, value, label);
}

function isEmpty(value){
    return value == "" || value == null || value == undefined || value == "0";
}

function addOption($el, text, value) {
    value = value | ''; 
    $el.append('<option value="' + value + '">'+ text +'</option>');
}

TaskForm = (function($){
    var self;

    function TaskForm(){
        this.$folder = $("#id_folder");
        this.$lawsuit = $("#id_lawsuit");
        this.$movement = $("#id_movement");
        this.$btn_add_folder = $("#btn_add_folder");
        this.$btn_add_lawsuit = $("#btn_add_lawsuit");
        this.$btn_add_movement = $("#btn_add_movement");
        this.$btn_add = $('#btn_add');
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

    TaskForm.prototype.eventChangeFolder = function(value, callback) {
        self.fieldWasChanged('folder', value);
        if (isEmpty(value)){
            return false;
        }
        $.get("/v1/lawsuit/lawsuit?folder=" + value, function(data){
            var choices;
            if (data.data.length == 0) {
                choices = ['<option value="">Sem registros</option>'];
            } else {
                choices = ['<option value="">Selecione...</option>'];
            }
            $(data.data).each(function(i, item){
                choices.push('<option value="' + item.id + '">' + item.law_suit_number + ' - ' + item.person_lawyer.name + '</option>');
            });
            self.$lawsuit.html(choices.join(''));

            if (typeof(callback) == "function"){
                callback();
            }
            self.$lawsuit.focus();
        });
    };

    TaskForm.prototype.eventChangeLawsuit = function(value, callback) {
        self.fieldWasChanged('lawsuit', value);
        if(value == '' || value == undefined){
            return false;
        }

        $.get("/v1/lawsuit/movement?lawsuit=" + value, function(data){
            var choices = [];
            if (data.data.length > 0) {
                choices = ['<option value="">Selecione...</option>'];
            } else {
                choices = ['<option value="">Sem registros</option>'];
            }
            $(data.data).each(function(i, item){
                choices.push('<option value="' + item.id + '">' + item.type_movement_name + '</option>');
            });
            self.$movement.html(choices.join(''));

            if (typeof(callback) == "function"){
                callback();
            }
            self.$movement.focus();
        });
    };

    TaskForm.prototype.eventChangeMovement = function(value) {
        self.fieldWasChanged('movement', value);
        self.loadTasks(value);
    };

    TaskForm.prototype.loadEvents = function() {
        self.$folder.change(function(){
            var value = $(this).val();
            self.eventChangeFolder(value);
        });

        self.$lawsuit.change(function(){
            var value = $(this).val();
            self.eventChangeLawsuit(value);
        });

        self.$movement.change(function(){
            var value = $(this).val();
            self.eventChangeMovement(value);
        });

        this.$btn_add_folder.click(function(){
            self.openPopup("/processos/pastas/");
        });

        this.$btn_add_lawsuit.click(function(){
            var folder = self.$folder.value || self.$folder.val();
            if (isEmpty(folder)) {
                return
            }
            self.openPopup("/processos/processos/" + folder);
        });

        this.$btn_add_movement.click(function(){
            var lawsuit = self.$lawsuit.val();
            if (isEmpty(lawsuit)) {
                return
            }
            self.openPopup("/processos/movimentacao/" + lawsuit);
        });

        this.$btn_add.click(function(){
            if(self.$btn_add.hasClass('disabled-btn')){
                return false;
            }
            $('#form-content').modal('show');
        });

    };

    TaskForm.prototype.disableAdd = function(field){
        self['$btn_add_' + field].addClass('disabled-btn');
    };

    TaskForm.prototype.enableAdd = function(field){
        self['$btn_add_' + field].removeClass('disabled-btn');
    };

    TaskForm.prototype.clearTaskList = function(){
        self.task_list.$data.tasks = [];
    };

    TaskForm.prototype.removeChoices = function(field){
        var $el = self['$' + field],
            label;
        $el.html('');

        if (field == 'lawsuit') {
            label = 'Selecione a pasta';
            self.removeChoices('movement');
        }
        if (field == 'movement') {
            label = 'Selecione o processo';
        }
        addOption($el, label);
    };

    TaskForm.prototype.fieldWasChanged = function(field, value){
        if (field == "folder") {
            if(isEmpty(value)){
                self.disableAdd('lawsuit');
                self.removeChoices('lawsuit');
            } else {
                self.enableAdd('lawsuit');
            }
            self.disableAdd('movement');
            self.clearTaskList();
        }
        if (field == 'lawsuit'){
            if(isEmpty(value)){
                self.disableAdd('movement');
                self.removeChoices('movement');
            } else {
                self.enableAdd('movement');
            }
            self.clearTaskList();
        }
        this.$btn_add.addClass('disabled-btn');
        if (field == 'movement'){
            if (isEmpty(value)) {
                self.clearTaskList();
            } else {
                this.$btn_add.removeClass('disabled-btn');
                self.loadTasks(value);
            }
        }
    };

    TaskForm.prototype.openPopup = function(url){
        window.open(url +"?popup=1", "", "width=800,height=500");
    };

    TaskForm.prototype.successPopup = function(field, value, label){
        var $el = self["$" + field];
        if ($el.prop('tagName').toLowerCase() == "select"){
            addOption($el, decodeURI(label), value);
        } else {
            $('#select2-id_'+ field +'-container').append(decodeURI(label));
            $('.select2-selection__placeholder').text('');
        }
        $el.val(value);
        $el.value = value;
        self.fieldWasChanged(field, value);
        if (field == 'lawsuit' || field == 'folder') {
            self.$movement.html('');
            addOption(self.$movement, "Sem registros", "");
        }
        if (field == 'folder') {
            self.$lawsuit.html('');
            addOption(self.$lawsuit, "Sem registros", "");
        }
        $("html, body").animate({ scrollTop: 0 }, "slow");
    };

    TaskForm.prototype.loadTasks = function(movement){
        self.task_list.$data.tasks = [];
        $.get("/v1/lawsuit/task?movement=" + movement, function(data){
            self.task_list.$data.tasks = data.data;
            setTimeout(addLinkOnRows, 1000);
        });
    };

    TaskForm.prototype.fillForm = function(params){
        if (params.folder != undefined && params.folderLabel != undefined){
            $('#select2-id_folder-container').append(decodeURI(params.folderLabel));
            $('.select2-selection__placeholder').text('');
            self.$folder.value = params.folder;
            self.enableAdd('lawsuit');
            self.$btn_add_lawsuit.removeClass('disabled-btn');
        }

        self.eventChangeFolder(params.folder, function(){
            self.$lawsuit.val(params.lawsuit);
            self.eventChangeLawsuit(params.lawsuit, function(){
                self.$movement.val(params.movement);
                self.eventChangeMovement(params.movement);
            });
        });
    };

    self = new TaskForm();
    return self;
})(jQuery);


$(document).ready(function(){
    TaskForm.init();
});
