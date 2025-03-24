from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


class User(models.Model):
    USER_ROLE_CHOICES = [
    ('user', 'User'),
    ('admin', 'Admin'),
    ('moderator', 'Moderator'),
    ]
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, max_length=254)
    role = models.SlugField(max_length=50,
                            choices=USER_ROLE_CHOICES, default='user')
    bio = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True,  max_length=50)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Comments(models.Model):
    review = models.ForeignKey(
        'Review', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментрий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Genre_title(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='titles',
        blank=True,
        null=True
    )
    genre = models.ForeignKey(
        'Genre',
        on_delete=models.CASCADE,
        related_name='genres',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведения'

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField('Оценка', validators=[MinValueValidator(1),
                                                      MaxValueValidator(10)])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(validators=[MaxValueValidator(timezone.now().year)])
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
