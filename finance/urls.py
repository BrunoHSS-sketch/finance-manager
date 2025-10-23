from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('categorias/', views.category_list_create, name='category_list_create'),
    path('categorias/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categorias/<int:pk>/toggle/', views.category_toggle_active, name='category_toggle_active'),
    path('categorias/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('transacoes/', views.transactions_list, name='transactions_list'),
    path('transacoes/create/', views.transactions_create, name='transactions_create'),
    path('transacoes/<int:pk>/edit/', views.transactions_edit, name='transactions_edit'),
    path('transacoes/<int:pk>/delete/', views.transactions_delete, name='transactions_delete'),
    path('metas/', views.goals_list_create, name='goals_list_create'),
    path('metas/<int:pk>/edit/', views.goals_edit, name='goals_edit'),
    path('metas/<int:pk>/delete/', views.goals_delete, name='goals_delete'),
]