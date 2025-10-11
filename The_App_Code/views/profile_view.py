from django.shortcuts import render, redirect
from django.contrib import messages
from ..services import profile as profile_service


def profile_view(request):
    """
    Display and update user profile.
    """
    if not request.user.is_authenticated:
        messages.info(request, "Please sign in to manage your profile.")
        return redirect("login")

    context = profile_service.build_context(request.user)

    if request.method == "POST":
        success, form = profile_service.handle_post(request, request.user)
        if success:
            messages.success(request, "Profile updated.")
            return redirect("profile")
        context["form"] = form

    context["active_page"] = "profile"
    return render(request, "profile.html", context)
