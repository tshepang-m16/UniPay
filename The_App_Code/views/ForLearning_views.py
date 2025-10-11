from django.shortcuts import render
from ..services import ForLearning as learning_service


def learning_view(request):
    """
    Display all financial literacy resources.
    """
    category = request.GET.get("category")
    resources = learning_service.list_resources(category)
    counts = learning_service.category_counts()

    context = {
        "resources": resources,
        "category_counts": counts,
        "selected_category": category or "all",
        "active_page": "learning",
    }
    return render(request, "ForLearning.html", context)
