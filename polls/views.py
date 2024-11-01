from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Poll, Option, Vote, Comment, Like
from .forms import PollForm, OptionFormSet, EditPollForm
from django.db.models import Q
from datetime import timedelta
import logging
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
import pytz
import json  

logger = logging.getLogger(__name__)
from django.db.models import Q


def base_poll(request):
    query = request.GET.get("query", "")
    poll_type = request.GET.get("poll_type", "")

    polls = Poll.objects.prefetch_related("options").order_by("-created_at")
    no_polls_message = None

    if query:
        polls = polls.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

        if not polls.exists():
            no_polls_message = f"No polls found using the keyword: '{query}'"

    if poll_type:
        polls = polls.filter(poll_type=poll_type)

    current_time = timezone.now()

    popular_polls = (
        Poll.objects.filter(view_count__gt=10)
        .exclude(expiration_time__lt=current_time)
        .order_by("-view_count")
    )

    liked_polls = Like.objects.filter(user=request.user, poll__in=polls).values_list(
        "poll_id", flat=True
    )
    liked_comments = Like.objects.filter(user=request.user, poll__in=polls).values_list(
        "comment_id", flat=True
    )

    liked_comments_set = set(liked_comments)
    liked_polls_set = set(liked_polls)

    return render(
        request,
        "polls/all_polls.html",
        {
            "polls": polls,
            "query": query,
            "poll_type": poll_type,
            "no_polls_message": no_polls_message,
            "popular_polls": popular_polls,
            "liked_polls_set": liked_polls_set,
            "liked_comments_set": liked_comments_set,
        },
    )


def load_comments(request, poll_id):
    offset = int(request.GET.get("offset", 0))
    limit = int(request.GET.get("limit", 5))  # Load 5 comments at a time

    # Fetch comments for the given poll, ordered by creation time
    comments = Comment.objects.filter(poll_id=poll_id).order_by("-created_at")[
        offset : offset + limit
    ]

    # Create a set of liked comment IDs for the current user
    liked_comments = Like.objects.filter(user=request.user).values_list(
        "comment_id", flat=True
    )
    liked_comments_set = set(liked_comments)

    comments_data = []
    for c in comments:
        comments_data.append(
            {
                "id": c.id,
                "user": {"username": c.user.username},
                "text": c.text,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "total_likes": c.total_likes(),  # Call the method with parentheses
                "liked": c.id
                in liked_comments_set,  # Check if the comment is liked by the user
            }
        )

    return JsonResponse({"comments": comments_data})


def add_polls(request):
    if request.method == "POST":
        poll_form = PollForm(request.POST, request.FILES)
        option_formset = OptionFormSet(request.POST, request.FILES)
        error_message = None

        # Check if the formsets are valid
        if poll_form.is_valid() and option_formset.is_valid():
            poll = poll_form.save(commit=False)  # Create poll instance but don't save yet

            # Check if the poll type is a question and if there are correct answers
            if poll.poll_type == 'question':
                correct_answers = any(option_form.cleaned_data.get("is_correct") for option_form in option_formset)
                
                if not correct_answers:
                    error_message = "A question must have at least one correct answer."
                else:
                    # If there are correct answers, proceed to save the poll
                    if request.user.is_authenticated:
                        poll.creator = request.user

                    poll.save()  # Save the poll after validation
                    if "banner_image" in request.FILES:
                        poll.banner_image = request.FILES["banner_image"]
                        poll.save()
                    poll.generate_unique_link()
                    poll.generate_qr_code()
                    poll.save()

                    for option_form in option_formset:
                        if option_form.cleaned_data.get("option_text") or option_form.cleaned_data.get("option_image"):
                            option = option_form.save(commit=False)
                            option.poll = poll
                            if "option_image" in option_form.cleaned_data and option_form.cleaned_data["option_image"]:
                                option.option_image = option_form.cleaned_data["option_image"]
                            option.save()

                    return redirect("polls:vote_poll", poll_id=poll.id)
            else:
                # For non-question polls, save without checking for correct answers
                if request.user.is_authenticated:
                    poll.creator = request.user

                poll.save()  # Save the poll
                if "banner_image" in request.FILES:
                    poll.banner_image = request.FILES["banner_image"]
                    poll.save()
                poll.generate_unique_link()
                poll.generate_qr_code()
                poll.save()

                for option_form in option_formset:
                    if option_form.cleaned_data.get("option_text") or option_form.cleaned_data.get("option_image"):
                        option = option_form.save(commit=False)
                        option.poll = poll
                        if "option_image" in option_form.cleaned_data and option_form.cleaned_data["option_image"]:
                            option.option_image = option_form.cleaned_data["option_image"]
                        option.save()

                return redirect("polls:vote_poll", poll_id=poll.id)

        else:
            logger.error("Poll Form Errors: %s", poll_form.errors)
            logger.error("Option Formset Errors: %s", option_formset.errors)

            if option_formset.non_form_errors():
                error_message = "At least two options are required."
            else:
                error_message = []
                for i, form in enumerate(option_formset.forms):
                    if not form.is_valid():
                        form_errors = form.errors.as_data()
                        for field, field_errors in form_errors.items():
                            for error in field_errors:
                                error_message.append(f"Option {i + 1}: {error.message}")

                if not error_message:
                    error_message = "Please correct the errors below."

    else:
        poll_form = PollForm()
        option_formset = OptionFormSet(queryset=Option.objects.none())
        error_message = None

    return render(
        request,
        "polls/add_polls.html",
        {
            "poll_form": poll_form,
            "option_formset": option_formset,
            "error_message": error_message,
        },
    )

