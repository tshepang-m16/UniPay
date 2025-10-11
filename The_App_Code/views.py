from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
from decimal import Decimal

from .models import (
    UserProfile, Transaction, SavingGoal, Promotion, BudgetEntry, 
    Donation, LearningResource, MoneyTransfer, AdminNotification
)
from .forms import TransactionForm, SavingGoalForm


def render_page(request, template_name, active_page, extra_context=None):
    """Render a template while flagging which page is active in navigation."""
    context = {"active_page": active_page}
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


USER_CATEGORIES = [
    "Students",
    "Working class", 
    "Admin",
    "Superuser",
]



def handle_transaction_form(request):
    """Handle transaction form submission."""
    form = TransactionForm(request.POST)
    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.user = request.user
        transaction.save()
        messages.success(request, "Transaction added successfully!")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    return redirect('dashboard')


def handle_goal_form(request):
    """Handle saving goal form submission."""
    form = SavingGoalForm(request.POST)
    if form.is_valid():
        goal = form.save(commit=False)
        goal.user = request.user
        goal.save()
        messages.success(request, "Goal saved successfully!")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    return redirect('dashboard')


@login_required
def dashboard(request):
    user = request.user
    
    # Handle different form submissions
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        
        if form_type == "send_money":
            return handle_money_transfer(request)
        elif form_type == "transaction":
            return handle_transaction_form(request)
        elif form_type == "goal":
            return handle_goal_form(request)
    
    # Get user's transactions and goals
    transactions = Transaction.objects.filter(user=user).order_by("-occurred_at")[:10]
    goals = SavingGoal.objects.filter(user=user)
    
    # Calculate metrics - handle case where constants don't exist yet
    try:
        incoming_kinds = [Transaction.INCOMING, Transaction.TRANSFER_IN]
        outgoing_kinds = [Transaction.OUTGOING, Transaction.TRANSFER_OUT]
    except AttributeError:
        # Fallback for older Transaction model without transfer constants
        incoming_kinds = ['incoming']
        outgoing_kinds = ['outgoing']
    
    incoming_total = transactions.filter(
        kind__in=incoming_kinds
    ).aggregate(total=Sum("amount"))["total"] or 0
    
    outgoing_total = transactions.filter(
        kind__in=outgoing_kinds
    ).aggregate(total=Sum("amount"))["total"] or 0
    
    net_flow = incoming_total - outgoing_total
    
    # Get donation total
    donation_total_packs = Donation.objects.filter(donor=user).aggregate(
        total=Sum("quantity")
    )["total"] or 0
    
    # Get available recipients (users with phone numbers, excluding current user)
    available_recipients = UserProfile.objects.filter(
        phone_number__isnull=False,
        is_active=True
    ).exclude(user=user).select_related('user')
    
    context = {
        "recent_transactions": transactions,
        "goals": goals,
        "incoming_total": incoming_total,
        "outgoing_total": outgoing_total,
        "net_flow": net_flow,
        "donation_total_packs": donation_total_packs,
        "available_recipients": available_recipients,
        "transaction_form": TransactionForm(),
        "goal_form": SavingGoalForm(),
        "now": timezone.now(),
    }
    
    return render(request, "dashboard.html", context)


