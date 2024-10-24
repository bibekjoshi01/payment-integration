from django.utils.translation import gettext_lazy as _

# General Messages
LOGIN_SUCCESS = _("You have successfully logged in.")

USER_ERRORS = {
    "USERNAME_EXISTS": _("This username is already taken."),
    "EMAIL_EXISTS": _("An account with this email address already exists."),
    "PHONE_EXISTS": _("A user with this phone number already exists."),
    "MISSING_ROLES": _("Please select at least one user group."),
}


# VERIFICATION_(
# flake8: noqa
INVALID_CREDENTIALS = _("Invalid Credentials.")
INVALID_PASSWORD = _("Incorrect password. Please try again.")
ACCOUNT_DISABLED = _(
    "Your account has been disabled. Please contact support for assistance."
)

ACCOUNT_VERIFIED = _("Your Account Verified Successfully.")
ACCOUNT_NOT_FOUND = _("Account with email {email} do not exists.")

PASSWORD_CHANGED = _("Password changed successfully.")
OLD_PASSWORD_INCORRECT = _("Incorrect old password.")
PASSWORDS_NOT_MATCH = _("New password and confirm password do not match.")
SAME_OLD_NEW_PASSWORD = _("New password must be different from old password.")
