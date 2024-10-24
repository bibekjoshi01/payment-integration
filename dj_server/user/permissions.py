from rest_framework.permissions import BasePermission


class WebsiteUserBasePermission(BasePermission):
    def has_permission(self, request, view):
        if (
            request.user.is_anonymous
            or request.user.is_archived
            or not request.user.is_active
            or not request.user.is_email_verified
            or not request.user.is_website_user()
        ):
            return False

        return True
