from __future__ import annotations

from django.contrib.auth import login

from ..forms import StyledAuthenticationForm


def handle_request(request):
    form = StyledAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return True, form
    return False, form


def build_context(form):
    return {"form": form}
