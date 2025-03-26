from rest_framework import serializers
import re
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueValidator
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title, User


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'category',
            'genre',
        )
        model = Title


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context.get('request').user
        title = get_object_or_404(Title, id=title_id)
        if (title.reviews.filter(author=author).exists()
           and self.context.get('request').method != 'PATCH'):
            raise serializers.ValidationError(
                'Можно оставлять только один отзыв!'
            )
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='text'
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для эндпоинта 'users/me/' для любого авторизов. пользователя.
    [GET] персональные данные пользователя.
    [POST] заполнение полей 'first_name', 'last_name' и 'bio'.
    """

    role = serializers.StringRelatedField(read_only=True)
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(max_length=254, read_only=True)

    class Meta:
        model = User
        ordering = ['id']
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        read_only_fields = ('role',)


class UserAdminSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для эндпоинта 'users/' для пользователя с ролью 'admin'.
    [GET] получение списка пользователей.
    [POST] регистрация нового пользователя.
    [GET, PATCH, DELETE] работа с пользователем по username.
    """
    class Meta:
        model = User
        ordering = ['id']
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def username_validator(self, value):
        matched_symbols = re.sub(r"[\w.@+-]", "", value)
        if value == 'me':
            raise serializers.ValidationError(
                {"username": ["Вы не можете использоват этот username!"]}
            )
        if value in matched_symbols:
            raise serializers.ValidationError(
                'Некорректные символы в username'
            )
        return value


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if self.initial_data.get('username') == 'me':
            raise serializers.ValidationError(
                {"username": ["Вы не можете использоват этот username!"]}
            )
        return data


class GetTokenSerializer(serializers.Serializer):
    username = serializers.SlugField(
        max_length=150, required=True
    )
    confirmation_code = serializers.SlugField(
        required=True, max_length=254
    )

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
