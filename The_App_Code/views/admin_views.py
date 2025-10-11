from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.models import User
from decimal import Decimal

from ..models import UserProfile, MoneyTransfer, AdminNotification


@login_required
def admin_dashboard(request):
    """Administrator dashboard for managing users and transfers."""
    # Check if user is admin
    try:
        profile = request.user.profile
        if not profile.is_admin():
            messages.error(request, "Access denied. Administrator privileges required.")
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    # Get admin metrics
    total_users = User.objects.count()
    active_transfers = MoneyTransfer.objects.filter(status=MoneyTransfer.PENDING).count()
    total_earnings = MoneyTransfer.objects.filter(
        status=MoneyTransfer.COMPLETED
    ).aggregate(total=Sum('service_fee'))['total'] or Decimal('0')
    
    completed_transfers = MoneyTransfer.objects.filter(status=MoneyTransfer.COMPLETED).count()
    total_transfers = MoneyTransfer.objects.count()
    success_rate = (completed_transfers / total_transfers * 100) if total_transfers > 0 else 0
    
    # Get recent data
    recent_transfers = MoneyTransfer.objects.select_related('sender', 'recipient').order_by('-created_at')[:10]
    user_profiles = UserProfile.objects.select_related('user').order_by('-created_at')[:15]
    
    context = {
        'total_users': total_users,
        'active_transfers': active_transfers,
        'total_earnings': total_earnings,
        'success_rate': success_rate,
        'potential_earnings': total_earnings * Decimal('2'),
        'recent_transfers': recent_transfers,
        'user_profiles': user_profiles,
    }
    
    return render(request, 'admin_dashboard.html', context)