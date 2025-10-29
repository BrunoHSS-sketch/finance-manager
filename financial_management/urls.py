# financial_management/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse  # <--- IMPORT ADICIONADO
from django.core import management  # <--- IMPORT ADICIONADO
from django.conf import settings  # <--- IMPORT ADICIONADO


# ===============================================
# FUNÇÃO SIMPLES PARA A VERCEL CHAMAR O CRON
# ===============================================
def vercel_cron_handler(request):
    """
    View simples que a Vercel chama.
    Ela executa o management command e retorna uma resposta HTTP.
    Adicione uma camada de segurança se precisar (ex: verificar um header secreto).
    """
    # Simples verificação de segurança (opcional, mas recomendado)
    # Você precisaria definir CRON_SECRET no seu ambiente Vercel
    # auth_header = request.headers.get('Authorization')
    # expected_secret = f"Bearer {settings.CRON_SECRET}"
    # if not settings.CRON_SECRET or auth_header != expected_secret:
    #    return HttpResponse("Unauthorized", status=401)

    try:
        management.call_command('generate_recurrences')
        return HttpResponse("Cron job executed successfully.")
    except Exception as e:
        # Logar o erro seria ideal aqui
        return HttpResponse(f"Error executing cron job: {e}", status=500)


# ===============================================

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Para login/logout
    path('', include('finance.urls')),  # Inclui as URLs da sua app finance

    # ===============================================
    # NOVA ROTA PARA O CRON DA VERCEL
    # ===============================================
    path('api/cron/generate_recurrences', vercel_cron_handler, name='vercel_cron_handler'),
    # ===============================================

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
