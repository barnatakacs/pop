from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from .forms import NewPostForm
from .forms import CommentForm
from .models import Post, Like, Comment


class NewPostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = NewPostForm
    template_name = 'posts/new.html'
    success_url = reverse_lazy('core:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@login_required
def like(request, pk, redirection):
    post_to_like = get_object_or_404(Post, pk=pk)

    like_instance, created = Like.objects.get_or_create(
        user=request.user,
        post=post_to_like
    )

    if not created:
        like_instance.delete()

    if redirection == 'detail':
        return redirect('posts:detail', pk=pk)
    elif redirection == 'profile':
        return redirect('users:profile', username=request.user.username)
    else:
        return redirect('core:index')


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    success_url = 'core:index'

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        comment_pk = self.kwargs.get('comment_pk')
        self.object = Comment.objects.get(pk=comment_pk)
        self.object.delete()

        redirection = self.kwargs.get('redirection')
        post_pk = self.kwargs.get('post_pk')

        if redirection == 'detail':
            return redirect('posts:detail', pk=post_pk)
        elif redirection == 'profile':
            post = get_object_or_404(Post, pk=post_pk)
            return redirect('users:profile', username=post.author.username)
        else:
            return redirect(self.get_success_url())

    def test_func(self):
        comment_pk = self.kwargs.get('comment_pk')
        comment = Comment.objects.get(pk=comment_pk)
        return self.request.user == comment.author


class ExplorePageView(ListView):
    model = Post
    template_name = 'posts/explore.html'
    context_object_name = 'posts'

    def get_queryset(self):
        last_1000_posts = Post.objects.annotate(
            like_count=Count('likes')).order_by('-created_at')[:1000]

        last_1000_posts_list = list(last_1000_posts)

        average_like_count = sum(post.like_count for post in last_1000_posts_list) / \
            len(last_1000_posts_list) if last_1000_posts_list else 0

        filtered_posts = [
            post for post in last_1000_posts_list if post.like_count >= average_like_count]

        search_query = self.request.GET.get('explore', '').strip()

        if search_query:
            filtered_posts = [
                post for post in filtered_posts if search_query.lower() in post.content.lower() or search_query.lower() in post.author.username.lower()]

        return filtered_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Explore'
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.get_object()

        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
            context['comments'] = Comment.objects.select_related(
                'author').filter(post=post)
            profile = self.request.user.user_profile
            context["saved_posts"] = profile.saved_posts.all()

        if self.request.user.is_authenticated:
            context['user_liked'] = Like.objects.filter(
                post=post, user=self.request.user).exists()

        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

        return redirect(reverse('posts:detail', kwargs={'pk': post.id}))


class SavedPageView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/explore.html'
    context_object_name = 'posts'

    def get_queryset(self):
        profile = self.request.user.user_profile
        saved_posts = profile.saved_posts.all()
        return saved_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Saved'
        return context


@login_required
def save(request, pk, redirection):
    post_to_save = get_object_or_404(Post, pk=pk)
    profile = request.user.user_profile

    if post_to_save in profile.saved_posts.all():
        profile.saved_posts.remove(post_to_save)
    else:
        profile.saved_posts.add(post_to_save)

    if redirection == 'detail':
        return redirect('posts:detail', pk=pk)
    elif redirection == 'profile':
        return redirect('users:profile', username=post_to_save.author.username)
    else:
        return redirect('core:index')


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post

    def get_success_url(self):
        username = self.object.author.username
        return reverse('users:profile', kwargs={'username': username})
