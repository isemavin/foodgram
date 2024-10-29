from djoser.views import UserViewSet as BaseUserViewSet

from api.models import User
from api.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer