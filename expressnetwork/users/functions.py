from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from users import models


def get_profile_by_hub(user: models.User):
    return models.Profile.objects.filter(user=user).first()

def get_hashed_password(allowed_chars: str) -> tuple:
    password_str = get_random_string(length=10, allowed_chars=allowed_chars)
    return password_str, make_password(password_str)


