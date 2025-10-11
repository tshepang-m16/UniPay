from django.shortcuts import render
from ..services import promotions as promotions_service


def promotions_view(request):
    """
    Display all active promotions and incentives.
    """
    promotions = promotions_service.list_promotions()
    context = {
        "promotions": promotions,
        "active_page": "promotions",
    }
    return render(request, "promotions.html", context)
