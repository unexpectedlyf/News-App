from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponse, Http404  # Import Http404 for ArticleDetailView

from .models import User, Publisher, Article
from .forms import (
    ReaderRegistrationForm,
    JournalistRegistrationForm,
    EditorRegistrationForm,
    UserLoginForm,
    ArticleForm,
)
from .utils import (
    tweet_article_approved,
    send_article_notification_email,
)  # Import Twitter and Email helpers

# Get the custom user model here
CustomUser = get_user_model()


# --- Mixins for Role-Based Access Control ---
class IsReaderMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_reader()

    def handle_no_permission(self):
        messages.error(self.request, "You must be a Reader to access this page.")
        return redirect("home")


class IsEditorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_editor()

    def handle_no_permission(self):
        messages.error(self.request, "You must be an Editor to access this page.")
        return redirect("home")


class IsJournalistMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_journalist()

    def handle_no_permission(self):
        messages.error(self.request, "You must be a Journalist to access this page.")
        return redirect("home")


# --- Authentication Views ---
class UserLoginView(LoginView):
    template_name = "news_app/login.html"
    authentication_form = UserLoginForm

    def get_success_url(self):
        messages.success(self.request, f"Welcome, {self.request.user.username}!")
        return reverse_lazy("home")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


class ReaderRegistrationView(CreateView):
    model = User
    form_class = ReaderRegistrationForm
    template_name = "news_app/registration_form.html"
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_type"] = "Reader"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, "Reader account created successfully. Please log in."
        )
        return super().form_valid(form)


class JournalistRegistrationView(CreateView):
    model = User
    form_class = JournalistRegistrationForm
    template_name = "news_app/registration_form.html"
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_type"] = "Journalist"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, "Journalist account created successfully. Please log in."
        )
        return super().form_valid(form)


class EditorRegistrationView(CreateView):
    model = User
    form_class = EditorRegistrationForm
    template_name = "news_app/registration_form.html"
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_type"] = "Editor"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, "Editor account created successfully. Please log in."
        )
        return super().form_valid(form)


# --- Password Reset Views ---
def password_reset_request(request):
    if request.method == "POST":
        email_address = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email_address)
            # Generate token and UID for the password reset link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse_lazy(
                    "password-reset-confirm", kwargs={"uidb64": user.pk, "token": token}
                )  # Using user.pk directly as uidb64
            )

            # Send email
            subject = "Password Reset Request for News App"
            html_message = render_to_string(
                "news_app/password_reset_email.html",
                {
                    "user": user,
                    "reset_url": reset_url,
                },
            )
            plain_message = strip_tags(html_message)
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
            )
            messages.success(
                request,
                "Password reset email sent successfully. Please check your inbox.",
            )
            return redirect("password-reset-done")
        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with that email address.")
            return render(
                request,
                "news_app/password_reset_request.html",
                {"email": email_address},
            )
    return render(request, "news_app/password_reset_request.html")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "news_app/password_reset_done.html"


def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the user ID
        # user_id = force_str(urlsafe_base64_decode(uidb64)) # This is the standard way with uidb64

        user_id = uidb64
        user = CustomUser.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password and new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(
                    request,
                    "Your password has been reset successfully. You can now log in.",
                )
                return redirect("password-reset-complete")
            else:
                messages.error(request, "Passwords do not match or are empty.")
        return render(
            request,
            "news_app/password_reset_confirm.html",
            {"uidb64": uidb64, "token": token},
        )
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect("password-reset-request")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "news_app/password_reset_complete.html"


# --- Article Views (Reader/General Access) ---
class ArticleListView(ListView):
    model = Article
    template_name = "news_app/article_list.html"
    context_object_name = "articles"
    paginate_by = 10  # Optional: for pagination

    def get_queryset(self):
        # Only show approved articles to general readers
        return Article.objects.filter(is_approved=True).order_by("-published_date")


