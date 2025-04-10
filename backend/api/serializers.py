from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Tags, Ingredients, Recipes, Favorites,
                            ShoppingCart, RecipeIngredient)
from users.serializers import UserSerializer


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipesSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(use_url='recipe_images', required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = ['id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author',
                  'is_favorited', 'is_in_shopping_cart']

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredient__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorites.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def validate_image(self, image):
        if not image:
            raise ValidationError('Поле image не может быть пустым.')
        return image

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise ValidationError('Список ингредиентов не может быть пустым.')
        for ingredient in ingredients:
            if not Ingredients.objects.filter(id=ingredient['id']).exists():
                raise ValidationError('Ингредиента с таким id не существует.')
            if ingredient['id'] in ingredients_list:
                raise ValidationError(
                    'Повторение ингредиента в одном рецепте недопустимо.')
            ingredients_list.append(ingredient['id'])
            if ingredient['amount'] < 1:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0.')
        return ingredients

    def validate_tags(self, tags):
        tags_list = []
        if not tags:
            raise ValidationError('Список тегов не может быть пустым.')
        for tag in tags:
            if not Tags.objects.filter(id=tag).exists():
                raise ValidationError('Тега с таким id не существует.')
            if tag in tags_list:
                raise ValidationError(
                    'Повторение тега в одном рецепте недопустимо.')
            tags_list.append(tag)
        return tags

    def create_ingredients(self, ingredients, recipe):
        self.validate_ingredients(ingredients)
        for ingredient in ingredients:
            ingredient_obj = Ingredients.objects.get(id=ingredient['id'])
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient_obj,
                                            amount=ingredient['amount'])

    def create(self, validated_data):
        tags_data = self.initial_data.get('tags')
        ingredients_data = self.initial_data.get('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        self.create_ingredients(ingredients=ingredients_data, recipe=recipe)
        self.validate_tags(tags_data)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        self.validate_tags(tags)
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.save()
        return instance
