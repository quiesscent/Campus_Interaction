from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from .models import Poll
from .forms import PollForm, OptionFormSet
from .models import Poll, Option

# Create your views here.
def base_poll(request):
    polls = Poll.objects.prefetch_related('options').all()  # Prefetch options for each poll
    return render(request, 'polls/base.html', {'polls': polls})

def add_poll(request):
    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        option_formset = OptionFormSet(request.POST)
        
        if poll_form.is_valid() and option_formset.is_valid():
            poll = poll_form.save(commit=False)
            poll.creator = request.user  # Assuming the user is logged in
            poll.save()

            for option_form in option_formset:
                if option_form.cleaned_data.get('option_text'):
                    option = option_form.save(commit=False)
                    option.poll = poll
                    option.save()

            return redirect('base_poll')  # Correct URL redirection
    else:
        poll_form = PollForm()
        option_formset = OptionFormSet()
    return render(request, 'polls/add_polls.html', {
        'poll_form': poll_form,
        'option_formset': option_formset,
    })
