from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Poll, Option, Vote
from .forms import PollForm, OptionFormSet


def base_poll(request):
    polls = Poll.objects.prefetch_related('options').all()
    return render(request, 'polls/base.html', {'polls': polls})


@login_required
def add_polls(request):
    if request.method == 'POST':
        poll_form = PollForm(request.POST, request.FILES)
        option_formset = OptionFormSet(request.POST)  # Pass the POST data to the formset
        
        if poll_form.is_valid() and option_formset.is_valid():
            poll = poll_form.save(commit=False)
            poll.creator = request.user
            poll.save()

            poll.generate_unique_link()
            poll.generate_qr_code()
            poll.save()

            # Iterate over the formset to save all options
            for option_form in option_formset:
                if option_form.cleaned_data.get('option_text'):
                    option = option_form.save(commit=False)
                    option.poll = poll
                    # Set is_correct only for question types
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
            poll_form.save()
            option_formset.save()
            return redirect('poll_detail', poll_id=poll.id)
    else:
        poll_form = PollForm(instance=poll)
        option_formset = OptionFormSet(queryset=poll.options.all())

    return render(request, "polls/edit_poll.html", {
        'poll_form': poll_form,
        'option_formset': option_formset,
        'poll': poll,
    })


@login_required
def vote_poll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if not poll.is_active():
        return render(request, 'polls/expired.html', {'poll': poll})
    
    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = get_object_or_404(Option, pk=option_id, poll=poll)
        if Vote.objects.filter(user=request.user, poll=poll).exists():
            return render(request, 'polls/already_voted.html', {'poll': poll})
        Vote.objects.create(user=request.user, poll=poll, option=option)
        
        if poll.poll_type == 'question':
            return render(request, 'polls/', {'poll': poll, 'option': option})
        else:
            return redirect('poll_results', poll_id=poll_id)
    
    return render(request, 'polls/vote.html', {'poll': poll})

def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    options = poll.options.all()  # Fetch all options associated with this poll
    total_votes = poll.total_votes()  # Use the model method to get the total votes

    return render(request, "polls/poll_details.html", {
        'poll': poll,
        'options': options,
        'total_votes': total_votes,
    })


def poll_results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    options = poll.options.all()
    votes = Vote.objects.filter(poll=poll)
    total_votes = votes.count()

    return render(request, 'polls/results.html', {
        'poll': poll,
        'options': options,
        'total_votes': total_votes,
    })
