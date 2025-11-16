from django import forms
from .models import Application, Service

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['service', 'application_data']
        widgets = {
            'application_data': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Опишите детали вашего заявления...'
            }),
        }
        labels = {
            'service': 'Услуга',
            'application_data': 'Детали заявления',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.all()
        self.fields['service'].empty_label = "Выберите услугу"