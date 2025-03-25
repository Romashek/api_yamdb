from django.shortcuts import get_object_or_404
import uuid
from rest_framework import permissions, viewsets, status
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination

from .serializers import (CategorySerializer, CommentSerializer, GetTokenSerializer,
                             GenreSerializer, ReviewSerializer, RegisterSerializer,
                             TitleSerializer, UserAdminSerializer, UserSerializer)
from ratings.models import Category, Genre, Review, Title, User
from .permissions import IsAdmin, IsAuthorModeratorAdminOrReadOnly, ReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated],
            serializer_class=UserSerializer,
            pagination_class=None)
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    try:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            confirmation_code = str(uuid.uuid4()).split("-")[0]
            user.confirmation_code = confirmation_code
            user.save()

            send_mail(
                'Код подтверждения',
                f'Ваш код для подтверждения: {user.confirmation_code}',
                settings.ADMIN_EMAIL,
                [user.email]
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except KeyError as e:
        return Response({"error": f"Missing key: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = User.objects.get(username=username)
            if user.confirmation_code == confirmation_code:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({"error": "Неверный код подтверждения"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
