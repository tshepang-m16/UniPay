from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import BudgetEntry, Donation, SavingGoal, Transaction, UserProfile


class StyledDateInput(forms.DateInput):
    input_type = "date"


class StyledDateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            "country",
            "quantity",
            "frequency",
            "message",
            "name",
            "email",
        ]
        widgets = {
            "country": forms.Select(attrs={"class": "field"}),
            "quantity": forms.NumberInput(attrs={"class": "field", "min": 1}),
            "frequency": forms.Select(attrs={"class": "field"}),
            "message": forms.TextInput(attrs={"class": "field", "placeholder": "With love"}),
            "name": forms.TextInput(attrs={"class": "field"}),
            "email": forms.EmailInput(attrs={"class": "field"}),
        }


class BudgetEntryForm(forms.ModelForm):
    class Meta:
        model = BudgetEntry
        fields = ["category", "planned_amount", "actual_amount", "month"]
        widgets = {
            "category": forms.TextInput(attrs={"class": "field"}),
            "planned_amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "actual_amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "month": StyledDateInput(attrs={"class": "field"}),
        }


class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ["name", "target_amount", "current_amount", "due_date", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field"}),
            "target_amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "current_amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "due_date": StyledDateInput(attrs={"class": "field"}),
            "status": forms.Select(attrs={"class": "field"}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["description", "amount", "currency", "kind", "category", "occurred_at"]
        widgets = {
            "description": forms.TextInput(attrs={"class": "field"}),
            "amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "currency": forms.TextInput(attrs={"class": "field", "maxlength": 6}),
            "kind": forms.Select(attrs={"class": "field"}),
            "category": forms.TextInput(attrs={"class": "field"}),
            "occurred_at": StyledDateTimeInput(attrs={"class": "field"}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "membership_level",
            "preferred_currency",
            "country",
            "city",
            "address",
            "postal_code",
            "phone_number",
            "language",
        ]
        widgets = {
            field: forms.TextInput(attrs={"class": "field"})
            for field in fields
        }
        widgets.update({
            "membership_level": forms.TextInput(attrs={"class": "field"}),
            "preferred_currency": forms.TextInput(attrs={"class": "field", "maxlength": 6}),
            "language": forms.TextInput(attrs={"class": "field"}),
        })


class StyledAuthenticationForm(AuthenticationForm):
    """Wrap Django's auth form so templates can use a consistent CSS class."""

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "field"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "field"}))
