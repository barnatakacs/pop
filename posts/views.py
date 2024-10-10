from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import CreateView
from .forms import NewPostForm
from .models import Post, Like, Comment
from .forms import CommentForm
from django.views.generic.edit import DeleteView
from django.http import HttpResponseRedirect
from django.db.models import Count

# Create your views here.


# def new(request):
#     if request.method == 'POST':
#         form = NewPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.save()
#             return redirect('core:index')
#     else:
#         form = NewPostForm()

#     return render(request, 'posts/new.html', {
#         'form': form
#     })


class NewPostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = NewPostForm
    template_name = 'posts/new.html'
    success_url = reverse_lazy('core:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


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
        else:
            return redirect(self.get_success_url())

    def test_func(self):
        comment_pk = self.kwargs.get('comment_pk')
        comment = Comment.objects.get(pk=comment_pk)
        return self.request.user == comment.author


class ExplorePageView(LoginRequiredMixin, ListView):
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

        return filtered_posts


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.get_object()

        context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.select_related(
            'author').filter(post=post)

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
