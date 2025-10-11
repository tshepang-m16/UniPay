from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from ..models import UserProfile


def register_view(request):
    """Handle user registration with profile creation."""
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Profile data
        phone_number = request.POST.get('phone_number')
        country = request.POST.get('country')
        city = request.POST.get('city', '')
        preferred_currency = request.POST.get('preferred_currency', 'USD')
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html')
        
        if phone_number and UserProfile.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered.')
            return render(request, 'register.html')
        
        try:
            # Create user and profile in a transaction
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    display_name=f"{first_name} {last_name}".strip() or username,
                    phone_number=phone_number,
                    country=country,
                    city=city,
                    preferred_currency=preferred_currency,
                    role=UserProfile.STANDARD,
                    is_active=True
                )
                
                # Log the user in
                user = authenticate(username=username, password=password1)
                if user:
                    login(request, user)
                    messages.success(request, f'Welcome to Remittence, {user.first_name or user.username}!')
                    return redirect('dashboard')
                    
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'register.html')
    
    # Countries for dropdown
    countries = [
        'United States', 'Canada', 'United Kingdom', 'Germany', 'France',
        'Kenya', 'Ghana', 'Nigeria', 'South Africa', 'Uganda',
        'Tanzania', 'Rwanda', 'Ethiopia', 'Senegal', 'Morocco',
        'Australia', 'India', 'Philippines', 'Other'
    ]
    
    currencies = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('KES', 'Kenyan Shilling (KSh)'),
        ('GHS', 'Ghanaian Cedi (₵)'),
        ('NGN', 'Nigerian Naira (₦)'),
        ('ZAR', 'South African Rand (R)'),
        ('UGX', 'Ugandan Shilling'),
        ('TZS', 'Tanzanian Shilling'),
    ]
    
    context = {
        'countries': countries,
        'currencies': currencies,
    }
    
    return render(request, 'register.html', context)