@login_required
def user_dashboard(request):
    polls = Poll.objects.filter(creator=request.user).order_by("-created_at")

    # Create a list of polls with their active status
    polls_with_status = [
        (poll, poll.is_active) for poll in polls
    ]  # No parentheses needed

    return render(
        request,
        "polls/user_dashboard.html",
        {
            "polls_with_status": polls_with_status,
        },
    )
@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, creator=request.user)
    if request.method == "POST":
        poll.delete()
        return redirect("polls:user_dashboard")


@login_required
def edit_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, creator=request.user)
    existing_options = poll.options.all()

    if request.method == "POST":
        poll_form = EditPollForm(request.POST, request.FILES, instance=poll)
        option_formset = OptionFormSet(
            request.POST, request.FILES, queryset=existing_options
        )

        if poll_form.is_valid() and option_formset.is_valid():
            poll = poll_form.save()

            # Save the banner image if it exists
            if "banner_image" in request.FILES:
                poll.banner_image = request.FILES["banner_image"]
                poll.save()

            # Save options from the formset
            for option_form in option_formset:
                if option_form.cleaned_data.get(
                    "option_text"
                ) or option_form.cleaned_data.get("option_image"):
                    option = option_form.save(commit=False)
                    option.poll = poll
                    if (
                        "option_image" in option_form.cleaned_data
                        and option_form.cleaned_data["option_image"]
                    ):
                        option.option_image = option_form.cleaned_data["option_image"]
                    option.save()

            return redirect("polls:user_dashboard")
        else:
            logger.error("Poll Form Errors: %s", poll_form.errors)
            logger.error("Option Formset Errors: %s", option_formset.errors)

    else:
        # Initialize the forms with the existing poll and options data
        poll_form = EditPollForm(instance=poll)
        option_formset = OptionFormSet(queryset=existing_options)

    return render(
        request,
        "polls/edit_poll.html",
        {
            "poll_form": poll_form,
            "option_formset": option_formset,
            "poll": poll,
        },
    )


