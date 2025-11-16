from django import forms
from .models import Appointment, Service, MFCOffice, Application
from django.utils import timezone
from datetime import datetime, timedelta

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['office', 'service', 'appointment_datetime']
        widgets = {
            'appointment_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'office': 'Офис МФЦ',
            'service': 'Услуга',
            'appointment_datetime': 'Дата и время приема',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'].queryset = MFCOffice.objects.all()
        self.fields['office'].empty_label = "Выберите офис"
        self.fields['service'].queryset = Service.objects.all()
        self.fields['service'].empty_label = "Выберите услугу"

        # Устанавливаем минимальную дату для записи (текущий день)
        today = timezone.now().date()
        min_datetime = datetime.combine(today, datetime.min.time()) + timedelta(days=1)
        self.fields['appointment_datetime'].widget.attrs['min'] = min_datetime.isoformat('T', 'minutes')[:16]

    def clean_appointment_datetime(self):
        appointment_datetime = self.cleaned_data['appointment_datetime']
        if appointment_datetime <= timezone.now():
            raise forms.ValidationError("Дата и время приема должны быть в будущем.")
        return appointment_datetime

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