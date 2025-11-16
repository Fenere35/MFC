from django.contrib import admin
from django.utils.html import format_html
from .models import *

class OfficeServiceInline(admin.TabularInline):
    model = OfficeService
    extra = 1
    raw_id_fields = ['service']

class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1
    raw_id_fields = ['office']

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_count']
    list_display_links = ['name']
    search_fields = ['name', 'description']
    
    @admin.display(description='Количество услуг')
    def service_count(self, obj):
        return obj.service_set.count()

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'execution_term', 'cost', 'office_count']
    list_filter = ['category', 'cost']
    list_display_links = ['name']
    search_fields = ['name', 'description']
    raw_id_fields = ['category']
    
    @admin.display(description='Доступно в офисах')
    def office_count(self, obj):
        return obj.officeservice_set.count()

@admin.register(MFCOffice)
class MFCOfficeAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'employee_count']
    list_filter = ['name']
    search_fields = ['name', 'address', 'phone']
    inlines = [EmployeeInline, OfficeServiceInline]
    
    @admin.display(description='Сотрудников')
    def employee_count(self, obj):
        return obj.employee_set.count()

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'office', 'position', 'news_count']
    list_filter = ['position', 'office']
    list_display_links = ['full_name']
    search_fields = ['full_name']
    raw_id_fields = ['office']
    
    @admin.display(description='Новостей')
    def news_count(self, obj):
        return obj.news_set.count()

@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'application_count']
    list_display_links = ['name']
    
    @admin.display(description='Заявлений')
    def application_count(self, obj):
        return obj.application_set.count()

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_info', 'service', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'service']
    list_display_links = ['id']
    search_fields = ['user__username', 'service__name']
    raw_id_fields = ['user', 'service', 'status']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    @admin.display(description='Пользователь')
    def user_info(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.username})"
        
    actions = ['mark_as_completed', 'mark_as_rejected']
    
    @admin.action(description='Пометить как выполненные')
    def mark_as_completed(self, request, queryset):
        completed_status = ApplicationStatus.objects.get(name='Выполнено')
        updated = queryset.update(status=completed_status)
        self.message_user(request, f'{updated} заявлений помечено как выполненные.')
    
    @admin.action(description='Пометить как отклоненные')
    def mark_as_rejected(self, request, queryset):
        rejected_status = ApplicationStatus.objects.get(name='Отклонено')
        updated = queryset.update(status=rejected_status)
        self.message_user(request, f'{updated} заявлений помечено как отклоненные.')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_info', 'office', 'service', 'appointment_datetime', 'status']
    list_filter = ['status', 'office', 'appointment_datetime']
    list_display_links = ['id']
    search_fields = ['user__username', 'office__name']
    raw_id_fields = ['user', 'office', 'service']
    
    @admin.display(description='Пользователь')
    def user_info(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    actions = ['mark_as_completed', 'cancel_appointments']
    
    @admin.action(description='Пометить как выполненные')
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} записей помечено как выполненные.')
    
    @admin.action(description='Отменить записи')
    def cancel_appointments(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} записей отменено.')

@admin.register(OfficeService)
class OfficeServiceAdmin(admin.ModelAdmin):
    list_display = ['office', 'service']
    list_filter = ['office']
    raw_id_fields = ['office', 'service']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_at', 'short_content']
    list_filter = ['published_at', 'author']
    list_display_links = ['title']
    search_fields = ['title', 'content']
    raw_id_fields = ['author']
    date_hierarchy = 'published_at'
    
    @admin.display(description='Содержание')
    def short_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content

# Регистрируем UserProfile отдельно
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_snils', 'is_staff']
    
    @admin.display(description='СНИЛС')
    def get_snils(self, obj):
        try:
            return obj.userprofile.snils
        except UserProfile.DoesNotExist:
            return "Не указан"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)