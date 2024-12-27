from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
import shortuuid

from recipes.models import (Tags, Ingredients, Recipes, ShoppingCart,
                            Favorites, RecipeIngredient)
from api.permissions import IsAuthenticatedOrReadOnly
from api.serializers import (TagsSerializer, IngredientsSerializer,
                             RecipesSerializer)
from users.serializers import ShortRecipeSerializer
from api.filters import IngredientFilter, RecipeFilter


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
        try:
            ShoppingCart.objects.get(user=user)
        except ShoppingCart.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=user).values(
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
