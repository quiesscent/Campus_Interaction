from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            messages.success(
                request,
                "Account created successfully! Please login and complete your profile.",
            )
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "profiles/register.html", {"form": form})


@login_required
def dashboard(request):
    # Create profile if it doesn't exist
    Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'delete_account' in request.POST:
            # Handle account deletion
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been successfully deleted.')
            return redirect('login')
            
        elif 'username' in request.POST:  # Account settings form
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)
            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Your account settings have been updated!')
                return HttpResponseRedirect(reverse('dashboard'))
        else:  # Profile form
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(
                request.POST,
                request.FILES,
                instance=request.user.profile
            )
            if p_form.is_valid():
                profile = p_form.save(commit=False)
                if 'profile_pic' in request.FILES:
                    profile.profile_pic = request.FILES['profile_pic']
                profile.save()
                messages.success(request, 'Your profile has been updated!')
                return HttpResponseRedirect(reverse('dashboard'))
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': request.user.profile
    }
    return render(request, 'profiles/dashboard.html', context)