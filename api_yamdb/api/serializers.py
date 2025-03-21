from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from ratings.models import Category, Comment, Genre, Review, Title, User


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'



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
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        fields = '__all__'
        model = Review
        # validators = [
        #     serializers.UniqueTogetherValidator(
        #         queryset=Review.objects.all(),
        #         fields=('author', 'title')
        #     )
        # ]

    # def validate_title(self, title):
    #     # title_reviews = title.reviews.all()
    #     # reviews_authors = [review.author for review in title_reviews]
    #     # if self.context['request'].user in reviews_authors:
    #     if Review.objects.filter(
    #         title=title,
    #         author=self.context['request'].user
    #     ).exists():
    #         raise serializers.ValidationError(
    #             'You are not allowed to add more than one review per title!')
    #     return title


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='text'
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = '__all__'
