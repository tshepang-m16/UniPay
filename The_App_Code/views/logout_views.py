from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout


def logout_view(request):
    """
    Handle logout action or show confirmation page.
    """
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been signed out.")
        return redirect("login")

    return render(request, "logout.html", {"active_page": "logout"})
