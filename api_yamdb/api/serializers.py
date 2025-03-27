import re

from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from django.conf import settings
from reviews.models import Category, Comment, Genre, Review, Title, User


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

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if title.reviews.filter(author=author).exists():
                raise ValidationError('Можно оставлять только один отзыв!')
        return data

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для эндпоинта 'users/me/' для любого
    авторизованного пользователя.
    """

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value == settings.ME_URL:
            raise serializers.ValidationError(
                {"username": ["Вы не можете использоват этот username!"]}
            )
        if not bool(re.match(settings.VALID_CHARACTERS_USERNAME, value)):
            raise serializers.ValidationError(
                'Некорректные символы в username'
            )
        return value


class UserAdminSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для эндпоинта 'users/' для пользователя с ролью 'admin'.
    """

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_username(self, value):
        if value == settings.ME_URL:
            raise serializers.ValidationError(
                {"username": ["Вы не можете использоват этот username!"]}
            )
        if not bool(re.match(settings.VALID_CHARACTERS_USERNAME, value)):
            raise serializers.ValidationError(
                'Некорректные символы в username'
            )
        return value


class RegisterSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=settings.MAX_LENGTH_USERNAME,
        regex=settings.VALID_CHARACTERS_USERNAME,
        required=True
    )
    email = serializers.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                {"username": ["Вы не можете использоват этот username!"]}
            )
        return data

    def create(self, validated_data):
        try:
            user, _ = User.objects.get_or_create(**validated_data)
        except IntegrityError:
            raise ValidationError(
                'Error email or username.',
            )
        return user


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.MAX_LENGTH_USERNAME, required=True
    )
    confirmation_code = serializers.CharField(
        required=True
    )


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(
        read_only=True,
        default=5
    )

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title

# То что в сети нашел, но я не разобрался как это работает
    # def get_rating(self, obj):
    #     reviews = Review.objects.filter(title=obj)
    #     if reviews:
    #         ratings_sum = sum(review.score for review in reviews)
    #         return round(ratings_sum / len(reviews))
    #     return None
