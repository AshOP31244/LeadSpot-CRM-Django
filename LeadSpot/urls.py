from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.contrib.auth import views as auth_views

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('leads/')
    return redirect('login')

urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='leads/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('leads/', include('leads.urls')),
]
