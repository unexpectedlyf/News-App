from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Article, Publisher

User = get_user_model()  # Get the custom user model


class ReaderRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
        )  # Only username and email for initial registration

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "reader"
        if commit:
            user.save()
            # Assign to 'Reader' group
            group, created = Group.objects.get_or_create(name="Reader")
            user.groups.add(group)
        return user


class JournalistRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "journalist"
        if commit:
            user.save()
            # Assign to 'Journalist' group
            group, created = Group.objects.get_or_create(name="Journalist")
            user.groups.add(group)
        return user


class EditorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "editor"
        if commit:
            user.save()
            # Assign to 'Editor' group
            group, created = Group.objects.get_or_create(name="Editor")
            user.groups.add(group)
        return user


class UserLoginForm(AuthenticationForm):
    # This form is for logging in existing users
    pass


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "publisher",
            "image",
        ]  # Author and is_approved set by view/admin
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 10}
            ),  # Make content textarea larger
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Get the current user from kwargs
        super().__init__(*args, **kwargs)
     