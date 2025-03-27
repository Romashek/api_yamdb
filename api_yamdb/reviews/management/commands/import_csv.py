import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


def category_load(row):
    Category.objects.update_or_create(
        id=row['id'],
        name=row['name'],
        slug=row['slug']
    )


def comment_load(row):
    review = Review.objects.get(id=row['review_id'])
    author = User.objects.get(id=row['author'])
    Comment.objects.update_or_create(
        id=row['id'],
        review=review,
        text=row['text'],
        author=author,
        pub_date=row['pub_date']
    )


def genre_load(row):
    Genre.objects.update_or_create(
        id=row['id'],
        name=row['name'],
        slug=row['slug']
    )


def genre_title_load(row):
    title = Title.objects.get(id=row['title_id'])
    genre = Genre.objects.get(id=row['genre_id'])
    GenreTitle.objects.update_or_create(
        id=row['id'],
        title=title,
        genre=genre
    )


def review_load(row):
    title = Title.objects.get(id=row['title_id'])
    author = User.objects.get(id=row['author'])
    Review.objects.update_or_create(
        id=row['id'],
        title=title,
        text=row['text'],
        author=author,
        score=row['score'],
        pub_date=row['pub_date']
    )


def title_load(row):
    category = Category.objects.get(id=row['category'])
    Title.objects.update_or_create(
        id=row['id'],
        name=row['name'],
        year=row['year'],
        category=category
    )


def users_load(row):
    User.objects.update_or_create(
        id=row['id'],
        username=row['username'],
        email=row['email'],
        role=row['role'],
        bio=row['bio'],
        first_name=row['first_name'],
        last_name=row['last_name'],
    )


action = {
    'category.csv': category_load,
    'genre.csv': genre_load,
    'titles.csv': title_load,
    'users.csv': users_load,
    'review.csv': review_load,
    'comments.csv': comment_load,
    'genre_title.csv': genre_title_load
}


class Command(BaseCommand):
    help = 'Import data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):

        for filename in action.keys():
            try:
                with open(os.path.join(settings.BASE_DIR, 'static/data/')
                          + filename, mode='r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        try:
                            action[filename](row)
                        except Exception as e:
                            return self.stdout.write(
                                self.style.ERROR
                                (f'Error importing row {row}: {e}'))
                self.stdout.write(self.style.SUCCESS
                                  ('Data imported successfully'))
            except FileNotFoundError:
                return self.stdout.write(self.style.ERROR
                                         (f'File {filename} not found'))
            except Exception as e:
                return self.stdout.write(self.style.ERROR
                                         (f'Error importing data: {e}'))
