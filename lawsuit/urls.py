from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^type_movements/$', name='type_movements'),
    url(r'^type_movement/$', name='type_movement'),

]