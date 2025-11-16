from django.core.mail import send_mail
from django.conf import settings

def send_appointment_notification(appointment):
    """Отправка уведомления о записи на прием"""
    subject = f'Запись на прием в МФЦ подтверждена'
    message = f'''
    Уважаемый(ая) {appointment.user.get_full_name()},
    
    Ваша запись на прием подтверждена:
    - Услуга: {appointment.service.name}
    - Офис: {appointment.office.name}
    - Адрес: {appointment.office.address}
    - Дата и время: {appointment.appointment_datetime.strftime("%d.%m.%Y %H:%M")}
    
    С уважением,
    МФЦ-Онлайн
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.user.email],
        fail_silently=False,
    )