class ArticleDetailView(ListView):
    model = Article
    template_name = "news_app/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        # Get the article by PK
        pk = self.kwargs["pk"]
        article = get_object_or_404(Article, pk=pk)

        # Allow access if:
        # 1. The article is approved (for everyone)
        # 2. The current user is the author (journalist) of the article
        # 3. The current user is an editor
        if (
            article.is_approved
            or (
                self.request.user.is_authenticated
                and self.request.user == article.author
            )
            or (self.request.user.is_authenticated and self.request.user.is_editor())
        ):
            return Article.objects.filter(
                pk=pk
            )  # Return a queryset containing the article
        else:
            # If none of the above conditions are met, raise 404
            raise Http404("Article not found or not approved for your access level.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = context[
            "article"
        ].first()  # Get the single article object from the queryset

        if not article:
            raise Http404("Article not found or not approved.")

        context["article"] = article  # Set the single article object in context

        # Pre-calculate subscription status for the current user if they are a reader
        context["is_subscribed_to_publisher"] = False
        context["is_subscribed_to_journalist"] = False
        context["show_journalist_subscribe_options"] = False  # New flag

        if self.request.user.is_authenticated and self.request.user.is_reader():
            if article.publisher:
                context["is_subscribed_to_publisher"] = (
                    self.request.user.subscribed_publishers.filter(
                        pk=article.publisher.pk
                    ).exists()
                )

            # Check if the user is a reader and not the author of the article
            if not (
                self.request.user.is_journalist()
                and self.request.user.pk == article.author.pk
            ):
                context["is_subscribed_to_journalist"] = (
                    self.request.user.subscribed_journalists.filter(
                        pk=article.author.pk
                    ).exists()
                )
                context["show_journalist_subscribe_options"] = True  # Set the new flag

        return context


