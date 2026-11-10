
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def librarian_required(view_func):

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        try:
            member = request.user.profile.member
        except Exception:
            raise PermissionDenied(
                'Your account is not linked to a library membership.'
            )

        if member.member_type != 'LIBRARIAN':
            raise PermissionDenied(
                'Only librarians can access this operation.'
            )

        if member.membership_status != 'ACTIVE':
            raise PermissionDenied(
                'Your library membership is not active.'
            )

        return view_func(request, *args, **kwargs)

    return wrapper
