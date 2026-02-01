"""
Business logic layer for paste operations.
Follows Single Responsibility Principle - each service handles one domain concern.
"""
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from .models import Paste
from .paste_repository import PasteRepository


class TimeService:
    """Handles time-related operations, including TEST_MODE support."""
    
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
    
    def get_current_time(self, request):
        """Get current time, respecting TEST_MODE and x-test-now-ms header."""
        if self.test_mode:
            test_time_ms = request.META.get('HTTP_X_TEST_NOW_MS')
            if test_time_ms:
                try:
                    from datetime import datetime
                    timestamp_seconds = int(test_time_ms) / 1000.0
                    return datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
                except (ValueError, OSError):
                    pass
        return timezone.now()


class PasteAvailabilityService:
    """Determines if a paste is available based on expiry and view limits."""
    
    @staticmethod
    def is_available(paste, current_time):
        """Check if paste is available based on expiry and view count."""
        if paste.expires_at and current_time >= paste.expires_at:
            return False
        if paste.max_views is not None and paste.view_count >= paste.max_views:
            return False
        return True


class PasteService:
    """Core business logic for paste operations."""
    
    def __init__(self, repository=None, time_service=None, availability_service=None):
        self.repository = repository or PasteRepository()
        self.time_service = time_service or TimeService()
        self.availability_service = availability_service or PasteAvailabilityService()
    
    def create_paste(self, content, ttl_seconds=None, max_views=None):
        """Create a new paste with optional TTL and view limit."""
        expires_at = None
        if ttl_seconds:
            expires_at = timezone.now() + timedelta(seconds=ttl_seconds)
        
        return self.repository.create(
            content=content,
            expires_at=expires_at,
            max_views=max_views
        )
    
    def fetch_paste(self, paste_id, request):
        """
        Fetch paste by ID and increment view count atomically.
        Returns tuple: (paste_data, error)
        """
        current_time = self.time_service.get_current_time(request)
        
        with transaction.atomic():
            paste = self.repository.get_for_update(paste_id)
            if not paste:
                return None, "Paste not found or no longer available"
            
            if not self.availability_service.is_available(paste, current_time):
                return None, "Paste not found or no longer available"
            
            paste.view_count += 1
            self.repository.save(paste, update_fields=['view_count'])
            
            remaining_views = None
            if paste.max_views is not None:
                remaining_views = paste.max_views - paste.view_count
            
            return {
                'content': paste.content,
                'remaining_views': remaining_views,
                'expires_at': paste.expires_at
            }, None
    
    def get_paste_for_view(self, paste_id, request):
        """Get paste for HTML view without incrementing count."""
        current_time = self.time_service.get_current_time(request)
        paste = self.repository.get(paste_id)
        
        if not paste or not self.availability_service.is_available(paste, current_time):
            return None
        
        return paste
