from rest_framework import serializers

from api.models import User
from django.contrib.auth import get_user_model

user = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = (
            'id',
            'email',
            'username',
            'avatar',
            'first_name',
            'last_name',
        )
        read_only_fields = ('id',)