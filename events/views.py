from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from profiles.models import Profile
from .models import Event, University, EventRegistration, UserProfile
from .forms import EventForm
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import Http404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


def event_list(request):
    events = Event.objects.all().order_by('-start_date')

    # Filtering (University filtering removed)
    status = request.GET.get('status')
    category = request.GET.get('category')

    if status:
        events = events.filter(status=status)
    if category:
        events = events.filter(category_id=category)

    # Pagination
    paginator = Paginator(events, 12)
    page = request.GET.get('page')
    events = paginator.get_page(page)

    context = {
        'events': events,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_registered = False

    if request.user.is_authenticated:
        user_registered = EventRegistration.objects.filter(
            event=event,
            participant__user=request.user
        ).exists()
        
        if request.method == 'POST' and 'register' in request.POST:
            EventRegistration.objects.get_or_create(
                event=event,
                participant=request.user.userprofile
            )
            return redirect('event_detail', event_id=event_id)
    
    context = {
        'event': event,
        'user_registered': user_registered,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def create_event(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = user  # Assign the current user as the organizer
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