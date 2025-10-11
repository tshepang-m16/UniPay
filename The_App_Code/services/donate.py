#donate.py
from __future__ import annotations

from django.db.models import Sum

from ..forms import DonationForm
from ..models import Donation


def handle_post(request, user):
    if request.method != "POST":
        return False, {"form": DonationForm(prefix="donation")}

    form = DonationForm(request.POST, prefix="donation")
    if form.is_valid():
        donation = form.save(commit=False)
        if user.is_authenticated:
            donation.donor = user
            if not donation.name:
                donation.name = user.get_full_name() or user.get_username()
            if not donation.email:
                donation.email = user.email or donation.email
        donation.save()
        return True, {"form": DonationForm(prefix="donation")}

    return False, {"form": form}


def build_context(user):
    stats = Donation.objects.aggregate(total_packs=Sum("quantity"))
    donors = Donation.objects.values("email").distinct().count()
    recent = Donation.objects.order_by("-created_at")[:5]

    total_packs = stats.get("total_packs") or 0
    goal = 1600
    percent = 0 if not total_packs else min(int((total_packs / goal) * 100), 100)

    return {
        "form": DonationForm(prefix="donation"),
        "donation_total_packs": total_packs,
        "donor_count": donors,
        "recent_donations": recent,
        "donation_goal_percent": percent,
        "donation_goal_target": goal,
    }
