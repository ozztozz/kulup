from rest_framework import serializers

from .models import User


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "adi",
            "soyadi",
            "telefon",
            "is_staff",
            "is_active",
            "created_at",
            "updated_at",
        ]
