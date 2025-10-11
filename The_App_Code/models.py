from django.conf import settings
from django.db import models
from django.contrib.auth.models import User  # Add this import
from django.utils import timezone
from decimal import Decimal


def first_day_of_current_month():
    today = timezone.now().date()
    return today.replace(day=1)


class TimeStampedModel(models.Model):
    """Abstract base model that tracks creation and update timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):
    """Stores additional profile information for a platform user."""

    # User role choices
    STANDARD = "standard"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    ROLE_CHOICES = [
        (STANDARD, "Standard User"),
        (ADMIN, "Administrator"),
        (SUPER_ADMIN, "Super Administrator"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=120, blank=True)
    membership_level = models.CharField(max_length=32, default="Standard")
    preferred_currency = models.CharField(max_length=6, default="USD")
    country = models.CharField(max_length=64, blank=True)
    city = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=12, blank=True)
    phone_number = models.CharField(max_length=32, blank=True, unique=True)
    language = models.CharField(max_length=32, default="English")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=STANDARD)
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f"Profile for {self.user.get_username()}"

    def is_admin(self):
        return self.role in [self.ADMIN, self.SUPER_ADMIN]


class MoneyTransfer(TimeStampedModel):
    """Tracks money transfers between users on the platform."""
    
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
        (CANCELLED, "Cancelled"),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_transfers",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_transfers",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=6, default="USD")
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # amount + fee
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=PENDING)
    reference_number = models.CharField(max_length=32, unique=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.amount} {self.currency}"


class AdminNotification(TimeStampedModel):
    """System notifications sent by administrators."""
    
    GENERAL = "general"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    PROMOTION = "promotion"
    TYPE_CHOICES = [
        (GENERAL, "General"),
        (SECURITY, "Security Alert"),
        (MAINTENANCE, "Maintenance"),
        (PROMOTION, "Promotion"),
    ]

    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=GENERAL)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="received_notifications",
        blank=True,
    )
    is_global = models.BooleanField(default=False)  # Send to all users
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.title} by {self.sent_by.username}"


class Transaction(TimeStampedModel):
    """Represents money moving in or out for a user."""

    INCOMING = "incoming"
    OUTGOING = "outgoing"
    TRANSFER_IN = "transfer_in"  # Received from another user
    TRANSFER_OUT = "transfer_out"  # Sent to another user
    KIND_CHOICES = [
        (INCOMING, "Incoming"),
        (OUTGOING, "Outgoing"),
        (TRANSFER_IN, "Transfer Received"),
        (TRANSFER_OUT, "Transfer Sent"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=6, default="USD")
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=OUTGOING)
    category = models.CharField(max_length=64, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)
    related_transfer = models.ForeignKey(
        'MoneyTransfer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self) -> str:
        direction = "" if self.kind in [self.OUTGOING, self.TRANSFER_OUT] else "+"
        return f"{direction}{self.amount} {self.currency} - {self.description}"


class SavingGoal(TimeStampedModel):
    """Savings or remittance goals the user is tracking."""

    ON_TRACK = "on_track"
    BEHIND = "behind"
    AHEAD = "ahead"
    STATUS_CHOICES = [
        (ON_TRACK, "On Track"),
        (BEHIND, "Behind"),
        (AHEAD, "Ahead"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saving_goals",
    )
    name = models.CharField(max_length=120)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=ON_TRACK)

    class Meta:
        ordering = ["due_date", "name"]

    def progress_percent(self) -> float:
        if not self.target_amount:
            return 0
        return float(min((self.current_amount / self.target_amount) * 100, 100))

    def __str__(self) -> str:
        return f"{self.name} ({self.progress_percent():.0f}%)"


class Promotion(TimeStampedModel):
    """Marketing promotions and incentives surfaced to users."""

    title = models.CharField(max_length=150)
    description = models.TextField()
    badge_text = models.CharField(max_length=20, blank=True)
    reward = models.CharField(max_length=120, blank=True)
    cta_label = models.CharField(max_length=40, default="View details")
    cta_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(default=0)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-is_active", "-priority", "title"]

    def __str__(self) -> str:
        return self.title


class BudgetEntry(TimeStampedModel):
    """Budget allocations per category that a user tracks monthly."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budget_entries",
    )
    category = models.CharField(max_length=80)
    planned_amount = models.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.DateField(default=first_day_of_current_month)

    class Meta:
        ordering = ["-month", "category"]
        unique_together = ("user", "category", "month")

    def variance(self):
        return self.planned_amount - self.actual_amount

    def __str__(self) -> str:
        return f"{self.category} ({self.month:%Y-%m})"


class Donation(TimeStampedModel):
    """Sanitary pad donation pledges captured from the donate page."""

    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    FREQUENCY_CHOICES = [
        (ONE_TIME, "One-time"),
        (MONTHLY, "Monthly"),
        (QUARTERLY, "Quarterly"),
    ]

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    country = models.CharField(max_length=60)
    quantity = models.PositiveIntegerField()
    frequency = models.CharField(max_length=16, choices=FREQUENCY_CHOICES, default=ONE_TIME)
    message = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.quantity} packs"


class LearningResource(TimeStampedModel):
    """Financial education resources surfaced in the learning hub."""

    BUDGETING = "budget"
    REMITTANCE = "remittance"
    BUSINESS = "business"
    SAFETY = "safety"
    CATEGORY_CHOICES = [
        (BUDGETING, "Budgeting"),
        (REMITTANCE, "Smart Remittances"),
        (BUSINESS, "Small Business"),
        (SAFETY, "Safety & Fraud"),
    ]

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    LEVEL_CHOICES = [
        (BEGINNER, "Beginner"),
        (INTERMEDIATE, "Intermediate"),
        (ADVANCED, "Advanced"),
    ]

    ARTICLE = "article"
    TOOLKIT = "toolkit"
    VIDEO = "video"
    RESOURCE_CHOICES = [
        (ARTICLE, "Article"),
        (TOOLKIT, "Toolkit"),
        (VIDEO, "Video"),
    ]

    title = models.CharField(max_length=150)
    summary = models.TextField()
    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES, default=BUDGETING)
    level = models.CharField(max_length=16, choices=LEVEL_CHOICES, default=BEGINNER)
    duration_minutes = models.PositiveIntegerField(default=5)
    resource_type = models.CharField(max_length=16, choices=RESOURCE_CHOICES, default=ARTICLE)
    call_to_action = models.CharField(max_length=40, default="Read Lesson")
    link = models.URLField(blank=True)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self) -> str:
        return self.title


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reset token for {self.user.username}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
