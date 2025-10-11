from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import uuid

from ..models import PasswordResetToken


def password_reset_request(request):
    """Handle password reset request."""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'password_reset_request.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Create reset token
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(hours=2)  # Token expires in 2 hours
            
            # Delete any existing tokens for this user
            PasswordResetToken.objects.filter(user=user).delete()
            
            # Create new token
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # Create reset URL
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'token': token})
            )
            
            # Send email (for now, just show the link)
            try:
                send_mail(
                    subject='Remittence - Password Reset',
                    message=f'Click this link to reset your password: {reset_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(
                    request, 
                    f'Password reset link has been sent to {email}. Please check your email.'
                )
            except Exception as e:
                # For development, show the reset link directly
                messages.info(
                    request,
                    f'Email not configured. Use this link to reset: {reset_url}'
                )
            
            return redirect('login')
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(
                request, 
                f'If {email} is registered, you will receive a password reset link.'
            )
            return redirect('login')
    
    return render(request, 'password_reset_request.html')


def password_reset_confirm(request, token):
    """Handle password reset confirmation."""
    try:
        reset_token = PasswordResetToken.objects.get(
            token=token,
            used=False,
            expires_at__gt=timezone.now()
        )
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('login')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if not password1 or not password2:
            messages.error(request, 'Please fill in both password fields.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        # Reset the password
        user = reset_token.user
        user.set_password(password1)
        user.save()
        
        # Mark token as used
        reset_token.used = True
        reset_token.save()
        
        messages.success(request, 'Your password has been reset successfully. You can now login.')
        return redirect('login')
    
    context = {
        'token': token,
        'user': reset_token.user
    }
    return render(request, 'password_reset_confirm.html', context)