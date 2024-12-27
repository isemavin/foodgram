from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from api.constants import (USER_NAME)


class User(AbstractUser):
    username = models.CharField(max_length=USER_NAME,
                                unique=True,
                                validators=[UnicodeUsernameValidator()])
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    first_name = models.CharField(max_length=USER_NAME, blank=False,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=USER_NAME, blank=False,
                                 verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/',
                               blank=True, default='')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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

    def clean(self):
        super().clean()
        if self.subscriber == self.subscribed_to:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def __str__(self):
        return f'{self.subscriber} подписался на {self.subscribed_to}'
