from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Profile, Follow
from posts.models import Post
from .forms import EditProfileForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Create your views here.


# @login_required
# def profile_page(request, username):
#     user = get_object_or_404(User, username=username)
#     profile = get_object_or_404(Profile, user=user)
#     is_following = Follow.objects.filter(
#         follower=request.user, following=profile.user).exists()
#     posts = Post.objects.all().filter(author=profile.user)

#     return render(request, 'users/profile.html', {
#         'profile': profile,
#         'is_following': is_following,
#         'posts': posts
#     })


class ProfilePageView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'users/profile.html'
    context_object_name = 'profile'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object.user
        context['posts'] = Post.objects.filter(
            author=user).order_by('-created_at')
        context['is_following'] = Follow.objects.filter(
            follower=self.request.user, following=user
        ).exists()
        return context


# @login_required
# def edit_profile(request):
#     profile = get_object_or_404(Profile, user=request.user)
#     if request.method == 'POST':
#         form = EditProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()

#         return redirect('users:profile', username=profile.user.username)
#     else:
#         form = EditProfileForm()

#     return render(request, 'users/edit_profile.html', {
#         'form': form,
#         'profile': profile
#     })


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


# def follow_stat(request, username, stat):
#     user = get_object_or_404(User, username=username)
#     profile = get_object_or_404(Profile, user=user)

#     if stat == 'followers':
#         users_list = Follow.objects.filter(
#             following=user).select_related('follower')
#         users = [follow.follower for follow in users_list]
#     elif stat == 'following':
#         users_list = Follow.objects.filter(
#             follower=user).select_related('following')
#         users = [follow.following for follow in users_list]
#     else:
#         return render(request, '404.html', status=404)

#     return render(request, 'users/follow_stat.html', {
#         'profile': profile,
#         'users': users,
#         'stat': stat
#     })


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
