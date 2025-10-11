from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from ..services import login as login_service


def login_view(request):
    """
    Render the login page and authenticate user.
    """
    success, form = login_service.handle_request(request)
    if success:
        messages.success(request, "Welcome back!")
        return redirect("dashboard")

    context = login_service.build_context(form)
    context["active_page"] = "login"
    return render(request, "login.html", context)
