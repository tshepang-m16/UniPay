from django.urls import path

# Import each page view from its dedicated file
from .views.dashboard_views import dashboard_view
from .views.login_view import login_view
from .views.logout_views import logout_view
from .views.promotions_views import promotions_view
from .views.budget_views import budget_view
from .views.donate_views import donate_view
from .views.profile_view import profile_view
from .views.ForLearning_views import learning_view
from .views.users_views import users_view
from .views.chatbot_views import chatbot_api
from .views.admin_views import admin_dashboard
from .views.auth_views import register_view
from .views.password_reset_views import password_reset_request, password_reset_confirm

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('signup/', register_view, name='signup'),
    
    # Password Reset
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/<str:token>/', password_reset_confirm, name='password_reset_confirm'),

    path('promotions/', promotions_view, name='promotions'),
    path('budget/', budget_view, name='budget'),
    path('donate/', donate_view, name='donate'),
    path('profile/', profile_view, name='profile'),

    path('learning/', learning_view, name='learning'),
    path('education/', learning_view, name='education'),

    path('users/', users_view, name='users'),
    path('chatbot/api/', chatbot_api, name='chatbot_api'),

    # Admin dashboard
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),

    # Legacy .html routes (redirect to clean URLs)
    path('dashboard.html', dashboard_view),
    path('login.html', login_view),
    path('logout.html', logout_view),
    path('promotions.html', promotions_view),
    path('budget.html', budget_view),
    path('donate.html', donate_view),
    path('profile.html', profile_view),
    path('ForLearning.html', learning_view),
    path('education.html', learning_view),
    path('users.html', users_view),
    path('register.html', register_view),
    path('signup.html', register_view),
]
