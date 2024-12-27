from django.db.models import Count
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from users.models import (User, Subscriptions)
from users.serializers import (UserSerializer, AvatarSerializer,
                               SubscribeSerializer)
from api.pagination import CustomPageNumberPagination


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(instance=user,
                                    context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['PUT'], permission_classes=[IsAuthenticated])
    def avatar(self, request, *args, **kwargs):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        user = request.user
        current_avatar = user.avatar
        user.avatar = None
        user.save(update_fields=['avatar'])
        if current_avatar:
            current_avatar.delete(save=False)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        subscriber = request.user
        subscribed_to = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            serializer = SubscribeSerializer(subscribed_to, data=request.data,
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscriptions.objects.create(subscriber=subscriber,
                                         subscribed_to=subscribed_to)
            response_data = serializer.data
            response_data['recipes_count'] = subscriber.recipes.count()
            return Response(response_data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                subscription = Subscriptions.objects.get(
                    subscriber=subscriber,
                    subscribed_to=subscribed_to)
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscriptions.DoesNotExist:
                return Response({'detail': 'Подписка не найдена.'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribers__subscriber=user).annotate(
            recipes_count=Count('recipes'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeSerializer(page, many=True,
                                             context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(queryset, many=True,
                                         context={'request': request})
        return Response(serializer.data)

    def get_object(self, id):
        if id == 'me':
            return self.request.user
        else:
            try:
                return self.queryset.get(id=id)
            except (User.DoesNotExist, ValueError):
                raise Http404

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object(kwargs.get('id'))
        serializer = self.get_serializer(instance,
                                         context={'request': request})
        return Response(serializer.data)
