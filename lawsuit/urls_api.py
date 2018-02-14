from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views_api as views


urlpatterns = [
    url(r'lawsuit$', login_required(views.LawsuitApiView.as_view()),
        name='lawsuit_api'),
    url(r'movement$', login_required(views.MovementApiView.as_view()),
        name='movement_api'),
    url(r'task$', login_required(views.TaskApiView.as_view()),
        name='task_api'),
]
