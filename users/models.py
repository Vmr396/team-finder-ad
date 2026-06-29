import random
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import URLValidator
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from PIL import Image, ImageDraw, ImageFont

from .managers import UserManager
from team_finder.constants import (
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    AVATAR_SIZE,
    AVATAR_FONT_SIZE,
    AVATAR_COLORS,
    AVATAR_TEXT_COLOR,
)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        blank=True,
    )
    surname = models.CharField(
        max_length=USER_SURNAME_MAX_LENGTH,
        blank=True,
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
    )
    bio = models.TextField(blank=True)
    github_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
    )
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and not self.avatar:
            self._generate_default_avatar()

    def _generate_default_avatar(self):
        """Генерирует аватар с первой буквой имени на цветном фоне"""
        size = AVATAR_SIZE
        bg_color = random.choice(AVATAR_COLORS)

        img = Image.new('RGB', (size, size), color=bg_color)
        draw = ImageDraw.Draw(img)

        letter = (self.name[0] if self.name else self.email[0]).upper()

        try:
            font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
        except IOError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        self.avatar.save(
            f'avatar_{self.id}.png',
            ContentFile(buffer.read()),
            save=True
        )

    def clean(self):
        super().clean()
        if self.github_url:
            validator = URLValidator()
            validator(self.github_url)
            if 'github.com' not in self.github_url:
                raise ValidationError(
                    {'github_url': 'Ссылка должна вести на GitHub'}
                )
