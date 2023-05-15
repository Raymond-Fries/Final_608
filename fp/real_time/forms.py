from django import forms
from .models import Companies

# creating a form
class Company_Select_Form(forms.Form):
    company_select = forms.ModelChoiceField(queryset=Companies.objects.only('symbol'),empty_label=None, initial='AMD',required=False)

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['company_select'].queryset = Companies.objects.only('symbol')
