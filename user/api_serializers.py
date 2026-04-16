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


class UserListSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "adi",
            "soyadi",
            "display_name",
            "is_active",
            "is_staff",
        ]

    def get_display_name(self, obj):
        full_name = f"{obj.adi} {obj.soyadi}".strip()
        return full_name if full_name else obj.email
