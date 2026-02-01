from django.shortcuts import render
from django.db import connection
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreatePasteSerializer
from .services_utility import PasteService, TimeService


class HealthCheckView(APIView):
    """Health check endpoint that verifies database connectivity."""
    
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return Response({"ok": True}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"ok": False}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class PasteView(APIView):
    """Handle paste creation and retrieval."""
    
    def post(self, request):
        """Create a new paste with optional TTL and view limit."""
        serializer = CreatePasteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        service = PasteService()
        paste = service.create_paste(
            content=data['content'],
            ttl_seconds=data.get('ttl_seconds'),
            max_views=data.get('max_views')
        )
        
        frontend_url = settings.FRONTEND_URL
        paste_url = f"{frontend_url}/p/{paste.id}"
        
        return Response(
            {"id": str(paste.id), "url": paste_url},
            status=status.HTTP_201_CREATED
        )


class PasteDetailView(APIView):
    """Fetch paste by ID with view count increment."""
    
    def get(self, request, paste_id):
        """Fetch paste by ID, increment view count atomically."""
        time_service = TimeService(test_mode=settings.TEST_MODE)
        service = PasteService(time_service=time_service)
        
        paste_data, error = service.fetch_paste(paste_id, request)
        
        if error:
            return Response(
                {"error": error},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                "content": paste_data['content'],
                "remaining_views": paste_data['remaining_views'],
                "expires_at": paste_data['expires_at'].isoformat() if paste_data['expires_at'] else None
            },
            status=status.HTTP_200_OK
        )


def view_paste_html(request, paste_id):
    """Render paste as HTML page (kept as function for template rendering)."""
    time_service = TimeService(test_mode=settings.TEST_MODE)
    service = PasteService(time_service=time_service)
    
    paste = service.get_paste_for_view(paste_id, request)
    
    if not paste:
        return render(request, '404.html', status=404)
    
    return render(request, 'paste.html', {'paste': paste, 'paste_id': paste_id})
