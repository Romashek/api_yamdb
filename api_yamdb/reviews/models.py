from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from reviews import constants
from .validators import validate_username_contains_me, validate_year


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    ROLES = [
        (USER, 'user'),
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator')
    ]

    username = models.CharField(
        max_length=constants.MAX_LENGTH_USERNAME,
        unique=True,
        validators=[
            validate_username_contains_me,
            RegexValidator(
                regex=constants.VALID_CHARACTERS_USERNAME,
                message='Имя пользователя должно\
                    соответствовать шаблону.',
                code='invalid_username'
            )
        ],
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=constants.MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name='Электронная почта'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=constants.MAX_LENGTH_ROLE,
        choices=ROLES,
        default=USER,
        verbose_name='Роль'
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class NameSlugModel(models.Model):
    name = models.CharField(max_length=constants.MAX_LENGTH_TITLE)
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name[:constants.NUMBER_OF_CHAR]


class Category(NameSlugModel):
    class Meta(NameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    class Meta(NameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class GenreTitle(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    genre = models.ForeignKey(
        'Genre',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведения'
        default_related_name = 'genres'

    def __str__(self):
        return f'{self.title[:constants.NUMBER_OF_CHAR]} - {self.genre}'


class Title(models.Model):
    name = models.CharField(
        max_length=constants.MAX_LENGTH_TITLE,
        verbose_name='Название'
    )
    year = models.SmallIntegerField(
        validators=[validate_year],
        verbose_name='Год'
    )
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Жанр'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:constants.NUMBER_OF_CHAR]


class TextModel(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(TextModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name="reviews"
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(constants.MIN_SCORE),
                    MaxValueValidator(constants.MAX_SCORE)]
    )

    class Meta(TextModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text[:constants.NUMBER_OF_CHAR]


class Comment(TextModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(TextModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (f'{self.text[:constants.NUMBER_OF_CHAR]}, '
                f'Отзыв: {self.review.text[:constants.NUMBER_OF_CHAR]}, '
                f'Автор: {self.author}')
