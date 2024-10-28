import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from profiles.models import Profile
from .models import Event, EventRegistration, Comment, EventReaction
from .forms import EventForm, CommentForm, EventRegistrationForm


# Set up logging
logger = logging.getLogger(__name__)

@login_required
def event_list(request):
    status_filter = request.GET.get('status')
    campus_filter = request.GET.get('campus')
    
    events = Event.objects.all().order_by('-start_date').prefetch_related('comments')
    
    if status_filter:
        now = timezone.now()
        if status_filter == 'upcoming':
            events = events.filter(start_date__gte=now)
        elif status_filter == 'ongoing':
            events = events.filter(start_date__lte=now, end_date__gte=now)
        elif status_filter == 'completed':
            events = events.filter(end_date__lt=now)
    
    if campus_filter:
        events = events.filter(campus__campus=campus_filter)
    
    # Get unique campus values from Profile model
    campuses = Profile.objects.values_list('campus', flat=True).distinct()
    
    paginator = Paginator(events, 12)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    
    for event in events:
        event.comments_count = event.comments.count()
    
    return render(request, 'events/event_list.html', {
        'events': events,
        'campuses': campuses,
    })

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    user_registered = EventRegistration.objects.filter(event=event, participant=user_profile).exists()
    
    comments = event.comments.filter(parent=None).prefetch_related('replies', 'likes')
    comment_form = CommentForm()

    if request.method == 'POST':
        if 'register' in request.POST:
            registration_form = EventRegistrationForm(data=request.POST, event=event)
            if registration_form.is_valid():
                EventRegistration.objects.create(event=event, participant=user_profile)
                messages.success(request, "Successfully registered for the event!")
                return redirect('event_detail', event_id=event_id)
            else:
                messages.error(request, "Invalid registration details. Please try again.")

    context = {
        'event': event,
        'user_registered': user_registered,
        'comment_form': comment_form,
        'comments': comments,
        'registration_form': EventRegistrationForm(event=event)
    }
    return render(request, 'events/event_detail.html', context)

@login_required
@transaction.atomic
def create_event(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                event = form.save(commit=False)
                event.organizer = user_profile
                event.campus = user_profile.campus
                event.save()
                messages.success(request, "Event created successfully!")
                return redirect('events:event_list')
            except Exception as e:
                messages.error(request, f"An error occurred while saving the event: {e}")
        else:
            messages.error(request, "Invalid form submission.")
            print(form.errors)  # Print form errors to console for debugging
    else:
        form = EventForm()

    return render(request, 'events/create_event.html', {'form': form})

@login_required
def add_comment(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        parent_comment_id = request.POST.get('parent_comment_id')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.event = event
            comment.user = user_profile
            
            # Check if this is a reply
            if parent_comment_id:
                comment.parent = get_object_or_404(Comment, id=parent_comment_id)
            
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect('events:event_detail', event_id=event_id)

    messages.error(request, "Failed to add comment.")
    return redirect('events:event_detail', event_id=event_id)

@login_required
@require_POST
def toggle_comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user_profile = request.user.profile
    
    if user_profile in comment.likes.all():  # Check if user already liked the comment
        comment.likes.remove(user_profile)
        liked = False
    else:
        comment.likes.add(user_profile)
        liked = True
    
    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'likes_count': comment.likes.count()
    })

@login_required
@require_http_methods(["POST", "DELETE"])
@transaction.atomic
def delete_event(request, event_id):
    # Fetch the event or return 404 if it doesn't exist
    event = get_object_or_404(Event, id=event_id)

    # Permission check
    if event.organizer.user != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Permission denied"}, status=403)

    # Attempt to delete image if exists
    image_path = event.image.path if event.image else None
    event.delete()  # Delete event from the database

    # Delete associated media file if it exists
    if image_path:
        try:
            default_storage.delete(image_path)
        except Exception as e:
            logger.error(f"Error deleting file {image_path}: {e}")
            return JsonResponse({
                "status": "success",
                "message": "Event deleted, but media file removal failed."
            }, status=500)

    # Use Django messages for UI feedback and return JSON response
    messages.success(request, "Event deleted successfully.")
    return JsonResponse({"status": "success", "message": "Event deleted successfully."})

@login_required
@require_POST
def toggle_reaction(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        reaction_type = request.POST.get('reaction_type')

        if reaction_type not in dict(EventReaction.REACTION_CHOICES):
            return JsonResponse({'status': 'error', 'message': 'Invalid reaction type'}, status=400)

        reaction, created = EventReaction.objects.get_or_create(
            event=event,
            user=request.user.profile,
            defaults={'reaction_type': reaction_type}
        )

        if not created:
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                return JsonResponse({'status': 'removed', 'reaction_type': reaction_type})
            else:
                reaction.reaction_type = reaction_type
                reaction.save()

        return JsonResponse({'status': 'success', 'reaction_type': reaction_type})

    return JsonResponse({'status': 'error'}, status=400)

@login_required
def campus_autocomplete(request):
    if 'term' in request.GET:
        query = request.GET.get('term')
        
        # Query for campus using Profile model
        campuses = Profile.objects.filter(
            Q(campus__icontains=query)
        ).values('id', 'campus').distinct()[:10]

        # Format the results to return campus data
        results = [{'id': profile['id'], 'label': profile['campus'], 'value': profile['campus']} for profile in campuses]
        return JsonResponse(results, safe=False)

    return JsonResponse([], safe=False)