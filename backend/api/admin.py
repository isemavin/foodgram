from django.contrib import admin
from django.db.models import Count

from api.models import (Tags, Ingredients, User, Recipes,
                        Subscriptions, Favorites, ShoppingCart)


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')


class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscribed_to')


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('author', 'display_ingredients', 'display_tags', 'image',
                    'name', 'text', 'cooking_time', 'pub_date')
    search_fields = ('author', 'name',)
    list_filter = ('tags',)
    readonly_fields = ('total_favorites_count',)

    def total_favorites_count(self, obj):
        return obj.favorites_set.count()
    total_favorites_count.short_description = (
        'Количество добавлений в избранное')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(total_favoritest_count=Count('favorites'))
        return qs

    def display_ingredients(self, obj):
        return ', '.join([i.name for i in obj.ingredients.all()])
    display_ingredients.short_description = 'Ингредиенты'

    def display_tags(self, obj):
        return ', '.join([t.name for t in obj.tags.all()])
    display_tags.short_description = 'Теги'


admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
