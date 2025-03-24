import uuid
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from django.contrib.auth.tokens import default_token_generator
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from .serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleSerializer, RegisterSerializer,
                             GetTokenSerializer, UserAdminSerializer)
from ratings.models import Category, Genre, Review, Title, User
from .permissions import AuthorOrReadOnly, permissions



def get_confirmation_code(user):
    try:
        confirmation_code = str(uuid.uuid4()).split("-")[0]
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            'Код подтверждения',
            f'Ваш код для подтверждения: {user.confirmation_code}',
            settings.ADMIN_EMAIL,
            [user.email]
        )
    except Exception as e:
        raise ValidationError(f"Ошибка при отправке кода подтверждения: {e}")


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
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'



class RegisterViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def signup(self, request):
        user = User.objects.filter(**request.data)
        if user.exists():
            get_confirmation_code(user)
            return Response(request.data, status=status.HTTP_200_OK)

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = User.objects.filter(**serializer.data)
            get_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def token(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=serializer.data['username'])
        if serializer.data['confirmation_code'] == user.confirmation_code:
            refresh = RefreshToken.for_user(user)
            return Response(
                {'token': str(refresh.access_token)},
                status=status.HTTP_200_OK
            )
        return Response(
            'Проверьте правильность указанных для получения токена данных.',
            status=status.HTTP_400_BAD_REQUEST
        )


# Попытка реализовать регистрацию на функциях а не классах
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    token = default_token_generator.make_token(user)
    send_mail(
        subject='Registration',
        message=f'Your token: {token}',
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data)