@login_required
def vote_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not request.session.get(f"viewed_poll_{poll.id}", False):
        poll.increment_view_count()
        request.session[f"viewed_poll_{poll.id}"] = True

    options = poll.options.all()
    user_vote = Vote.objects.filter(poll=poll, user=request.user).first()
    has_reached_vote_limit = False

    if user_vote and not user_vote.can_vote_again():
        has_reached_vote_limit = True

    utc_now = timezone.now()
    kenyan_tz = pytz.timezone("Africa/Nairobi")
    now = utc_now.astimezone(kenyan_tz)

    time_limit = now - timedelta(minutes=30)

    if request.method == "POST":
        if "cancel_vote" in request.POST and user_vote and user_vote.can_vote_again():
            if (
                poll.poll_type == "opinion"
                and user_vote.created_at >= time_limit
                and poll.is_active
            ):
                # Increment the attempts in Poll
                poll.attempts += 1
                poll.save()  # Save the updated attempts
                user_vote.delete()  # Delete the existing vote
                return redirect("polls:vote_poll", poll_id=poll.id)

        # Voting logic
        selected_options = (
            request.POST.getlist("option")
            if poll.multi_option
            else [request.POST.get("option")]
        )

        if not user_vote or user_vote.can_vote_again():
            if poll.multi_option:
                for option_id in selected_options:
                    option = get_object_or_404(Option, id=option_id)
                    Vote.objects.create(poll=poll, option=option, user=request.user)
            else:
                option_id = selected_options[0]
                option = get_object_or_404(Option, id=option_id)
                if user_vote:
                    user_vote.option = option
                    user_vote.created_at = timezone.now()
                    user_vote.save()
                else:
                    Vote.objects.create(poll=poll, option=option, user=request.user)

            # Increment the attempts in Poll
            poll.attempts += 1
            poll.save()

            return redirect("polls:vote_poll", poll_id=poll.id)

    remaining_attempts = 2 - poll.attempts
    return render(
        request,
        "polls/vote.html",
        {
            "poll": poll,
            "options": options,
            "multi_option": poll.multi_option,
            "user_vote": user_vote,
            "has_reached_vote_limit": has_reached_vote_limit,
            "qr_code_url": poll.qr_code.url if poll.qr_code else None,
            "poll_link": poll.link,
            "remaining_attempts": remaining_attempts,
            "now": now,
            "time_limit": time_limit,
        },
    )


def search_poll(request, title):
    # Use icontains to allow for case-insensitive matching
    polls = Poll.objects.filter(title__iexact=title)
    if not polls.exists():
        # Handle case where no poll matches the title
        return render(
            request, "all_polls.html", {"message": "No polls found with that title."}
        )

    # Assuming you want to render the list of matching polls
    return render(request, "polls/all_polls.html", {"polls": polls})


def poll_results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    options = Option.objects.filter(poll=poll)
    total_votes = poll.total_votes()
    results = []
    for option in options:
        # Check if this option is the correct answer
        is_correct = (
            option.is_correct
        )  # Assuming Option model has an `is_correct` field
        votes = option.votes.count()  # Count of votes for this option

        scored_users = (
            option.votes.values_list("user__username", flat=True)
            if poll.is_public
            else []
        )
        percentage = (votes / total_votes * 100) if total_votes > 0 else 0
        results.append(
            {
                "option_text": option.option_text,
                "is_correct": is_correct,
                "votes": votes,
                "scored_users": scored_users,
                "percentage": percentage,
                "option_image": option.option_image if option.option_image else None,
            }
        )

    context = {
        "poll": poll,
        "results": results,
        "qr_code_url": poll.qr_code.url if poll.qr_code else None,
        "poll_link": poll.link,
    }

    return render(request, "polls/poll_results.html", context)


@login_required
def add_comment(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.method == "POST":
        # Extract comment text from the JSON request
        data = json.loads(request.body)
        comment_text = data.get("comment")

        # Set created_at to Nairobi time
        nairobi_tz = pytz.timezone("Africa/Nairobi")
        created_at_nairobi = timezone.now().astimezone(nairobi_tz)

        # Create the comment, setting created_at automatically with auto_now_add
        comment = Comment.objects.create(
            poll=poll,
            user=request.user,
            text=comment_text,
            created_at=created_at_nairobi,
        )

        # Return a JSON response with the comment data
        return JsonResponse({
            "success": True,
            "user": request.user.username,
            "comment_text": comment.text,
        })

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def like_comment(request, comment_id):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user
        existing_like = Like.objects.filter(user=user, comment=comment).first()
        
        if existing_like:
            existing_like.delete()
            liked = False
        else:
            Like.objects.create(user=user, comment=comment)
            liked = True

        total_likes = comment.comment_likes.count()
        
        return JsonResponse({"success": True, "total_likes": total_likes, "liked": liked})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def like_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    # Check if the user has already liked the poll
    existing_like = Like.objects.filter(user=request.user, poll=poll, comment=None).first()

    if not existing_like:
        # Create a new like
        Like.objects.create(user=request.user, poll=poll)
        liked = True
    else:
        existing_like.delete()
        liked = False

    total_likes = poll.poll_likes.count()  # Use the updated related name here

    # Return a JSON response
    return JsonResponse({"success": True, "liked": liked, "total_likes": total_likes})
