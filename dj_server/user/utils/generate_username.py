import secrets
import string

from ..models import User


def generate_unique_user_username(user_type: str):
    type_temp = user_type
    if type_temp == "system_user":
        title = "SU"
    elif type_temp == "website_user":
        title = "WU"
    else:
        title = "NA"

    """Generate a unique username of 15 characters long."""
    chars = string.digits
    # Generate a random string of 10 characters long
    extra = "".join(secrets.choice(chars) for _ in range(10))
    username = f"{title}-{extra[5:]}-{extra[:5]}"

    if User.objects.filter(username=username).exists():
        generate_unique_user_username(user_type)  # Added user_type argument
    return username
