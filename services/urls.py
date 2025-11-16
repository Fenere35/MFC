from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.service_list, name='service_list'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('offices/', views.office_list, name='office_list'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('applications/', views.application_list, name='application_list'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('search/', views.search, name='search'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
]