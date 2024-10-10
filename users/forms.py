from django import forms
from .models import Profile


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']

    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Bio',
            'class': 'w-full py-4 px-6 rounded-xl border-2',
            'rows': 5
        }))

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'hidden'
        }))
