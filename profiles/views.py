import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
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
    """View for rendering the dashboard template"""
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {"u_form": u_form, "p_form": p_form, "profile": request.user.profile}
    return render(request, "profiles/dashboard.html", context)


@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """API endpoint for updating profile details"""
    try:
        data = json.loads(request.POST.get("data", "{}"))
        profile = request.user.profile
        user = request.user

        # Handle user data updates
        if "username" in data:
            u_form = UserUpdateForm(data, instance=user)
            if u_form.is_valid():
                u_form.save()
            else:
                return JsonResponse(
                    {"status": "error", "errors": u_form.errors}, status=400
                )

        # Handle profile data updates
        profile_data = {
            "student_id": data.get("student_id", profile.student_id),
            "course": data.get("course", profile.course),
            "year_of_study": data.get("year_of_study", profile.year_of_study),
            "bio": data.get("bio", profile.bio),
            "campus": data.get("campus", profile.campus),
            "gender": data.get("gender", profile.gender),
            "date_of_birth": data.get("date_of_birth", profile.date_of_birth),
        }

        p_form = ProfileUpdateForm(profile_data, instance=profile)
        if p_form.is_valid():
            p_form.save()

            # Handle profile picture separately
            if "profile_pic" in request.FILES:
                profile_pic = request.FILES["profile_pic"]
                path = default_storage.save(
                    f"profile_pics/{user.username}_{profile_pic.name}",
                    ContentFile(profile_pic.read()),
                )
                profile.profile_pic = path
                profile.save()

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Profile updated successfully",
                    "data": {
                        "username": user.username,
                        "email": user.email,
                        "profile_pic_url": profile.get_avatar_url(),
                        **profile_data,
                    },
                }
            )
        else:
            return JsonResponse(
                {"status": "error", "errors": p_form.errors}, status=400
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_account(request):
    """API endpoint for account deletion"""
    try:
        user = request.user
        logout(request)
        user.delete()
        return JsonResponse(
            {"status": "success", "message": "Account deleted successfully"}
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
