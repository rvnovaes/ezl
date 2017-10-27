from functools import wraps

import django.db.models.fields
import django.forms.models

from ezl.celery import app as celery_app


__all__ = ['celery_app']


django.db.models.fields.BLANK_CHOICE_DASH = [('', 'Selecione')]


def modelchoicefield_init(func):

    @wraps(func)
    def decorated(self, *args, **kwargs):
        func(self, *args, **kwargs)
        if self.empty_label == '---------':
            self.empty_label = 'Selecione'

    return decorated


django.forms.models.ModelChoiceField.__init__ = \
    modelchoicefield_init(django.forms.models.ModelChoiceField.__init__)
