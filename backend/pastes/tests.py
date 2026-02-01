"""
Unit tests for service layer.
Demonstrates testability of refactored code with dependency injection.
"""
from django.test import TestCase, RequestFactory
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock, patch
from pastes.services_utility import PasteService, TimeService, PasteAvailabilityService
from pastes.paste_repository import PasteRepository
from pastes.models import Paste


class TimeServiceTest(TestCase):
    """Test TimeService for deterministic time handling."""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_normal_mode_returns_current_time(self):
        """In normal mode, should return current time."""
        service = TimeService(test_mode=False)
        request = self.factory.get('/')
        
        result = service.get_current_time(request)
        
        self.assertIsNotNone(result)
        self.assertAlmostEqual(
            result.timestamp(),
            timezone.now().timestamp(),
            delta=1
        )
    
    def test_test_mode_with_header(self):
        """In test mode with header, should return header time."""
        service = TimeService(test_mode=True)
        request = self.factory.get('/', HTTP_X_TEST_NOW_MS='1700000000000')
        
        result = service.get_current_time(request)
        
        self.assertEqual(result.timestamp(), 1700000000.0)
    
    def test_test_mode_without_header_falls_back(self):
        """In test mode without header, should fall back to current time."""
        service = TimeService(test_mode=True)
        request = self.factory.get('/')
        
        result = service.get_current_time(request)
        
        self.assertAlmostEqual(
            result.timestamp(),
            timezone.now().timestamp(),
            delta=1
        )


class PasteAvailabilityServiceTest(TestCase):
    """Test paste availability logic."""
    
    def test_available_paste_with_no_limits(self):
        """Paste with no limits should be available."""
        paste = Paste(content="test", view_count=0)
        current_time = timezone.now()
        
        result = PasteAvailabilityService.is_available(paste, current_time)
        
        self.assertTrue(result)
    
    def test_expired_paste_by_time(self):
        """Paste past expiry time should be unavailable."""
        paste = Paste(
            content="test",
            expires_at=timezone.now() - timedelta(seconds=1),
            view_count=0
        )
        current_time = timezone.now()
        
        result = PasteAvailabilityService.is_available(paste, current_time)
        
        self.assertFalse(result)
    
    def test_expired_paste_by_views(self):
        """Paste at max views should be unavailable."""
        paste = Paste(content="test", max_views=5, view_count=5)
        current_time = timezone.now()
        
        result = PasteAvailabilityService.is_available(paste, current_time)
        
        self.assertFalse(result)
    
    def test_paste_with_remaining_views(self):
        """Paste below max views should be available."""
        paste = Paste(content="test", max_views=5, view_count=4)
        current_time = timezone.now()
        
        result = PasteAvailabilityService.is_available(paste, current_time)
        
        self.assertTrue(result)


class PasteServiceTest(TestCase):
    """Test PasteService business logic."""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_create_paste_without_limits(self):
        """Should create paste without expiry or view limits."""
        service = PasteService()
        
        paste = service.create_paste(content="Hello World")
        
        self.assertIsNotNone(paste.id)
        self.assertEqual(paste.content, "Hello World")
        self.assertIsNone(paste.expires_at)
        self.assertIsNone(paste.max_views)
        self.assertEqual(paste.view_count, 0)
    
    def test_create_paste_with_ttl(self):
        """Should create paste with TTL expiry."""
        service = PasteService()
        
        paste = service.create_paste(content="Test", ttl_seconds=60)
        
        self.assertIsNotNone(paste.expires_at)
        expected_expiry = timezone.now() + timedelta(seconds=60)
        self.assertAlmostEqual(
            paste.expires_at.timestamp(),
            expected_expiry.timestamp(),
            delta=1
        )
    
    def test_create_paste_with_max_views(self):
        """Should create paste with view limit."""
        service = PasteService()
        
        paste = service.create_paste(content="Test", max_views=5)
        
        self.assertEqual(paste.max_views, 5)
        self.assertEqual(paste.view_count, 0)
    
    def test_fetch_paste_increments_view_count(self):
        """Fetching paste should increment view count atomically."""
        paste = Paste.objects.create(content="Test", max_views=5)
        service = PasteService()
        request = self.factory.get('/')
        
        result, error = service.fetch_paste(paste.id, request)
        
        self.assertIsNone(error)
        self.assertEqual(result['content'], "Test")
        self.assertEqual(result['remaining_views'], 4)
        
        # Verify in database
        paste.refresh_from_db()
        self.assertEqual(paste.view_count, 1)
    
    def test_fetch_paste_at_max_views_fails(self):
        """Fetching paste at max views should fail."""
        paste = Paste.objects.create(content="Test", max_views=5, view_count=5)
        service = PasteService()
        request = self.factory.get('/')
        
        result, error = service.fetch_paste(paste.id, request)
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)
    
    def test_fetch_expired_paste_fails(self):
        """Fetching expired paste should fail."""
        paste = Paste.objects.create(
            content="Test",
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        service = PasteService()
        request = self.factory.get('/')
        
        result, error = service.fetch_paste(paste.id, request)
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)
    
    def test_fetch_nonexistent_paste_fails(self):
        """Fetching non-existent paste should fail."""
        service = PasteService()
        request = self.factory.get('/')
        
        result, error = service.fetch_paste('00000000-0000-0000-0000-000000000000', request)
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)
    
    def test_remaining_views_calculation(self):
        """Should correctly calculate remaining views."""
        paste = Paste.objects.create(content="Test", max_views=10, view_count=3)
        service = PasteService()
        request = self.factory.get('/')
        
        result, error = service.fetch_paste(paste.id, request)
        
        self.assertIsNone(error)
        self.assertEqual(result['remaining_views'], 6)  # 10 - 4 (after increment)
    
    def test_unlimited_views_returns_null(self):
        """Paste without max_views should return null for remaining_views."""
        paste = Paste.objects.create(content="Test")
        service = PasteService()
        request = self.factory.get('/')
        
        result, error = service.fetch_paste(paste.id, request)
        
        self.assertIsNone(error)
        self.assertIsNone(result['remaining_views'])
