from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from profiles.models import Profile
from .models import Event, University, EventRegistration, UserProfile, Comment, EventReaction
from .forms import EventForm, CommentForm
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import Http404

from .models import University  # Make sure the University model is imported

def event_list(request):
    # Get filter parameters from the request
    status_filter = request.GET.get('status')
    university_filter = request.GET.get('university')

    # Base query for events
    events = Event.objects.all().order_by('-start_date').prefetch_related('comments')

    # Filter by status if provided
    if status_filter:
        events = events.filter(status=status_filter)
    
    # Filter by university if provided
    if university_filter:
        events = events.filter(organizer__userprofile__university__id=university_filter)

    # Get all universities for the filter dropdown
    universities = University.objects.all()

    paginator = Paginator(events, 12)
    page = request.GET.get('page')
    events = paginator.get_page(page)

    # Add extra details like number of comments
    for event in events:
        event.comments_count = event.comments.count()

    return render(request, 'events/event_list.html', {
        'events': events,
        'universities': universities,  # Pass universities to the template
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_registered = False
    comment_form = CommentForm()
    comments = event.comments.filter(parent=None).prefetch_related('replies', 'likes')

    if request.user.is_authenticated:
        # Ensure the user has a profile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Check if the user is registered for the event
        user_registered = EventRegistration.objects.filter(
            event=event,
            participant=user_profile
        ).exists()

        # Handle event registration
        if request.method == 'POST' and 'register' in request.POST:
            EventRegistration.objects.get_or_create(
                event=event,
                participant=user_profile
            )
            return redirect('event_detail', event_id=event_id)

    context = {
        'event': event,
        'user_registered': user_registered,
        'comment_form': comment_form,
        'comments': comments,
    }

    return render(request, 'events/event_detail.html', context)


@login_required
def create_event(request):
    user = request.user  # Get the currently logged-in user

    # Get the logged-in user's UserProfile to access their university
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = user  # Assign the current user as the organizer

            # Assign the user's university to the event if available
            if user_profile and user_profile.university:
                event.university = user_profile.university

            event.save()
            return redirect('event_list')  # Redirect after successful creation

        else:
            # Handle form errors
            return render(request, 'events/create_event.html', {'form': form, 'error': 'Invalid form submission.'})

    else:
        form = EventForm()  # Display the form if it's a GET request

    return render(request, 'events/create_event.html', {'form': form})


def university_autocomplete(request):
    if 'term' in request.GET:
        query = request.GET.get('term')
        universities = University.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query)
        ).values('id', 'name')[:10]

        results = [{'id': uni['id'], 'label': uni['name'], 'value': uni['name']} for uni in universities]
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)

@login_required
def add_comment(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        parent_comment_id = request.POST.get('parent_comment_id')
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.event = event
            comment.user = user_profile
            
            # If replying to a comment
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                comment.parent = parent_comment
                
            comment.save()
            return redirect('event_detail', event_id=event_id)
    
    return redirect('event_detail', event_id=event_id)

@login_required
def toggle_comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user_profile = request.user.userprofile
    
    if user_profile in comment.likes.all():
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
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Toggle like
    existing_like = comment.likes.filter(user=user_profile).first()
    if existing_like:
        existing_like.delete()
    else:
        comment.likes.add(user_profile)
    
    return JsonResponse({'likes_count': comment.likes.count()})


@login_required
def toggle_reaction(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        reaction_type = request.POST.get('reaction_type')

        if reaction_type not in dict(EventReaction.REACTION_CHOICES):
            return JsonResponse({'status': 'error', 'message': 'Invalid reaction type'}, status=400)

        reaction, created = EventReaction.objects.get_or_create(
            event=event,
            user=request.user.userprofile,
            defaults={'reaction_type': reaction_type}
        )

        if not created:
            if reaction.reaction_type == reaction_type:
                # If the user clicks the same reaction, remove it
                reaction.delete()
                return JsonResponse({'status': 'removed'})
            else:
                # Change to the new reaction
                reaction.reaction_type = reaction_type
                reaction.save()

        return JsonResponse({'status': 'success', 'reaction_type': reaction_type})

    return JsonResponse({'status': 'error'}, status=400)