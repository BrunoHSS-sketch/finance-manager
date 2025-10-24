# financial_management/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView # <--- Verifique/Adicione esta linha
from django.contrib.staticfiles.storage import staticfiles_storage # <--- Verifique/Adicione esta linha
# from django.conf import settings # <- Esta não é estritamente necessária aqui

urlpatterns = [
    # Redirecionamento para o favicon.ico
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("images/favicon.ico"), permanent=True),
        name="favicon_ico",
    ),
    # Opcional: Redirecionamento para favicon.png (se necessário)
    path(
        "favicon.png",
        RedirectView.as_view(url=staticfiles_storage.url("images/favicon-32x32.png"), permanent=True),
        name="favicon_png",
    ),

    # Suas rotas existentes:
    path('admin/', admin.site.urls),
    path('', include('finance.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
