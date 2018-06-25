var office_groups = [];
$('[data-toggle=tagsinput]').each(function(){
  var office = $(this).attr('office')
  var groups = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('text'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: '/taginput/'+ office +'/permissions'
    });
    groups.initialize();
    var elt = $(this)
    elt.tagsinput({
        itemValue: 'value',
        itemText: 'text',
        typeaheadjs: {
            name: 'groups',
            displayKey: 'text',
            source: groups.ttAdapter()
        }
    });
});
// {% for office in object.person.offices.all %}
//   {% for office_group in office.office_groups.all %}
//       {% for group in object.groups.all %}
//           {% if group == office_group.group %}
//
//           {% endif %}
//       {% endfor %}
//   {% endfor %}
// {% endfor %}
