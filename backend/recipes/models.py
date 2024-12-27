from django.db import models
from django.core.validators import MinValueValidator

from api.constants import (TAGS_SLUG, TAGS_NAME, RECIPES_NAME,
                           SCORE_MIN_VALUE_VALIDATOR, INGREDIENTS_NAME,
                           INGREDIENTS_UNIT, AMOUNT_VALIDATOR)
from users.models import User


class Tags(models.Model):
    name = models.CharField(max_length=TAGS_NAME, unique=True,
                            verbose_name='Название тега')
    slug = models.SlugField(max_length=TAGS_SLUG, unique=True,
                            verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(max_length=INGREDIENTS_NAME,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=INGREDIENTS_UNIT,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_neme_measurement_unit')
        ]

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredient',
        verbose_name='Список ингредиентов')
    tags = models.ManyToManyField(Tags, verbose_name='Теги')
    image = models.ImageField(
        upload_to='recipe_images/',
        blank=True,
        null=True)
    name = models.CharField(max_length=RECIPES_NAME,
                            verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(SCORE_MIN_VALUE_VALIDATOR)],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(AMOUNT_VALIDATOR)],)

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_recipe_ingredient')
        ]

    def __str__(self):
        return self.ingredient.name


class BaseFavoriteOrShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_recipe')
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в {self._meta.verbose_name}'


class Favorites(BaseFavoriteOrShoppingCart):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(BaseFavoriteOrShoppingCart):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
