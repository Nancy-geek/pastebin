"""
Repository layer for database operations.
Abstracts data access logic from business logic.
"""
from .models import Paste


class PasteRepository:
    """Handles all database operations for Paste model."""
    
    def create(self, content, expires_at=None, max_views=None):
        """Create a new paste."""
        return Paste.objects.create(
            content=content,
            expires_at=expires_at,
            max_views=max_views
        )
    
    def get(self, paste_id):
        """Get paste by ID."""
        try:
            return Paste.objects.get(id=paste_id)
        except Paste.DoesNotExist:
            return None
    
    # Must be inside transaction.atomic()
    def get_for_update(self, paste_id):          
        """Get paste with row-level lock for atomic updates."""
        try:
            return Paste.objects.select_for_update().get(id=paste_id)
        except Paste.DoesNotExist:
            return None
    
    def save(self, paste, update_fields=None):
        """Save paste instance."""
        paste.save(update_fields=update_fields)
        return paste
