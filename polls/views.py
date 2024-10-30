from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Poll, Option, Vote
from .forms import PollForm, OptionFormSet, EditPollForm
from django.db.models import Q
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
def base_poll(request):
    query = request.GET.get('query', '')
    poll_type = request.GET.get('poll_type', '')

    polls = Poll.objects.prefetch_related('options').order_by('-created_at')
    no_polls_message = None

    if query:
        polls = polls.filter(
            title__icontains=query
        ) | polls.filter(
            description__icontains=query
        )

        if not polls.exists():
            no_polls_message = f"No polls found using the keyword: '{query}'"

    if poll_type:
        polls = polls.filter(poll_type=poll_type)

    current_time = timezone.now()
    print(f"Current time: {current_time}")
    popular_polls = Poll.objects.filter(
        view_count__gt=10
    ).exclude(
        expiration_time__lt=current_time
    ).order_by('-view_count')
    for poll in popular_polls:
        print(f"Poll: {poll.title}, Views: {poll.view_count}, Expiration: {poll.expiration_time}, Allow Expiration: {poll.allow_expiration}")

    return render(request, 'polls/all_polls.html', {
        'polls': polls,
        'query': query,
        'poll_type': poll_type,
        'no_polls_message': no_polls_message,
        'popular_polls': popular_polls
    })


def add_polls(request):
    if request.method == 'POST':
        poll_form = PollForm(request.POST, request.FILES)
        option_formset = OptionFormSet(request.POST, request.FILES)

        if poll_form.is_valid() and option_formset.is_valid():
            poll = poll_form.save(commit=False)

            if request.user.is_authenticated:
                poll.creator = request.user

            poll.save()  # Save the poll instance

            # Save the banner image if it exists
            if 'banner_image' in request.FILES:
                poll.banner_image = request.FILES['banner_image']
                poll.save()

            # Generate unique link and QR code
            poll.generate_unique_link()
            poll.generate_qr_code()
            poll.save()

            # Saving options from the formset
            for option_form in option_formset:
                if option_form.cleaned_data.get('option_text') or option_form.cleaned_data.get('option_image'):
                    option = option_form.save(commit=False)
                    option.poll = poll
                    if 'option_image' in option_form.cleaned_data and option_form.cleaned_data['option_image']:
                        option.option_image = option_form.cleaned_data['option_image']
                    option.save()

            return redirect('polls:vote_poll', poll_id=poll.id)
        else:
            logger.error("Poll Form Errors: %s", poll_form.errors)
            logger.error("Option Formset Errors: %s", option_formset.errors)

            # Check for specific formset errors and set a message
            if option_formset.non_form_errors():
                error_message = "At least two options are required."
            else:
                error_message = None

    else:
        poll_form = PollForm()
        option_formset = OptionFormSet(queryset=Option.objects.none())
        error_message = None

    return render(request, "polls/add_polls.html", {
        'poll_form': poll_form,
        'option_formset': option_formset,
        'error_message': error_message,  # Pass the error message to the template
    })

@login_required
def user_dashboard(request):
    polls = Poll.objects.filter(creator=request.user).order_by('-created_at')
    
    # Create a list of polls with their active status
    polls_with_status = [(poll, poll.is_active) for poll in polls]  # No parentheses needed
    
    return render(request, "polls/user_dashboard.html", {
        'polls_with_status': polls_with_status,
    })




@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, creator=request.user)
    if request.method == 'POST':
        poll.delete()
        return redirect('polls:user_dashboard')


@login_required
def edit_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, creator=request.user)
    existing_options = poll.options.all()

    if request.method == 'POST':
        poll_form = EditPollForm(request.POST, request.FILES, instance=poll)
        option_formset = OptionFormSet(request.POST, request.FILES, queryset=existing_options)

        if poll_form.is_valid() and option_formset.is_valid():
            poll = poll_form.save()

            # Save the banner image if it exists
            if 'banner_image' in request.FILES:
                poll.banner_image = request.FILES['banner_image']
                poll.save()

            # Save options from the formset
            for option_form in option_formset:
                if option_form.cleaned_data.get('option_text') or option_form.cleaned_data.get('option_image'):
                    option = option_form.save(commit=False)
                    option.poll = poll
                    if 'option_image' in option_form.cleaned_data and option_form.cleaned_data['option_image']:
                        option.option_image = option_form.cleaned_data['option_image']
                    option.save()

            return redirect('polls:user_dashboard')
        else:
            logger.error("Poll Form Errors: %s", poll_form.errors)
            logger.error("Option Formset Errors: %s", option_formset.errors)

    else:
        # Initialize the forms with the existing poll and options data
        poll_form = EditPollForm(instance=poll)
        option_formset = OptionFormSet(queryset=existing_options)

    return render(request, 'polls/edit_poll.html', {
        'poll_form': poll_form,
        'option_formset': option_formset,
        'poll': poll,
    })

