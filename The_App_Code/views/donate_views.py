from django.shortcuts import render, redirect
from django.contrib import messages
from ..services import donate as donate_service


def donate_view(request):
    """
    Handle sanitary pad donation pledges.
    """
    success, extras = donate_service.handle_post(request, request.user)
    if success:
        messages.success(request, "Thank you for your donation!")
        return redirect("donate")

    context = donate_service.build_context(request.user)
    context.update(extras)
    context["active_page"] = "donate"
    return render(request, "donate.html", context)
