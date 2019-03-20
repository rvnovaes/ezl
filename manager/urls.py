from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from manager import views


urlpatterns = [
    url(r'^listar/$',
        login_required(views.TemplateAnswersListView.as_view()),
        name='template_answers_list'),
]
