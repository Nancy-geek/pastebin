"""Paste model for storing text content with expiry and view limits."""
import uuid
from django.db import models


class Paste(models.Model):
    """Paste model with time-based and view-count expiry."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Universally Unique Identifier,  instead of an auto-incrementing integer ID.
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # if editing allowed, then we have last_modified_at field 
    expires_at = models.DateTimeField(null=True, blank=True)
    max_views = models.IntegerField(null=True, blank=True)
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'pastes'
        indexes = [
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):   # how an object is represented as a string 
        return str(self.id)
    # else without this - <Paste: Paste object (1)>  instead of <Paste: 70166986-d8eb-4569-922d-871fb3f97b10>


