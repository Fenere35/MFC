from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.core.paginator import Paginator
from .models import *
from .forms import ApplicationForm, AppointmentForm
from django.contrib import messages
from django.views.decorators.cache import cache_page
from .utils import send_appointment_notification

def custom_404(request, exception):
    return render(request, 'services/404.html', status=404)

def custom_500(request):
    return render(request, 'services/500.html', status=500)

@cache_page(60 * 15)
def home(request):
    """Главная страница с виджетами"""
    try:
        # Виджет 1: Последние новости
        latest_news = News.objects.select_related('author').order_by('-published_at')[:5]
        
        # Виджет 2: Популярные услуги (по количеству заявлений)
        popular_services = Service.objects.annotate(
            application_count=Count('application')
        ).order_by('-application_count')[:5]
        
        # Виджет 3: Офисы МФЦ
        offices = MFCOffice.objects.annotate(
            service_count=Count('officeservice')
        ).order_by('?')[:5]
        
        # Виджет 4: Статистика (агрегатные функции)
        stats = {
            'total_services': Service.objects.count(),
            'total_offices': MFCOffice.objects.count(),
            'total_applications': Application.objects.count(),
            'avg_service_cost': Service.objects.aggregate(avg_cost=Avg('cost'))['avg_cost'] or 0,
        }
        
        context = {
            'latest_news': latest_news,
            'popular_services': popular_services,
            'offices': offices,
            'stats': stats,
        }
        return render(request, 'services/home.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке главной страницы: {e}")


@login_required
def appointment_list(request):
    """Список записей на прием пользователя"""
    try:
        appointments = Appointment.objects.filter(
            user=request.user
        ).select_related('office', 'service').order_by('appointment_datetime')
        
        context = {
            'appointments': appointments,
        }
        return render(request, 'services/appointment_list.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке записей на прием: {e}")

@login_required
def appointment_create(request):
    """Создание новой записи на прием"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            
            # Отправляем уведомление
            try:
                send_appointment_notification(appointment)
                messages.success(request, 'Запись на прием успешно создана! На вашу почту отправлено уведомление.')
            except:
                messages.success(request, 'Запись на прием успешно создана!')
                
            return redirect('services:appointment_list')

@login_required
def appointment_update(request, appointment_id):
    """Редактирование записи на прием"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        user=request.user
    )
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Запись на прием успешно обновлена!')
            return redirect('services:appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'services/appointment_form.html', context)

@login_required
def appointment_delete(request, appointment_id):
    """Удаление записи на прием"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        user=request.user
    )
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Запись на прием успешно удалена!')
        return redirect('services:appointment_list')
    
    context = {'appointment': appointment}
    return render(request, 'services/appointment_confirm_delete.html', context)

@login_required
def application_create(request):
    """Создание нового заявления"""
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            # Устанавливаем начальный статус "Подано"
            initial_status = ApplicationStatus.objects.get(name='Подано')
            application.status = initial_status
            application.save()
            messages.success(request, 'Заявление успешно подано!')
            return redirect('services:application_list')
    else:
        form = ApplicationForm()
    
    context = {'form': form}
    return render(request, 'services/application_form.html', context)

@login_required
def application_update(request, application_id):
    """Редактирование заявления"""
    application = get_object_or_404(
        Application, 
        id=application_id, 
        user=request.user
    )
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявление успешно обновлено!')
            return redirect('services:application_list')
    else:
        form = ApplicationForm(instance=application)
    
    context = {
        'form': form,
        'application': application,
    }
    return render(request, 'services/application_form.html', context)

@login_required
def application_delete(request, application_id):
    """Удаление заявления"""
    application = get_object_or_404(
        Application, 
        id=application_id, 
        user=request.user
    )
    
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Заявление успешно удалено!')
        return redirect('services:application_list')
    
    context = {'application': application}
    return render(request, 'services/application_confirm_delete.html', context)

@login_required
def application_detail(request, application_id):
    """Детальная страница заявления"""
    try:
        application = get_object_or_404(
            Application.objects.select_related('service', 'status', 'service__category'),
            id=application_id,
            user=request.user
        )
        
        context = {
            'application': application,
        }
        return render(request, 'services/application_detail.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке заявления: {e}")



def service_list(request):
    """Список всех услуг"""
    try:
        print("=== SERVICE LIST DEBUG ===")
        print("GET parameters:", dict(request.GET))
        
        # Получаем все услуги
        services = Service.objects.select_related('category').all()
        
        # Поиск
        query = request.GET.get('q', '')
        print("Search query:", query)
        
        if query:
            services = services.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
            print("Filtered services count:", services.count())
        
        # Фильтрация по категории
        category_id = request.GET.get('category')
        print("Category ID:", category_id)
        if category_id:
            services = services.filter(category_id=category_id)
        
        categories = ServiceCategory.objects.all()
        
        context = {
            'services': services,
            'categories': categories,
            'query': query,
            'selected_category': category_id,
        }
        
        return render(request, 'services/service_list.html', context)
        
    except Exception as e:
        print(f"Error in service_list: {e}")
        return HttpResponse(f"Ошибка при загрузке услуг: {e}")

def service_detail(request, service_id):
    """Детальная страница услуги"""
    try:
        service = get_object_or_404(
            Service.objects.select_related('category'),
            id=service_id
        )
        
        # Офисы, где предоставляется эта услуга
        offices_with_service = MFCOffice.objects.filter(
            officeservice__service=service
        ).distinct()
        
        context = {
            'service': service,
            'offices_with_service': offices_with_service,
        }
        return render(request, 'services/service_detail.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке услуги: {e}")

def office_list(request):
    """Список офисов МФЦ"""
    try:
        print("=== OFFICE LIST DEBUG ===")
        print("GET parameters:", dict(request.GET))
        
        offices = MFCOffice.objects.all()
        
        # Поиск
        query = request.GET.get('q', '')
        print("Search query:", query)
        
        if query:
            offices = offices.filter(
                Q(name__icontains=query) | 
                Q(address__icontains=query)
            )
            print("Filtered offices count:", offices.count())
        
        context = {
            'offices': offices,
            'query': query,
        }
        return render(request, 'services/office_list.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке офисов: {e}")

def news_list(request):
    """Список новостей"""
    try:
        news_list = News.objects.select_related('author').all()
        
        context = {
            'news_list': news_list,
        }
        return render(request, 'services/news_list.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке новостей: {e}")

def news_detail(request, news_id):
    """Детальная страница новости"""
    try:
        news = get_object_or_404(
            News.objects.select_related('author', 'author__office'), 
            id=news_id
        )
        
        # Получаем связанные новости (последние 3, исключая текущую)
        related_news_list = News.objects.exclude(id=news_id).select_related('author')[:3]
        
        context = {
            'news': news,
            'related_news_list': related_news_list,
        }
        return render(request, 'services/news_detail.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке новости: {e}")

@login_required
def application_list(request):
    """Список заявлений пользователя"""
    try:
        applications = Application.objects.filter(
            user=request.user
        ).select_related('service', 'status')
        
        context = {
            'applications': applications,
        }
        return render(request, 'services/application_list.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке заявлений: {e}")

@login_required
def application_detail(request, application_id):
    """Детальная страница заявления"""
    try:
        application = get_object_or_404(
            Application.objects.select_related('service', 'status'),
            id=application_id,
            user=request.user
        )
        
        context = {
            'application': application,
        }
        return render(request, 'services/application_detail.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при загрузке заявления: {e}")

def search(request):
    """Полнотекстовый поиск"""
    try:
        query = request.GET.get('q', '')
        results = {}
        
        if query:
            # Поиск по услугам
            services = Service.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            ).select_related('category')[:10]
            
            # Поиск по офисам
            offices = MFCOffice.objects.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query)
            )[:10]
            
            # Поиск по новостям
            news = News.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            ).select_related('author')[:10]
            
            results = {
                'services': services,
                'offices': offices,
                'news': news,
            }
        
        context = {
            'query': query,
            'results': results,
        }
        return render(request, 'services/search.html', context)
    except Exception as e:
        return HttpResponse(f"Ошибка при поиске: {e}")

def search_suggestions(request):
    """API для подсказок поиска"""
    try:
        query = request.GET.get('q', '')
        suggestions = []
        
        print(f"Search suggestions request: {query}")
        
        if len(query) >= 2:
            # Поиск услуг для подсказок
            services = Service.objects.filter(
                Q(name__icontains=query)
            )[:5]
            
            for service in services:
                suggestions.append({
                    'text': service.name,
                    'type': 'service'
                })
            
            # Поиск офисов для подсказок
            offices = MFCOffice.objects.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query)
            )[:3]
            
            for office in offices:
                suggestions.append({
                    'text': office.name,
                    'type': 'office'
                })
            
            # Добавляем популярные запросы, если мало результатов
            if len(suggestions) < 3:
                popular_suggestions = [
                    {'text': 'паспорт', 'type': 'popular'},
                    {'text': 'загранпаспорт', 'type': 'popular'},
                    {'text': 'регистрация', 'type': 'popular'},
                    {'text': 'налоговый вычет', 'type': 'popular'},
                    {'text': 'пособие', 'type': 'popular'},
                ]
                
                for pop in popular_suggestions:
                    if query.lower() in pop['text'].lower() and len(suggestions) < 8:
                        suggestions.append(pop)
                        
        # Убираем дубликаты по тексту
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s['text'] not in seen:
                seen.add(s['text'])
                unique_suggestions.append(s)
        
        unique_suggestions = unique_suggestions[:8]
        print(f"Returning suggestions: {unique_suggestions}")
        
        return JsonResponse({'suggestions': [s['text'] for s in unique_suggestions]})
    except Exception as e:
        print(f"Error in search_suggestions: {e}")
        return JsonResponse({'suggestions': []})

# Обработка 404 ошибки
def custom_404(request, exception):
    return render(request, '404.html', status=404)