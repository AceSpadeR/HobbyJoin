from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Tag, Post

class RegistrationForm(UserCreationForm):
    profile_pic = forms.ImageField(required=False)
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}), required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'profile_pic', 'color', 'bio', 'tags']

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        if commit:
            user.save()
            profile = UserProfile()
            profile.user = user
            profile.bio = self.cleaned_data['bio']
            if 'profile_pic' in self.files:
                profile.profile_pic = self.files['profile_pic']
            profile.color = self.cleaned_data.get('color', '#FFFFFF')
            profile.save()
            profile.tags.set(self.cleaned_data['tags'])
        return user


class PostForm(forms.ModelForm):
    picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'dark-input'}))
    caption = forms.CharField(widget=forms.Textarea(attrs={'class': 'dark-input'}))
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)

    class Meta:
        model = Post
        fields = ['picture', 'caption', 'tags']

class UserProfileForm(forms.ModelForm):
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}), required=False)
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_pic', 'color', 'tags']