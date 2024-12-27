from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from recipes.models import (Tags, Ingredients, Recipes,
                            Favorites, ShoppingCart, RecipeIngredient)
from users.models import User, Subscriptions


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'avatar',
                    'subscribers_count', 'recipes_count')
    search_fields = ('email', 'username')

    @admin.display(description='Количество подписчиков')
    def subscribers_count(self, obj):
        return obj.subscribers.count()

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscribed_to')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('author', 'display_ingredients', 'display_tags', 'image',
                    'name', 'text', 'cooking_time', 'pub_date')
    search_fields = ('author', 'name',)
    list_filter = ('tags',)
    readonly_fields = ('total_favorites_count',)
    inlines = [
        IngredientInLine,
    ]

    @admin.display(description='Количество добавлений в избранное')
    def total_favorites_count(self, obj):
        return obj.favorites_set.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(total_favoritest_count=Count('favorites'))

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        return ', '.join([i.name for i in obj.ingredients.all()])

    @admin.display(description='Теги')
    def display_tags(self, obj):
        return ', '.join([t.name for t in obj.tags.all()])
