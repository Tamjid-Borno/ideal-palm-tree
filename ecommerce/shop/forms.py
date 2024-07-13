from django import forms
from .models import Comment, Reply, Profile, Query, Subscriber, Announcement
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'class': 'form-control'}),
        }
        labels = {
            'text': 'Your Comment',
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['text']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile', 'birthday', 'gender']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address']

class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['message']

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['headline', 'image', 'content']
