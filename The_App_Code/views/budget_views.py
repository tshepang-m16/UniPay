from django.shortcuts import render, redirect
from django.contrib import messages
from ..services import budget as budget_service


def budget_view(request):
    """
    Display and update budget entries.
    """
    success, extras = budget_service.handle_post(request, request.user)
    if success:
        messages.success(request, "Budget entry saved.")
        return redirect("budget")

    context = budget_service.build_context(
        request.user,
        month=request.GET.get("month"),
    )
    context.update(extras)
    context["active_page"] = "budget"
    return render(request, "budget.html", context)
