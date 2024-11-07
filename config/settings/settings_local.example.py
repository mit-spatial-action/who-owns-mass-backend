from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "your_local_database",
        "USER": "your_local_user",
        "PASSWORD": "your_local_password",
        "HOST": "localhost",
        "PORT": 0000,
        "OPTIONS": {
            "sslmode": 'allow'
        },
    }
}
