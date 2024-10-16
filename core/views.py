from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, FormView
from django.db.models import Subquery, OuterRef, Exists
from posts.models import Post, Like, Comment
from users.models import Profile, Follow
from posts.forms import CommentForm
from .forms import SignUpForm, LoginForm


class PostListView(ListView):
    model = Post
    template_name = 'core/index.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            following = Follow.objects.filter(
                follower=self.request.user).values('following')
            posts = Post.objects.filter(author__in=Subquery(
                following)).order_by('-created_at')

            user_liked = Like.objects.filter(
                user=self.request.user, post=OuterRef('pk'))
            posts = posts.annotate(user_liked=Exists(user_liked))

            return posts
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
            context['comments'] = Comment.objects.select_related(
                'author').filter(post__in=context['posts'])
            profile = self.request.user.user_profile
            context["saved_posts"] = profile.saved_posts.all()
        return context

    def get_template_names(self):
        if not self.request.user.is_authenticated:
            return ['core/welcome.html']
        return [self.template_name]

    def post(self, request, *args, **kwargs):
        if request.method == 'POST' and request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.author = request.user
                post_id = request.POST.get('post_id')
                new_comment.post = Post.objects.get(id=post_id)
                new_comment.save()

                return HttpResponseRedirect(reverse('core:index'))

            return self.get(request, *args, **kwargs)


class SignUpView(FormView):
    template_name = 'core/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('core:index')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.username.lower()
        user.save()

        Profile.objects.create(user=user)

        login(self.request, user)

        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'core/login.html'

    def get_success_url(self):
        return reverse_lazy('core:index')


@login_required
def custom_logout(request):
    logout(request)
    return redirect('core:index')