@login_required
def vote_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    # Increment view count only if the user hasn't viewed the poll before
    if not request.session.get(f'viewed_poll_{poll.id}', False):
        poll.increment_view_count()
        request.session[f'viewed_poll_{poll.id}'] = True  # Mark this poll as viewed in the session

    options = poll.options.all()
    print(f"Options for poll ID {poll_id}: {[option.id for option in options]}")
    user_vote = None
    has_reached_vote_limit = False

    # Check if the user has already voted
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(poll=poll, user=request.user).first()
        if user_vote and not user_vote.can_vote_again():
            has_reached_vote_limit = True  # User cannot cancel/vote anymore

    if request.method == 'POST':
        # Cancel vote logic
        if 'cancel_vote' in request.POST and user_vote and user_vote.can_vote_again():
            print(f"Current attempts before increment: {user_vote.attempts}")
            user_vote.attempts += 1
            print(f"Current attempts after increment: {user_vote.attempts}")
            
            user_vote.save()  # Save the updated attempts count
            print("Deleting user vote...")
            user_vote.delete()  # Delete the user's vote after incrementing attempts
            return redirect('polls:vote_poll', poll_id=poll.id)  # Refresh page after canceling vote

        # Voting logic
        selected_options = request.POST.getlist('option') if poll.multi_option else [request.POST.get('option')]
        if not user_vote or user_vote.can_vote_again():
            for option_id in selected_options:
                option = get_object_or_404(Option, id=option_id)
                if user_vote:
                    user_vote.option = option
                    user_vote.created_at = timezone.now()  # Update the time to current
                    user_vote.save()
                else:
                    Vote.objects.create(poll=poll, option=option, user=request.user, attempts=1)
            return redirect('polls:vote_poll', poll_id=poll.id)

    # Calculate remaining attempts
    remaining_attempts = 2 - (user_vote.attempts if user_vote else 2)
    return render(request, 'polls/vote.html', {
        'poll': poll,
        'options': options,
        'multi_option': poll.multi_option,
        'user_vote': user_vote,
        'has_reached_vote_limit': has_reached_vote_limit,
        'qr_code_url': poll.qr_code.url if poll.qr_code else None,
        'poll_link': poll.link,
        'remaining_attempts': remaining_attempts,
    })


def poll_results(request, poll_id):
    # Retrieve the poll by its ID
    poll = get_object_or_404(Poll, id=poll_id)
    options = Option.objects.filter(poll=poll)

    # Calculate total votes for the poll
    total_votes = poll.total_votes()  # Assuming this method exists in the Poll model
    
    # Collect results to send to the template
    results = []
    for option in options:
        # Check if this option is the correct answer
        is_correct = option.is_correct  # Assuming Option model has an `is_correct` field
        votes = option.votes.count()  # Count of votes for this option
        
        # Get scored users only if the poll is public
        scored_users = option.votes.values_list('user__username', flat=True) if poll.is_public else []

        # Calculate percentage
        percentage = (votes / total_votes * 100) if total_votes > 0 else 0
        results.append({
            'option_text': option.option_text,
            'is_correct': is_correct,
            'votes': votes,
            'scored_users': scored_users,  # This now contains usernames (or user objects if desired)
            'percentage': percentage,
            'option_image': option.option_image if option.option_image else None,  # Ensure option_image is included
        })

    context = {
        'poll': poll,
        'results': results,
        'qr_code_url': poll.qr_code.url if poll.qr_code else None,
        'poll_link': poll.link,
    }
    
    return render(request, 'polls/poll_results.html', context)
