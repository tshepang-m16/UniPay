from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Count

from ..models import UserProfile


def category_breakdown():
    data = UserProfile.objects.values("membership_level").annotate(total=Count("id"))
    return {
        row["membership_level"] or "Uncategorised": row["total"]
        for row in data
    }


def total_users():
    return get_user_model().objects.count()
