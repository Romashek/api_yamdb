from django.urls import include, path
from rest_framework import routers
from django.contrib.auth import views
from . import views
from .views import (TitleViewSet, ReviewViewSet, CommentViewSet,
                    CategoryViewSet, GenreViewSet, UserViewSet,
                    RegisterViewSet)


v1_router = routers.DefaultRouter()
v1_router.register('titles', TitleViewSet, basename='title')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('register', RegisterViewSet, basename='register')


urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/', include('djoser.urls.jwt')),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
]
