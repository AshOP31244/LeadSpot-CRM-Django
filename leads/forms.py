from django import forms
from .models import Lead


class LeadCreateForm(forms.ModelForm):
    contact_name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    contact_phone = forms.CharField(required=True)
    sector = forms.CharField(required=True)
    source = forms.CharField(required=True)

    class Meta:
        model = Lead
        fields = [
            'company_name',
            'city',
            'state',
            'sector',
            'contact_name',
            'contact_email',
            'contact_phone',
            'source',
            'department',
        ]
