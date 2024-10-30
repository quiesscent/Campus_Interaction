from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from .models import Forum, ForumMembership
from feeds.models import Post

class ForumListView(ListView):
    model = Forum
    template_name = 'forums/forum_list.html'

class ForumDetailView(DetailView):
    model = Forum
    template_name = 'forums/forum_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forum = self.get_object()
        context['posts'] = forum.posts.all()  # Access forum-specific posts
        return context

class JoinForumView(View):
    def post(self, request, forum_id):
        forum = get_object_or_404(Forum, id=forum_id)
        membership, created = ForumMembership.objects.get_or_create(user=request.user, forum=forum)
        return redirect('forum_detail', forum_id=forum.id)
