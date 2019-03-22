import ast
import json
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.views.generic import TemplateView
from core.utils import get_office_session
from core.views import CustomLoginRequiredView
from core.widgets import MDSelect
from .models import TemplateValue


class TemplateValueListView(CustomLoginRequiredView, TemplateView):
    model = TemplateValue
    template_name = 'manager/templatevalue_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.model.__module__
        context['model'] = self.model.__name__
        try:
            context['nav_' + str(self.model._meta.verbose_name)] = True
        except:
            pass
        context['form_name'] = self.model._meta.verbose_name
        context['form_name_plural'] = self.model._meta.verbose_name_plural
        context['page_title'] = self.model._meta.verbose_name_plural
        office = get_office_session(self.request)
        context['office'] = office

        return context

    def post(self, request, *args, **kwargs):
        office = get_office_session(request)
        template_values = office.templatevalue_office.filter(is_active=True).select_related('template')
        if office:
            for template_value in template_values:
                new_value = request.POST.get('template-value-{}'.format(template_value.id), None)
                if new_value != template_value.value.get('value'):
                    value = template_value.value
                    value['value'] = new_value
                    value['office_id'] = office.id
                    value['template_key'] = template_value.template.template_key
                    template_value.value = value
                    template_value.save()
        data = {
            'status': 'Updated'
        }
        return JsonResponse(data, status=200)


@login_required
def get_office_template_value(request):
    data = {}
    if request.method == 'GET':
        office = get_office_session(request)
        qs = office.templatevalue_office.filter(is_active=True).select_related('template')

        data['template_values'] = json.loads(
            json.dumps(
                list(qs.values('template__name', 'template__description', 'template__type', 'template__parameters',
                               'value', 'id')
                     )))
        status = 200
    else:
        status = 405
    return JsonResponse(data, status=status)


@login_required
def get_foreign_key_data(request):
    data = {}
    if request.method == 'GET':
        app_label, model_name = request.GET.get('model', '.').split('.')
        filter_params = ast.literal_eval(request.GET.get('extra_params', {}))
        if not (app_label and model_name):
            status = 400
        else:
            model = apps.get_model(app_label=app_label, model_name=model_name)
            office = get_office_session(request)
            if getattr(model, 'office', None):
                qs = model.objects.get_queryset(office=office)
            elif model_name == 'Person':
                qs = office.persons.all()
            else:
                qs = model.objects.all()
            qs = qs.filter(**filter_params).annotate(text_select=F(request.GET.get('field_list', 'name')))
            list_values = ['id', 'text_select']
            data['values'] = json.loads(
                json.dumps(
                    list(
                        qs.values(*list_values).order_by(list_values[1])
                    )))
            status = 200
    else:
        status = 405
    return JsonResponse(data, status=status)
