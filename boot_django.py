import os

import django
from django.conf import settings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "keyring"))


def boot_django():
    settings.configure(
        BASE_DIR=BASE_DIR,
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
            }
        },
        INSTALLED_APPS=("keyring",),
        TIME_ZONE="UTC",
        USE_TZ=True,
        KEYRINGPY_KEYS={
            "1": "oocx3pBP1y3TtPTjQubSu42c0YorKQ6E/Y+8tfoG/lY=",
            "2": "79tjxNIW55SldzXhn6M1kqDrZVeVXoGWODuiCgZRIBg=",
        },
        KEYRINGPY_SALT = "salt_and_peepers"
    )

    django.setup()
