import ast
import json
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.views.generic import TemplateView
from core.utils import get_office_session, update_office_custom_settings
from core.views import CustomLoginRequiredView
from .models import TemplateValue
from .utils import get_model_by_str, get_filter_params_by_str, update_template_value
from .template_values import ListTemplateValues


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
        manager = ListTemplateValues(office)
        template_values = manager.instance_values
        if office:
            for template_value in template_values:
                new_value = request.POST.get('template-value-{}'.format(template_value.id), None)
                if new_value != template_value.value.get('value'):
                    update_template_value(template_value, new_value)
        update_office_custom_settings(office)
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
        model_str = request.GET.get('model', '')
        if not model_str or '.' not in model_str:
            status = 400
        else:
            model = get_model_by_str(model_str)
            filter_params = get_filter_params_by_str(request.GET.get('extra_params', '{}'))

            office = get_office_session(request)
            if getattr(model, 'office', None) and model_str != 'auth.User':
                qs = model.objects.get_queryset(office=office)
            elif model._meta.object_name == 'Person':
                qs = office.persons.all()
            elif model._meta.object_name == 'User':
                qs = model.objects.filter(person__in=office.persons.all(),
                                          is_superuser=False)
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
