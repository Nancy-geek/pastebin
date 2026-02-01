from rest_framework import serializers


class CreatePasteSerializer(serializers.Serializer):
    """Serializer for paste creation with validation."""
    content = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)
    ttl_seconds = serializers.IntegerField(required=False, min_value=1)
    max_views = serializers.IntegerField(required=False, min_value=1)
