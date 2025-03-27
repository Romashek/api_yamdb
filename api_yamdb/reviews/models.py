from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings


from reviews.constants import NUMBER_OF_CHAR


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
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True
    )
    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True
    )
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=50, choices=ROLES, default=USER)
    confirmation_code = models.SlugField(null=True, blank=True)

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class Category(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_TITLE)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_TITLE)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


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
        return f'{self.title} - {self.genre}'


class Title(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_TITLE)
    year = models.SmallIntegerField(
        validators=[MaxValueValidator(timezone.now().year)]
    )
    genre = models.ManyToManyField(
        Genre,
    )
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name="reviews"
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name="reviews"
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text[:NUMBER_OF_CHAR]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        default_related_name = 'comments'
        ordering = ('-pub_date',)
        verbose_name = 'Комментрий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (f'{self.text[:NUMBER_OF_CHAR]}, '
                f'Отзыв: {self.review[:NUMBER_OF_CHAR]}, '
                f'Автор: {self.author}')
