from django.core.exceptions import ValidationError
from django.utils import timezone

from reviews.constants import ME_URL


def validate_year(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Year cannot be greater than the current year ({current_year}).'
        )


def validate_username_contains_me(value):
    if ME_URL != value:
        raise ValidationError(f'Username must contain {ME_URL}.')
