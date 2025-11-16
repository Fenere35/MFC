from django.core.mail import send_mail
from django.conf import settings

def send_appointment_notification(appointment):
    """Логирование уведомления о записи на прием (без реальной отправки)"""
    print("=" * 50)
    print("📧 EMAIL УВЕДОМЛЕНИЕ (в реальном проекте было бы отправлено)")
    print(f"Кому: {appointment.user.email}")
    print(f"Тема: Запись на прием в МФЦ подтверждена")
    print(f"Услуга: {appointment.service.name}")
    print(f"Офис: {appointment.office.name}") 
    print(f"Время: {appointment.appointment_datetime}")
    print("=" * 50)
    return True  # Всегда возвращаем успех для разработки

def send_application_status_notification(application):
    """Логирование изменения статуса заявления"""
    print("=" * 50)
    print("📧 EMAIL УВЕДОМЛЕНИЕ (в реальном проекте было бы отправлено)")
    print(f"Кому: {application.user.email}")
    print(f"Тема: Статус заявления изменен")
    print(f"Заявление: {application.service.name}")
    print(f"Новый статус: {application.status.name}")
    print("=" * 50)
    return True