from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from .models import *

def home(request):
    """Главная страница с виджетами"""
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

def service_list(request):
    """Список всех услуг"""
    services = Service.objects.select_related('category').all()
    
    # Поиск
    query = request.GET.get('q')
    if query:
        services = services.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Фильтрация по категории
    category_id = request.GET.get('category')
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

def service_detail(request, service_id):
    """Детальная страница услуги"""
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

def office_list(request):
    """Список офисов МФЦ"""
    offices = MFCOffice.objects.all()
    
    # Поиск
    query = request.GET.get('q')
    if query:
        offices = offices.filter(
            Q(name__icontains=query) | 
            Q(address__icontains=query)
        )
    
    context = {
        'offices': offices,
        'query': query,
    }
    return render(request, 'services/office_list.html', context)

def news_list(request):
    """Список новостей"""
    news_list = News.objects.select_related('author').all()
    
    context = {
        'news_list': news_list,
    }
    return render(request, 'services/news_list.html', context)

def news_detail(request, news_id):
    """Детальная страница новости"""
    news = get_object_or_404(News.objects.select_related('author'), id=news_id)
    
    context = {
        'news': news,
    }
    return render(request, 'services/news_detail.html', context)

@login_required
def application_list(request):
    """Список заявлений пользователя"""
    applications = Application.objects.filter(
        user=request.user
    ).select_related('service', 'status')
    
    context = {
        'applications': applications,
    }
    return render(request, 'services/application_list.html', context)

@login_required
def application_detail(request, application_id):
    """Детальная страница заявления"""
    application = get_object_or_404(
        Application.objects.select_related('service', 'status'),
        id=application_id,
        user=request.user
    )
    
    context = {
        'application': application,
    }
    return render(request, 'services/application_detail.html', context)

def search(request):
    """Полнотекстовый поиск"""
    query = request.GET.get('q', '')
    results = {}
    
    if query:
        # Поиск по услугам
        services = Service.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )[:10]
        
        # Поиск по офисам
        offices = MFCOffice.objects.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query)
        )[:10]
        
        # Поиск по новостям
        news = News.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )[:10]
        
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

# Обработка 404 ошибки
def custom_404(request, exception):
    return render(request, '404.html', status=404)