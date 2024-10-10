from django import forms
from .models import Post, Comment


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']

    content = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Write your description here',
        'class': 'w-full py-4 px-6 rounded-xl border-2',
        'rows': 5
    }))

    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={
        'class': 'hidden'
    }))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    content = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Add a comment...',
        'class': 'w-full h-11 border rounded-l-xl p-2',
        'rows': 1,
        'style': 'resize: none;'
    }))
