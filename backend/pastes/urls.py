from django.urls import path
from . import views

urlpatterns = [
    path('api/healthz', views.HealthCheckView.as_view(), name='health_check'),
    path('api/pastes', views.PasteView.as_view(), name='create_paste'),
    path('api/pastes/<uuid:paste_id>', views.PasteDetailView.as_view(), name='fetch_paste'),
    path('p/<uuid:paste_id>', views.view_paste_html, name='view_paste_html'),
]
