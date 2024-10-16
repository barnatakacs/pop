from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import OuterRef, Exists
from .models import Profile, Follow
from .forms import EditProfileForm
from posts.models import Post, Like, Comment
from posts.forms import CommentForm


class ProfilePageView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'users/profile.html'
    context_object_name = 'profile'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object.user
        posts = Post.objects.filter(
            author=user).order_by('-created_at')

        user_liked = Like.objects.filter(
            user=self.request.user, post=OuterRef('pk'))
        posts = posts.annotate(user_liked=Exists(user_liked))

        context['posts'] = posts

        context['is_following'] = Follow.objects.filter(
            follower=self.request.user, following=user
        ).exists()

        profile = self.request.user.user_profile
        context["saved_posts"] = profile.saved_posts.all()

        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
            context['comments'] = Comment.objects.select_related(
                'author').filter(post__in=context['posts'])
            profile = self.request.user.user_profile

        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST' and request.user.is_authenticated:

            comment_form = CommentForm(request.POST)

            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.author = request.user
                post_id = request.POST.get('post_id')
                new_comment.post = Post.objects.get(id=post_id)
                new_comment.save()

                return redirect('users:profile', username=self.get_object().user.username)

            return self.get(request, *args, **kwargs)


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = EditProfileForm
    template_name = 'users/edit_profile.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context


@login_required
def follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    current_user = get_object_or_404(User, username=request.user.username)

    if current_user == user_to_follow:
        return redirect('users:profile', username)

    follow_instance, created = Follow.objects.get_or_create(
        follower=current_user,
        following=user_to_follow
    )

    if not created:
        follow_instance.delete()

    return redirect('users:profile', username=username)


class FollowStatView(ListView):
    template_name = 'users/follow_stat.html'
    context_object_name = 'users'

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.profile = get_object_or_404(Profile, user=self.user)
        stat = self.kwargs['stat']

        if stat == 'followers':
            users_list = Follow.objects.filter(
                following=self.user).select_related('follower')
            return [follow.follower for follow in users_list]
        elif stat == 'following':
            users_list = Follow.objects.filter(
                follower=self.user).select_related('following')
            return [follow.following for follow in users_list]
        else:
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['stat'] = self.kwargs['stat']
        return context
