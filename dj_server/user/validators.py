from django.conf import settings
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ValidationError


def validate_image(image):
    """
    Validates the size of the image file.

    Parameters:
        - image (django.core.files.uploadedfile.InMemoryUploadedFile):
        - The image file to validate.

    Raises:
        ValidationError: If the size of the image file exceeds the maximum allowed size.

    Notes:
        - The maximum allowed size is specified in settings.MAX_UPLOAD_SIZE.
        - If the size exceeds the limit,
          a ValidationError is raised with an appropriate error message.
    """
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        error_message = f"Max size of file is {f} MB"
        raise ValidationError(error_message)


@deconstructible
class CustomUsernameValidator(validators.RegexValidator):
    regex = r"^[a-zA-Z0-9_-]+$"
    message = _(
        "Enter a valid username. This value may only contain letters, "
        "numbers, hyphens and underscores.",
    )
    flags = 0
