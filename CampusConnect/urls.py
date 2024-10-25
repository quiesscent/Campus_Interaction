"""
URL configuration for CampusConnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Resources import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('resources/<int:pk>/', views.resource_detail, name='resource_detail'),
    path('resources/<int:pk>/edit/', views.edit_resource, name='edit_resource'),
    path('resources/<int:pk>/delete/', views.delete_resource, name='delete_resource'),
    path('resources/<int:pk>/report/', views.report_resource, name='report_resource'),
    path('resources/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('resources/', views.view_resources, name='view_resources'),
    path('resources/<int:pk>/', views.resource_detail, name='resource_detail'),
    path('resources/upload/', views.upload_resource, name='upload_resource'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='resources/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='resources/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='resources/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='resources/password_reset_complete.html'),
         name='password_reset_complete'),
    ]
