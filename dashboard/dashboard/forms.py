from django import forms
from dashboard.models import sojourner

def get_product(dc):
	choice_list = sojourner.objects.filter(dc=dc).distinct('product')
	return tuple([(x, x) for x in choice_list])

def get_role(dc, product):
	choice_list = sojourner.objects.filter(dc=dc, product=product).distinct('role')

def get_env(dc, product, role):
	choice_list = sojourner.objects.filter(dc=dc, product=product, role=role).distinct('environment')

class SelectForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(SelectForm, self).__init__(*args, **kwargs)
		self.fields['myproduct'] = forms.ChoiceField(choices=get_product(self.data['dc']), widget=forms.Select(attrs={'onchange': 'SelectForm.submit();'}))

class SelectRole(forms.Form):
	def __init__(self, *args, **kwargs):
		super(SelectRole, self).__init__(*args, **kwargs)
		self.fields['myrole'] = forms.ChoiceField(choices=get_role(self.data['dc'], self.data['product']), widget=forms.Select(attrs={'onchange': 'SelectRole.submit();'}))

class SelectEnv(forms.Form):
	def __init__(self, *args, **kwargs):
		super(SelectEnv, self).__init__(*args, **kwargs)
		self.fields['myenv'] = forms.ChoiceField(choices=get_env(self.data['dc'], self.data['product'], self.data['role']), widget=forms.Select(attrs={'onchange': 'SelectEnv.submit();'}))

