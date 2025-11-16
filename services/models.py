from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class ServiceCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название категории")
    description = models.TextField(verbose_name="Описание", blank=True)
    
    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание", blank=True)
    execution_term = models.CharField(max_length=100, verbose_name="Срок исполнения")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость", default=0)
    
    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class MFCOffice(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название офиса")
    address = models.CharField(max_length=300, verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    work_schedule = models.CharField(max_length=100, verbose_name="График работы")
    
    class Meta:
        verbose_name = "Офис МФЦ"
        verbose_name_plural = "Офисы МФЦ"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    POSITION_CHOICES = [
        ('specialist', 'Специалист'),
        ('manager', 'Управляющий'),
        ('consultant', 'Консультант'),
        ('operator', 'Оператор'),
    ]
    
    office = models.ForeignKey(MFCOffice, on_delete=models.CASCADE, verbose_name="Офис")
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, verbose_name="Должность")
    
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} - {self.get_position_display()}"

class ApplicationStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название статуса")
    
    class Meta:
        verbose_name = "Статус заявления"
        verbose_name_plural = "Статусы заявлений"
        ordering = ['id']
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    snils = models.CharField(max_length=14, unique=True, verbose_name="СНИЛС")
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.snils})"

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    status = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE, verbose_name="Статус")
    application_data = models.TextField(verbose_name="Данные заявления", default="", blank=True)  
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Заявление"
        verbose_name_plural = "Заявления"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявление #{self.id} - {self.service.name}"
    
    def get_absolute_url(self):
        return reverse('application_detail', args=[str(self.id)])

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    office = models.ForeignKey(MFCOffice, on_delete=models.CASCADE, verbose_name="Офис")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    appointment_datetime = models.DateTimeField(verbose_name="Дата и время приема")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    
    class Meta:
        verbose_name = "Запись на прием"
        verbose_name_plural = "Записи на прием"
        ordering = ['appointment_datetime']
    
    def __str__(self):
        return f"Запись #{self.id} - {self.user.get_full_name()}"

class OfficeService(models.Model):
    office = models.ForeignKey(MFCOffice, on_delete=models.CASCADE, verbose_name="Офис")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    
    class Meta:
        verbose_name = "Услуга офиса"
        verbose_name_plural = "Услуги офисов"
        unique_together = ['office', 'service']
    
    def __str__(self):
        return f"{self.office.name} - {self.service.name}"

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    published_at = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")
    author = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Автор")
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])