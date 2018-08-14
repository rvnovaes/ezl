from django import forms 
from .models import Dashboard, Card
from codemirror import CodeMirrorTextarea


class DashboardForm(forms.ModelForm):
	class Meta:
		model = Dashboard
		fields = '__all__'

code_mirror = CodeMirrorTextarea(
			mode="python",
			theme="material", 
			config={
				'fixedGutter': True
			}
		)

class CardForm(forms.ModelForm):
	value = forms.CharField(label="Valor", widget=code_mirror)
	percent = forms.CharField(label="Percentual", widget=code_mirror)
	class Meta:
		model = Card
		fields = '__all__'