def handle_money_transfer(request):
    """Handle money transfer between users."""
    recipient_phone = request.POST.get("recipient_phone")
    amount = request.POST.get("amount")
    currency = request.POST.get("currency", "USD")
    description = request.POST.get("description", "")
    
    try:
        amount = Decimal(amount)
        service_fee = amount * Decimal('0.02')  # 2% fee
        total_amount = amount + service_fee
        
        # Find recipient by phone number
        recipient_profile = get_object_or_404(UserProfile, phone_number=recipient_phone)
        recipient = recipient_profile.user
        
        # Check if user has enough balance (simplified - you may want to implement wallet balance)
        sender_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Create money transfer record
        transfer = MoneyTransfer.objects.create(
            sender=request.user,
            recipient=recipient,
            amount=amount,
            currency=currency,
            service_fee=service_fee,
            total_amount=total_amount,
            description=description,
            reference_number=str(uuid.uuid4())[:8].upper(),
            status=MoneyTransfer.COMPLETED  # Auto-approve for demo
        )
        
        # Create transaction records for both users
        # Handle case where transfer constants don't exist yet
        try:
            sender_kind = Transaction.TRANSFER_OUT
            recipient_kind = Transaction.TRANSFER_IN
        except AttributeError:
            sender_kind = 'outgoing'
            recipient_kind = 'incoming'
            
        Transaction.objects.create(
            user=request.user,
            description=f"Transfer to {recipient.username}: {description}",
            amount=total_amount,  # Include fee in sender's deduction
            currency=currency,
            kind=sender_kind,
            category="Transfer",
        )
        
        Transaction.objects.create(
            user=recipient,
            description=f"Transfer from {request.user.username}: {description}",
            amount=amount,  # Recipient gets amount without fee
            currency=currency,
            kind=recipient_kind,
            category="Transfer",
        )
        
        messages.success(
            request, 
            f"Successfully sent {amount} {currency} to {recipient.username}. "
            f"Reference: {transfer.reference_number}"
        )
        
    except Exception as e:
        messages.error(request, f"Transfer failed: {str(e)}")
    
    return redirect('dashboard')


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
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "send_notification":
            return handle_admin_notification(request)
        elif action == "update_transfer":
            return handle_transfer_update(request)
        elif action == "toggle_user":
            return handle_user_toggle(request)
    
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
        'potential_earnings': total_earnings * Decimal('2'),  # For chart
        'recent_transfers': recent_transfers,
        'user_profiles': user_profiles,
    }
    
    return render(request, 'admin_dashboard.html', context)


def handle_admin_notification(request):
    """Handle sending admin notifications."""
    title = request.POST.get('title')
    message = request.POST.get('message')
    notification_type = request.POST.get('notification_type', 'general')
    is_global = request.POST.get('is_global') == 'on'
    
    notification = AdminNotification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type,
        sent_by=request.user,
        is_global=is_global
    )
    
    if is_global:
        # Add all active users as recipients
        active_users = User.objects.filter(profile__is_active=True)
        notification.recipients.set(active_users)
    
    messages.success(request, f"Notification '{title}' sent successfully.")
    return redirect('admin_dashboard')


def handle_transfer_update(request):
    """Handle transfer status updates."""
    transfer_id = request.POST.get('transfer_id')
    status = request.POST.get('status')
    
    transfer = get_object_or_404(MoneyTransfer, id=transfer_id)
    transfer.status = status
    transfer.save()
    
    messages.success(request, f"Transfer {transfer.reference_number} marked as {status}.")
    return redirect('admin_dashboard')


def handle_user_toggle(request):
    """Handle user activation/deactivation."""
    user_id = request.POST.get('user_id')
    user = get_object_or_404(User, id=user_id)
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.is_active = not profile.is_active
    profile.save()
    
    status = "activated" if profile.is_active else "suspended"
    messages.success(request, f"User {user.username} has been {status}.")
    return redirect('admin_dashboard')


def login_view(request):
    return render_page(request, "login.html", active_page="login")


def logout_view(request):
    return render_page(request, "logout.html", active_page="logout")


def promotions_view(request):
    return render_page(request, "promotions.html", active_page="promotions")


def budget_view(request):
    return render_page(request, "budget.html", active_page="budget")


def donate_view(request):
    return render_page(request, "donate.html", active_page="donate")


def profile_view(request):
    return render_page(request, "profile.html", active_page="profile")


def learning_view(request):
    return render_page(request, "ForLearning.html", active_page="learning")


def users_view(request):
    context = {"user_categories": USER_CATEGORIES}
    return render_page(request, "users.html", active_page="users", extra_context=context)
