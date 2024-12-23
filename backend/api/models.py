from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

from api.constants import (TAGS_SLUG, TAGS_NAME, RECIPES_NAME,
                           SCORE_MIN_VALUE_VALIDATOR, INGREDIENTS_NAME,
                           INGREDIENTS_UNIT, USER_NAME, AMOUNT_VALIDATOR)


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    first_name = models.CharField(max_length=USER_NAME, blank=False,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=USER_NAME, blank=False,
                                 verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/',
                               blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Tags(models.Model):
    name = models.CharField(max_length=TAGS_NAME, unique=True,
                            verbose_name='Название тега')
    slug = models.SlugField(max_length=TAGS_SLUG, unique=True,
                            verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredients(models.Model):
    name = models.CharField(max_length=INGREDIENTS_NAME,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=INGREDIENTS_UNIT,
                                        verbose_name='Единица измерения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(AMOUNT_VALIDATOR)],)


class Subscriptions(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions')
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'subscribed_to'],
                                    name='unique_subscriptions')
        ]


class Favorites(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]
