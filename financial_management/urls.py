"""
URL configuration for financial_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    # Redirecionamento para o favicon.ico
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("../finance/static/images/favicon.ico"), permanent=True),
        name="favicon_ico",
    ),
    # Opcional: Redirecionamento para favicon.png (se necessário)
    path(
        "favicon.png",
        RedirectView.as_view(url=staticfiles_storage.url("../finance/static/images/favicon-32x32.png"), permanent=True), # Ou o PNG que preferir
        name="favicon_png",
    ),

    # Suas rotas existentes:
    path('admin/', admin.site.urls),
    path('', include('finance.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]