# --- Journalist Views ---
class JournalistArticleCreateView(LoginRequiredMixin, IsJournalistMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "news_app/article_form.html"
    success_url = reverse_lazy("journalist-articles")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass the current user to the form
        return kwargs

    def form_valid(self, form):
        form.instance.author = (
            self.request.user
        )  # Set the author to the logged-in journalist
        # Newly created articles are not approved by default, an editor must approve them
        form.instance.is_approved = False
        messages.success(
            self.request,
            "Article submitted for review. An editor will approve it shortly.",
        )
        return super().form_valid(form)


class JournalistArticleListView(LoginRequiredMixin, IsJournalistMixin, ListView):
    model = Article
    template_name = "news_app/journalist_article_list.html"
    context_object_name = "my_articles"
    paginate_by = 10

    def get_queryset(self):
        # Show only articles authored by the current journalist
        return Article.objects.filter(author=self.request.user).order_by(
            "-published_date"
        )


class JournalistArticleUpdateView(LoginRequiredMixin, IsJournalistMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "news_app/article_form.html"
    success_url = reverse_lazy("journalist-articles")

    def get_queryset(self):
        # Ensure a journalist can only update their own articles
        return Article.objects.filter(author=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Article updated successfully.")
        return super().form_valid(form)


class JournalistArticleDeleteView(LoginRequiredMixin, IsJournalistMixin, DeleteView):
    model = Article
    template_name = "news_app/article_confirm_delete.html"
    success_url = reverse_lazy("journalist-articles")

    def get_queryset(self):
        # Ensure a journalist can only delete their own articles
        return Article.objects.filter(author=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Article deleted successfully.")
        return super().form_valid(form)


# --- Editor Views ---
class EditorArticleReviewList(LoginRequiredMixin, IsEditorMixin, ListView):
    model = Article
    template_name = "news_app/editor_review_list.html"
    context_object_name = "articles_for_review"
    paginate_by = 10

    def get_queryset(self):
        # Editors see all articles, including unapproved ones
        return Article.objects.all().order_by("-published_date")


@login_required
@user_passes_test(lambda u: u.is_editor())
def approve_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        if (
            not article.is_approved
        ):  # Only contunue if the article is not already approved
            # Set a temporary flag to indicate this approval came from the view
            article._just_approved = True
            article.is_approved = True
            article.save()  # This save will trigger the post_save signal
            messages.success(request, f'Article "{article.title}" approved.')

            # The tweet_article_approved and email sending logic will now be handled by the signal.
            # Removed direct calls to tweet_article_approved and email loops from here.
        else:
            messages.info(request, f'Article "{article.title}" was already approved.')

        return redirect("editor-review-list")
    return render(request, "news_app/approve_confirm.html", {"article": article})


# Editor can also update/delete any article
class EditorArticleUpdateView(LoginRequiredMixin, IsEditorMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "news_app/article_form.html"
    success_url = reverse_lazy("editor-review-list")  # Redirect back to review list

    def form_valid(self, form):
        messages.success(self.request, "Article updated successfully by editor.")
        return super().form_valid(form)


class EditorArticleDeleteView(LoginRequiredMixin, IsEditorMixin, DeleteView):
    model = Article
    template_name = "news_app/article_confirm_delete.html"
    success_url = reverse_lazy("editor-review-list")

    def form_valid(self, form):
        messages.success(self.request, "Article deleted successfully by editor.")
        return super().form_valid(form)


# --- Subscription Management Views (for Readers) ---
@login_required
@user_passes_test(lambda u: u.is_reader())
def subscribe_publisher(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.user.subscribed_publishers.filter(pk=pk).exists():
        messages.info(request, f"You are already subscribed to {publisher.name}.")
    else:
        request.user.subscribed_publishers.add(publisher)
        messages.success(request, f"Successfully subscribed to {publisher.name}.")
    return redirect(
        "publisher-list"
    )  # Redirect back to publisher list or a profile page


@login_required
@user_passes_test(lambda u: u.is_reader())
def unsubscribe_publisher(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.user.subscribed_publishers.filter(pk=pk).exists():
        request.user.subscribed_publishers.remove(publisher)
        messages.success(request, f"Successfully unsubscribed from {publisher.name}.")
    else:
        messages.info(request, f"You were not subscribed to {publisher.name}.")
    return redirect("publisher-list")


@login_required
@user_passes_test(lambda u: u.is_reader())
def subscribe_journalist(request, pk):
    journalist = get_object_or_404(User, pk=pk, role="journalist")
    if request.user.subscribed_journalists.filter(pk=pk).exists():
        messages.info(request, f"You are already subscribed to {journalist.username}.")
    else:
        request.user.subscribed_journalists.add(journalist)
        messages.success(request, f"Successfully subscribed to {journalist.username}.")
    return redirect("journalist-list")  # Redirect to a list of journalists


@login_required
@user_passes_test(lambda u: u.is_reader())
def unsubscribe_journalist(request, pk):
    journalist = get_object_or_404(User, pk=pk, role="journalist")
    if request.user.subscribed_journalists.filter(pk=pk).exists():
        request.user.subscribed_journalists.remove(journalist)
        messages.success(
            request, f"Successfully unsubscribed from {journalist.username}."
        )
    else:
        messages.info(request, f"You were not subscribed to {journalist.username}.")
    return redirect("journalist-list")


class PublisherListView(ListView):
    model = Publisher
    template_name = "news_app/publisher_list.html"
    context_object_name = "publishers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.is_reader():
            # Annotate each publisher with whether the current user is subscribed
            for publisher in context["publishers"]:
                publisher.is_subscribed_by_user = (
                    self.request.user.subscribed_publishers.filter(
                        pk=publisher.pk
                    ).exists()
                )
        return context


class JournalistListView(ListView):
    model = User
    template_name = "news_app/journalist_list.html"
    context_object_name = "journalists"

    def get_queryset(self):
        return User.objects.filter(role="journalist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.is_reader():
            # Annotate each journalist with whether the current user is subscribed
            for journalist in context["journalists"]:
                journalist.is_subscribed_by_user = (
                    self.request.user.subscribed_journalists.filter(
                        pk=journalist.pk
                    ).exists()
                )
        return context
