from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework import status
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from users.models import User, Subscriptions
from recipes.models import Recipes


user = get_user_model()


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ['id', 'name', 'image', 'cooking_time']


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True, allow_null=True)

    class Meta:
        model = user
        fields = (
            'id',
            'email',
            'username',
            'avatar',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = ('id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            subscriber=user, subscribed_to=obj).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.avatar:
            representation['avatar'] = instance.avatar.url
        else:
            representation['avatar'] = ''
        return representation


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = user
        fields = (
            'id',
            'email',
            'username',
            'avatar',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            subscriber=user, subscribed_to=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = obj.recipes.all()[:int(limit)]
        else:
            recipes = obj.recipes.all()
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def validate(self, data):
        subscriber = self.context['request'].user
        subscribed_to = self.instance

        if subscriber == subscribed_to:
            raise ValidationError(
                'Вы не можете подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )

        if Subscriptions.objects.filter(
            subscriber=subscriber,
            subscribed_to=subscribed_to
        ).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(use_url='avatar', required=True)

    class Meta:
        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)
        if avatar:
            instance.avatar = avatar
            instance.save()
        return super().update(instance, validated_data)
