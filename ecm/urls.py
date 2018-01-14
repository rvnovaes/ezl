# -*- coding: utf-8 -*-
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ajax-upload(?:/(?P<qquuid>\S+))?', views.UploadView.as_view(), name='ajax-upload'),
    url(r'^ajax-get-attachments', views.ajax_get_attachments, name='ajax-get-attachments'),
    url(r'^ajax-drop-attachment', views.ajax_dsrop_attachment, name='ajax-drop-attachment'),
]