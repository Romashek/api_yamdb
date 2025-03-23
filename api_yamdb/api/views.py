from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from .utils import generate_token
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from ratings.models import Category, Genre, Title, CustomUser
from .serializers import (TitleSerializer, GenreSerializer, CategorySerializer)
from .permissions import AuthorOrReadOnly, permissions


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = TitleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = GenreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (
        permissions.IsAuthenticated,
        AuthorOrReadOnly
    )


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        token = generate_token()

        user = CustomUser.objects.create_user(username=email, email=email,
                                              password=password)
        user.email_verified = False
        user.save()

        # Отправка письма с подтверждением
        subject = 'Подтвердите ваш e-mail'
        message = (f'Для подтверждения перейдитепо ссылке:'
                   f'http://вашсайт.com/verify-email/{token}/')
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        return redirect('waiting_for_verification')
    return render(request, 'register.html')


def verify_email(request, token):
    user = get_object_or_404(CustomUser, email_verification_token=token)
    user.email_verified = True
    user.save()
    return render(request, 'Ваш e-mail успешно подтвержден!')
