from __future__ import annotations

from typing import Tuple

from ..forms import ProfileForm
from ..models import UserProfile


def ensure_profile(user) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if not profile.display_name:
        profile.display_name = user.get_full_name() or user.get_username()
        profile.save(update_fields=["display_name"])
    return profile


def handle_post(request, user) -> Tuple[bool, ProfileForm]:
    profile = ensure_profile(user)
    form = ProfileForm(request.POST, instance=profile)
    if form.is_valid():
        form.save()
        return True, ProfileForm(instance=profile)
    return False, form


def build_context(user):
    profile = ensure_profile(user)
    form = ProfileForm(instance=profile)
    return {
        "profile": profile,
        "form": form,
    }
