from django.urls import path
from django.http import JsonResponse
from . import views

def api_root(request):
    return JsonResponse({
        'service': 'Pastebin API',
        'version': '1.0',
        'endpoints': {
            'health': '/api/healthz',
            'create': 'POST /api/pastes',
            'fetch': 'GET /api/pastes/<uuid>',
            'view': 'GET /p/<uuid>'
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('api/healthz', views.HealthCheckView.as_view(), name='health_check'),
    path('api/pastes', views.PasteView.as_view(), name='create_paste'),
    path('api/pastes/<uuid:paste_id>', views.PasteDetailView.as_view(), name='fetch_paste'),
    path('p/<uuid:paste_id>', views.view_paste_html, name='view_paste_html'),
]
