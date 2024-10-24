import secrets
import string


def generate_strong_password():
    # Define the character sets for generating the password
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    digits = string.digits
    special_characters = string.punctuation

    # Combine all character sets
    all_characters = uppercase_letters + lowercase_letters + digits + special_characters

    # Generate a strong password of 8 characters using secrets module
    return "".join(secrets.choice(all_characters) for _ in range(8))
