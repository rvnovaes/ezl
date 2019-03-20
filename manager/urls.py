from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from manager import views


urlpatterns = [
    url(r'^listar/$',
        login_required(views.TemplateValueListView.as_view()),
        name='template_answers_list'),
    url(r'^get_office_template_value/$',
        views.get_office_template_value,
        name='get_office_template_value'),
]
