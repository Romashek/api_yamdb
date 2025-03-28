from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Category, Comment, Genre, Review, Title, User


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    search_fields = ('review',)
    list_filter = ('review',)


@admin.register(Genre)
class GenreAdmin(BaseAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Review)
class ReviewAdmin(BaseAdmin):
    list_display = ('title', 'text', 'author', 'score')
    search_fields = ('pub_date',)
    list_filter = ('pub_date',)


class TitleGenreInline(admin.TabularInline):
    model = Title.genre.through
    extra = 1


@admin.register(Title)
class TitleAdmin(BaseAdmin):
    list_display = ('name', 'year', 'category', 'display_genres', 'description')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = (TitleGenreInline,)

    def display_genres(self, obj):
        return ', '.join(genre.name for genre in obj.genre.all())
    display_genres.short_description = 'Жанры'


class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'bio')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Additional info'), {'fields': ('role', 'confirmation_code')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'role', 'bio', 'first_name', 'last_name', 'confirmation_code')
    search_fields = ('username', 'role')
    list_filter = ('username',)

admin.site.register(User, CustomUserAdmin)
