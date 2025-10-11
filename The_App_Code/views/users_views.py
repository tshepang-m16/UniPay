from django.shortcuts import render
from ..services import users as users_service


def users_view(request):
    """
    Display user statistics and categories.
    """
    context = {
        "total_users": users_service.total_users(),
        "membership_breakdown": users_service.category_breakdown(),
        "active_page": "users",
    }
    return render(request, "users.html", context)
