from django.contrib import admin
from .models import Attachment


@admin.register(Attachment)
class AdminAttachment(admin.ModelAdmin):
    list_display = ['model_name', 'object_id', 'file']
