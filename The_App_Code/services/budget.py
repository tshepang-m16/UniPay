from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Dict, Tuple

from django.db.models import Sum

from ..forms import BudgetEntryForm
from ..models import BudgetEntry, first_day_of_current_month


def _parse_month(value: str | None) -> date:
    if not value:
        return first_day_of_current_month()
    try:
        year, month = value.split("-")
        return date(int(year), int(month), 1)
    except ValueError:
        return first_day_of_current_month()


def handle_post(request, user) -> Tuple[bool, Dict[str, object]]:
    if not request.user.is_authenticated or request.method != "POST":
        return False, {"form": BudgetEntryForm(prefix="budget")}

    form = BudgetEntryForm(request.POST, prefix="budget")
    if form.is_valid():
        entry, _ = BudgetEntry.objects.update_or_create(
            user=user,
            category=form.cleaned_data["category"],
            month=form.cleaned_data["month"],
            defaults={
                "planned_amount": form.cleaned_data["planned_amount"],
                "actual_amount": form.cleaned_data["actual_amount"],
            },
        )
        return True, {"form": BudgetEntryForm(prefix="budget")}

    return False, {"form": form}


def build_context(user, *, month: str | None = None):
    target_month = _parse_month(month)

    if user.is_authenticated:
        qs = BudgetEntry.objects.filter(user=user, month=target_month)
    else:
        qs = BudgetEntry.objects.none()

    totals = qs.aggregate(
        planned_total=Sum("planned_amount"),
        actual_total=Sum("actual_amount"),
    )

    planned = Decimal(totals.get("planned_total") or 0)
    actual = Decimal(totals.get("actual_total") or 0)

    return {
        "form": BudgetEntryForm(prefix="budget"),
        "month": target_month,
        "entries": qs,
        "planned_total": planned,
        "actual_total": actual,
        "variance_total": planned - actual,
    }
