from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
import shortuuid

from api.models import (User, Tags, Ingredients, Recipes, ShoppingCart,
                        Subscriptions, Favorites, RecipeIngredient)
from api.permissions import IsAuthenticatedOrReadOnly
from api.serializers import (UserSerializer, TagsSerializer,
                             IngredientsSerializer, AvatarSerializer,
                             RecipesSerializer, ShortRecipeSerializer,
                             SubscribeSerializer)
from api.pagination import CustomPageNumberPagination
from api.filters import IngredientFilter, RecipeFilter


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user_data = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'avatar': (
                str(request.user.avatar.url) if request.user.avatar else ''),
            'is_subscribed': False,
        }
        return Response(user_data)

    @action(detail=True, methods=['PUT', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            user.avatar = None
            user.save(update_fields=['avatar'])
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        subscriber = request.user
        subscribed_to = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            if subscriber == subscribed_to:
                raise exceptions.ValidationError(
                    'Вы не можете подписаться на самого себя.')
            if Subscriptions.objects.filter(subscriber=subscriber,
                                            subscribed_to=subscribed_to
                                            ).exists():
                raise exceptions.ValidationError(
                    'Вы уже подписаны на этого пользователя.')
            Subscriptions.objects.create(subscriber=subscriber,
                                         subscribed_to=subscribed_to)
            serializer = SubscribeSerializer(instance=subscribed_to,
                                             context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
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
        queryset = User.objects.filter(subscribers__subscriber=user)
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


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_class = IngredientFilter


class RecipesViewSet(ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def add_method(self, request, model, recipe):
        user = self.request.user
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError(
                f'Рецепт уже есть в {model.__name__}')
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_method(self, request, model, recipe):
        user = self.request.user
        try:
            instance = model.objects.get(user=user, recipe=recipe)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({'detail': f'Рецепт не найден в {model.__name__}'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        if request.method == 'POST':
            return self.add_method(request, ShoppingCart, recipe)
        elif request.method == 'DELETE':
            return self.delete_method(request, ShoppingCart, recipe)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        if request.method == 'POST':
            return self.add_method(request, Favorites, recipe)
        elif request.method == 'DELETE':
            return self.delete_method(request, Favorites, recipe)

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request, *args, **kwargs):
        short_uuid = shortuuid.uuid()[:6]
        base_url = 'http://localhost/'
        short_link = f'{base_url}s/{short_uuid}'
        data = {
            'short-link': short_link
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                'ingredient__name',
                'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = 'Cписок покупок:\n\n'
        for ingredient in ingredients:
            shopping_list += '\n'.join([
                f'{ingredient["ingredient__name"]} - {ingredient["amount"]}'
                f'{ingredient["ingredient__measurement_unit"]}\n'
            ])

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
