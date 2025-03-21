from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets

from api.permissions import IsAuthorOrIsAuthenticated
from api.serializers import CommentSerializer, ReviewSerializer
from ratings.models import Review, Title


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthorOrIsAuthenticated, permissions.IsAuthenticatedOrReadOnly
    ]

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
    permission_classes = [
        IsAuthorOrIsAuthenticated, permissions.IsAuthenticatedOrReadOnly
    ]

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
