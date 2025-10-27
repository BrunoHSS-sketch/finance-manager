from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # URLs de Transações (Lançamentos)
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/create/', views.transactions_create, name='transactions_create'),
    path('transactions/<int:pk>/edit/', views.transactions_edit, name='transactions_edit'),
    path('transactions/<int:pk>/delete/', views.transactions_delete, name='transactions_delete'),

    # URLs de Transações (Tipos Especiais)
    path('transactions/create_installment/', views.transactions_create_installment,
         name='transactions_create_installment'),
    path('transactions/create_transfer/', views.transactions_create_transfer, name='transactions_create_transfer'),

    # URLs de Plano de Parcelamento
    path('installments/<int:plan_pk>/edit/', views.installment_plan_edit, name='installment_plan_edit'),
    path('installments/<int:plan_pk>/delete/', views.installment_plan_delete, name='installment_plan_delete'),

    # ===============================================
    # NOVAS URLs: Para editar/excluir Transferências
    # ===============================================
    path('transfers/<int:pk>/edit/', views.transfer_edit, name='transfer_edit'),
    path('transfers/<int:pk>/delete/', views.transfer_delete, name='transfer_delete'),
    # ===============================================

    # URLs de Categorias
    path('categories/', views.category_list_create, name='category_list_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/toggle/', views.category_toggle_active, name='category_toggle_active'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # URLs de Contas
    path('accounts/', views.account_list_create, name='account_list_create'),
    path('accounts/<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('accounts/<int:pk>/toggle/', views.account_toggle_active, name='account_toggle_active'),
    path('accounts/<int:pk>/delete/', views.account_delete, name='account_delete'),

    # URLs de Metas
    path('goals/', views.goals_list_create, name='goals_list_create'),
    path('goals/<int:pk>/edit/', views.goals_edit, name='goals_edit'),
    path('goals/<int:pk>/delete/', views.goals_delete, name='goals_delete'),
]