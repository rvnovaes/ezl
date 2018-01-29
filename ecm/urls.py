# -*- coding: utf-8 -*-
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ajax-upload(?:/(?P<qquuid>\S+))?', views.UploadView.as_view(), name='ajax-upload'),
    url(r'^ajax-get-attachments', views.ajax_get_attachments, name='ajax-get-attachments'),
    url(r'^ajax-drop-attachment', views.ajax_dsrop_attachment, name='ajax-drop-attachment'),

    url(r'^anexos-padrao/$', views.DefaultAttachmentRuleListView.as_view(), name='defaultattachmentrule_list'),
    url(r'^anexos-padrao/criar/$', views.DefaultAttachmentRuleCreateView.as_view(), name='defaultattachmentrule_add'),
    url(r'^anexos-padrao/(?P<pk>[0-9]+)/$', views.DefaultAttachmentRuleUpdateView.as_view(), name='defaultattachmentrule_update'),
    url(r'^anexos-padrao/excluir$', views.DefaultAttachmentRuleDeleteView.as_view(), name='defaultattachmentrule_delete'),
]
