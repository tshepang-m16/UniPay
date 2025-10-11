from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from ..models import Promotion


def list_promotions(include_inactive: bool = False):
    today = timezone.now().date()
    qs = Promotion.objects.all()
    if not include_inactive:
        qs = qs.filter(is_active=True)
    qs = qs.filter(
        Q(valid_from__isnull=True) | Q(valid_from__lte=today),
        Q(valid_until__isnull=True) | Q(valid_until__gte=today),
    )
    return qs


def feature_promotion():
    return list_promotions().first()
