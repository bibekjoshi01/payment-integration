class EmailNotSetError(ValueError):
    def __init__(self):
        super().__init__("The given email must be set.")


class IsStaffError(ValueError):
    def __init__(self):
        super().__init__("Superuser must have is_staff=True.")


class IsSuperuserError(ValueError):
    def __init__(self):
        super().__init__("Superuser must have is_superuser=True.")
