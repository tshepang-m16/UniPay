
#Dashboard.py service
from __future__ import annotations
from decimal import Decimal
from typing import Dict, Tuple

from django.db.models import Q, Sum
from django.utils import timezone

from ..forms import SavingGoalForm, TransactionForm
from ..models import Donation, SavingGoal, Transaction


def _as_decimal(value) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value or 0)


def handle_post(request, user) -> Tuple[bool, Dict[str, object]]:
    """Create dashboard items from submitted forms. Returns (success, context extras)."""

    # ⛔ Prevent crash: ignore POSTs from guests
    if not user.is_authenticated or request.method != "POST":
        return False, {}

    form_type = request.POST.get("form_type")
    extras: Dict[str, object] = {}

    if form_type == "transaction":
        transaction_form = TransactionForm(request.POST, prefix="transaction")
        if transaction_form.is_valid():
            transaction = transaction_form.save(commit=False)
            transaction.user = user
            transaction.save()
            extras["transaction_form"] = TransactionForm(prefix="transaction")
            return True, extras
        extras["transaction_form"] = transaction_form
        extras.setdefault("goal_form", SavingGoalForm(prefix="goal"))
        return False, extras

    if form_type == "goal":
        goal_form = SavingGoalForm(request.POST, prefix="goal")
        if goal_form.is_valid():
            goal = goal_form.save(commit=False)
            goal.user = user
            goal.save()
            extras["goal_form"] = SavingGoalForm(prefix="goal")
            return True, extras
        extras["goal_form"] = goal_form
        extras.setdefault("transaction_form", TransactionForm(prefix="transaction"))
        return False, extras

    return False, {}


def build_context(user, *, overrides: Dict[str, object] | None = None) -> Dict[str, object]:
    """Prepare dashboard metrics for the requested user, safe for guests."""
    overrides = overrides or {}
    now = timezone.now()

    if user.is_authenticated:
        tx_qs = Transaction.objects.filter(user=user)
        goal_qs = SavingGoal.objects.filter(user=user)
        donation_qs = Donation.objects.filter(Q(donor=user) | Q(email=user.email))
    else:
        # ✅ Empty querysets for guests
        tx_qs = Transaction.objects.none()
        goal_qs = SavingGoal.objects.none()
        donation_qs = Donation.objects.all()

    totals = tx_qs.aggregate(
        incoming=Sum("amount", filter=Q(kind=Transaction.INCOMING)),
        outgoing=Sum("amount", filter=Q(kind=Transaction.OUTGOING)),
    )

    incoming = _as_decimal(totals.get("incoming"))
    outgoing = _as_decimal(totals.get("outgoing"))

    goals = []
    for goal in goal_qs:
        goals.append({
            "name": goal.name,
            "target": goal.target_amount,
            "current": goal.current_amount,
            "percent": getattr(goal, "progress_percent", lambda: 0)(),
            "status": getattr(goal, "get_status_display", lambda: "N/A")(),
            "due_date": goal.due_date,
        })

    donation_stats = donation_qs.aggregate(total_packs=Sum("quantity"))

    context = {
        "now": now,
        "recent_transactions": tx_qs.select_related("user")[:5],
        "goals": goals,
        "incoming_total": incoming,
        "outgoing_total": outgoing,
        "net_flow": incoming - outgoing,
        "donation_total_packs": donation_stats.get("total_packs") or 0,
        "transaction_form": overrides.get("transaction_form") or TransactionForm(prefix="transaction"),
        "goal_form": overrides.get("goal_form") or SavingGoalForm(prefix="goal"),
    }

    # 👇 Add banner flag for guests
    if not user.is_authenticated:
        context["anon_notice"] = True

    context.update(overrides)
    return context
