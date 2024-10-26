from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Poll, Option, Vote
from .forms import PollForm, OptionFormSet
from django.db.models import Q
from datetime import timedelta


def base_poll(request):
    polls = Poll.objects.prefetch_related('options').all()
    return render(request, 'polls/base.html', {'polls': polls})


def add_polls(request):
    if request.method == 'POST':
        poll_form = PollForm(request.POST, request.FILES)
        option_formset = OptionFormSet(request.POST)  

        if poll_form.is_valid() and option_formset.is_valid():
            poll = poll_form.save(commit=False)
            if request.user.is_authenticated:
                poll.creator = request.user
            poll.save()
            
            poll.generate_unique_link()
            poll.generate_qr_code()
            poll.save()

            for option_form in option_formset:
                if option_form.cleaned_data.get('option_text'):
                    option = option_form.save(commit=False)
                    option.poll = poll
                    if poll.poll_type == 'question':
                        option.is_correct = option_form.cleaned_data.get('is_correct', False)
                    option.save()
                    
            return redirect('vote_poll', poll_id=poll.id)  
    else:
        poll_form = PollForm()
        option_formset = OptionFormSet(queryset=Option.objects.none()) 

    return render(request, "polls/add_polls.html", {
        'poll_form': poll_form,
        'option_formset': option_formset,
    })



@login_required
def user_dashboard(request):
    polls = Poll.objects.filter(creator=request.user)
    return render(request, "polls/user_dashboard.html", {
        'polls': polls,
    })

@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, creator=request.user)
    if request.method == 'POST':
        poll.delete()
        return redirect('user_dashboard') 

@login_required
def edit_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, creator=request.user)

    if request.method == 'POST':
        poll_form = PollForm(request.POST, request.FILES, instance=poll)
        option_formset = OptionFormSet(request.POST, queryset=poll.options.all())

        # Debug logging
        print("Poll Form Valid: ", poll_form.is_valid())
        print("Option Formset Valid: ", option_formset.is_valid())
        print("Formset Data:", option_formset.data)  # Check the formset data

        if poll_form.is_valid() and option_formset.is_valid():
            poll_form.save()
            option_formset.save()
            print("Redirecting to user_dashboard")
            return redirect('user_dashboard')
        else:
            # Print form errors to debug
            print("Poll Form Errors: ", poll_form.errors)
            print("Option Formset Errors: ", option_formset.errors)

    else:
        poll_form = PollForm(instance=poll)
        option_formset = OptionFormSet(queryset=poll.options.all())

    return render(request, 'polls/edit_poll.html', {
        'poll_form': poll_form,
        'option_formset': option_formset,
        'poll': poll,
    })


@login_required
def vote_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    poll.increment_view_count()
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
            return redirect('vote_poll', poll_id=poll.id)  # Refresh page after canceling vote

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
            return redirect('vote_poll', poll_id=poll.id)

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
    total_votes = poll.total_votes()  # Assuming you have this method

    results = []
    for option in options:
        # Use the related name 'votes' to count the number of votes for this option
        votes_count = option.votes.count()  # Now this should work
        percentage = (votes_count / total_votes * 100) if total_votes > 0 else 0  # Prevent division by zero
        results.append({
            'option_text': option.option_text,
            'votes': votes_count,
            'percentage': percentage,
        })

    return render(request, 'polls/poll_results.html', {
        'poll': poll,
        'results': results,
    })

