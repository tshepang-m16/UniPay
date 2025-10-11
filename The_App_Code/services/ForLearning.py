from __future__ import annotations

from collections import Counter
from typing import Iterable

from django.db.models import Count

from ..models import LearningResource

CATEGORY_LABELS = dict(LearningResource.CATEGORY_CHOICES)


def list_resources(category: str | None = None):
    qs = LearningResource.objects.all()
    if category and category != "all":
        qs = qs.filter(category=category)
    return qs


def category_counts():
    qs = LearningResource.objects.values("category").annotate(total=Count("id"))
    data = {row["category"]: row["total"] for row in qs}
    results = []
    for key, label in CATEGORY_LABELS.items():
        results.append({
            "key": key,
            "label": label,
            "count": data.get(key, 0),
        })
    return results
