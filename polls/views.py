from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Poll, Option, Vote
from .forms import PollForm, OptionFormSet
from django.db.models import Q


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

        if poll_form.is_valid() and option_formset.is_valid():
            poll = poll_form.save()
            option_formset.save()
            return redirect('user_dashboard')
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

    # Check if the user has already voted
    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(Q(poll=poll) & Q(user=request.user)).first()
    
    # Allow multiple selections if `multi_option` is True
    if request.method == 'POST':
        # If cancelling a vote
        if 'cancel_vote' in request.POST:
            if user_vote:
                user_vote.delete()  # Delete the user's vote
                return redirect('vote_poll', poll_id=poll.id)  # Redirect to refresh the page

        # Handle voting
        selected_options = request.POST.getlist('option') if poll.multi_option else [request.POST.get('option')]

        # Ensure user can only vote if they haven't already voted or if the vote is older than 30 minutes
        if not user_vote or (timezone.now() - user_vote.voted_at > timedelta(minutes=30)):
            for option_id in selected_options:
                option = get_object_or_404(Option, id=option_id)
                Vote.objects.create(poll=poll, option=option, user=request.user)
            return redirect('vote_poll', poll_id=poll.id)

    return render(request, 'polls/vote.html', {
        'poll': poll,
        'options': options,
        'multi_option': poll.multi_option,
        'user_vote': user_vote,
        'qr_code_url': poll.qr_code.url if poll.qr_code else None,  # QR code URL if available
        'poll_link': poll.link,  # Poll link
    })

def poll_results(request, poll_id):
    # Retrieve the poll by its ID
    poll = get_object_or_404(Poll, id=poll_id)
    options = Option.objects.filter(poll=poll)

    # Calculate total votes for the poll
    total_votes = poll.total_votes()  # Assuming you have this method

    results = []
    for option in options:
        percentage = (option.votes.count() / total_votes * 100) if total_votes > 0 else 0  # Prevent division by zero
        results.append({
            'option_text': option.option_text,
            'votes': option.votes.count(),
            'percentage': percentage,
        })

    return render(request, 'polls/poll_results.html', {
        'poll': poll,
        'results': results,
    })