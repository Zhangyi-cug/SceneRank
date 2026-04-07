from django.urls import path
from . import views

urlpatterns = [
    path('config/', views.config_view, name='config'),
    path('config/reset/', views.config_reset, name='config-reset'),
    path('results/', views.results_view, name='results'),
    path('results/clear/', views.results_clear, name='results-clear'),
    path('results/export/', views.results_export, name='results-export'),
    path('results/<int:pk>/', views.result_delete, name='result-delete'),
    path('auth/login/', views.admin_login, name='admin-login'),
]
