from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from api.constants import (TAGS_SLUG, TAGS_NAME, RECIPES_NAME,
                           SCORE_MIN_VALUE_VALIDATOR, INGREDIENTS_NAME,
                           INGREDIENTS_UNIT)


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    avatar = models.ImageField(blank=True, null=True)

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


class Recipes(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.TextField(verbose_name='Список ингредиентов')
    tags = models.ManyToManyField(Tags, verbose_name='Теги')
    image = models.ImageField(blank=True, null=True)
    name = models.CharField(max_length=RECIPES_NAME,
                            verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(SCORE_MIN_VALUE_VALIDATOR)],
        verbose_name='Время приготовления'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


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


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь')
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписки')


class ShoppingCart(models.Model):
    pass