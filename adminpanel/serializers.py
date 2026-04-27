from rest_framework import serializers
from accounts.models import User


class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "is_active",
            "is_staff",
            "date_joined",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()