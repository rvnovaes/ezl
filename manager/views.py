import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import TemplateView
from core.views import CustomLoginRequiredView
from core.utils import get_office_session
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
        status = 400
    return JsonResponse(data, status=status)
