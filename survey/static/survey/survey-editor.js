SurveyEditor = (function($){

    /**
     * Representação de um objeto do tipo Question.
     * @constructor
     */
    var Question = function(){
        this.type = "text";
        this.name = "";
        this.title = "";
        this.choices = "";
        this.isRequired = true;
        this.visibleIf = "";
    };

    /**
     * Cria uma instância de Question.
     * @param {object} item - Objeto que será utilizado como base para criação.
     */
    Question.create = function(item){

        var instance = new Question(),
            choices_text = "";

        if (item == undefined)
            var item = {};

        if (item.choices != undefined) {
            $(item.choices).each(function(index, choice){
                if(typeof choice == "string") {
                    choices_text += choice + ", ";
                } else {
                    choices_text += choice.text + ", ";
                }
            });
        }

        if (item.title == undefined) {
            item.title = item.name;
        }

        item.choices = choices_text;

        for (key in item) {
            instance[key] = item[key]
        }
        return instance;
    };

    /**
     * Objeto que será exportado para o contexto global que controla todo o comportamento da tela.
     * @constructor
     */
    var Editor = function(){};

    /** Inicializa o formulário de pesquisa. */
    Editor.prototype.init = function(){
        var self = this;
        self.$data_field = $('#id_data');
        self.app = new Vue({
          el: '#app',
          updated: function(){},
          data: {
            questions: [],
            addQuestion: function(){
                self.app.$data.questions.push(Question.create());
            },
            removeQuestion: function(question){
                this.questions.splice(this.questions.indexOf(question), 1);
            }
          }
        });
        self.fillForm();
        $('#object_form').submit(function() {
            self.$data_field.val(self.getData());
            return true;
        });
    };

    /** Preenche o formulário com objetos ja carregados do banco. */
    Editor.prototype.fillForm = function(){
        var self = this,
            input_data = this.$data_field.val(),
            data;

        if (input_data == "")
            return

        data = JSON.parse(input_data);
        $.each(data.pages[0].elements, function(index, item){
            self.app.$data.questions.push(Question.create(item));
        });
    };

    Editor.prototype.getData = function() {
        var questions = JSON.parse(JSON.stringify(this.app.$data.questions)),
            choices,
            choice_text,
            question_choices;

        // Precisamos converter as choices dos campos de formato de texto para uma lista
        $.each(questions, function(index, question){
            question_choices = [];
            if (question.choices != undefined && typeof question.choices == "string") {
                choices = question.choices.split(",");
                $.each(choices, function(index, choice){
                    choice_text = choice.trim();
                    if(choice_text != "") {
                        question_choices.push(choice.trim());
                    }
                });
            }
            question.choices = question_choices;
        });
        var data = {
            pages: [
                {
                    elements: questions
                }
            ]
        };
        return JSON.stringify(data);
    };
    /** Inicializa a renderização de formulário do Materialize. */
    Editor.prototype.initForms = function(){
        $(document)
            .find('select')
            .not('.disabled')
            .not('.material-ignore')
            .material_select();
    };

    /** Desfaz a renderização de formulário do Materialize. */
    Editor.prototype.destroyForms = function() {
        $(document)
            .find('select')
            .not('.disabled')
            .not('.material-ignore')
            .material_select('destroy');
    };
    return new Editor();
})(jQuery);


$(document).ready(function(){
    var $input = $('#id_data'),
        data = $input.val();

    // Colocamos o HTML do formulário logo após o campo de dados da pesquisa (que fica oculto por CSS)
    // $input.parent().append($('[survey-template]').html());
    $($('[survey-template]').html()).insertBefore('.panel-footer');


    SurveyEditor.init();
});