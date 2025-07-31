from django.urls import path
from . import views
from django.contrib.auth import (
    views as auth_views,
)  # Import Django's default auth views for password reset

urlpatterns = [
    # General/Reader Views
    path(
        "", views.ArticleListView.as_view(), name="home"
    ),  # Home page showing approved articles
    path(
        "articles/<int:pk>/", views.ArticleDetailView.as_view(), name="article-detail"
    ),
    path("publishers/", views.PublisherListView.as_view(), name="publisher-list"),
    path("journalists/", views.JournalistListView.as_view(), name="journalist-list"),
    # User Authentication & Registration
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path(
        "register/reader/",
        views.ReaderRegistrationView.as_view(),
        name="register-reader",
    ),
    path(
        "register/journalist/",
        views.JournalistRegistrationView.as_view(),
        name="register-journalist",
    ),
    path(
        "register/editor/",
        views.EditorRegistrationView.as_view(),
        name="register-editor",
    ),
    # Password Reset URLs (using custom views for templates/messages)
    path(
        "password-reset/", views.password_reset_request, name="password-reset-request"
    ),
    path(
        "password-reset/done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password-reset-done",
    ),
    
    path(
        "password-reset-confirm/<int:uidb64>/<str:token>/",
        views.password_reset_confirm,
        name="password-reset-confirm",
    ),
    path(
        "password-reset/complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password-reset-complete",
    ),
    # Journalist Specific Views
    path(
        "journalist/articles/",
        views.JournalistArticleListView.as_view(),
        name="journalist-articles",
    ),
    path(
        "journalist/articles/create/",
        views.JournalistArticleCreateView.as_view(),
        name="article-create",
    ),
    path(
        "journalist/articles/<int:pk>/edit/",
        views.JournalistArticleUpdateView.as_view(),
        name="article-edit",
    ),
    path(
        "journalist/articles/<int:pk>/delete/",
        views.JournalistArticleDeleteView.as_view(),
        name="article-delete",
    ),
    # Editor Specific Views
    path(
        "editor/review/",
        views.EditorArticleReviewList.as_view(),
        name="editor-review-list",
    ),
    path("editor/approve/<int:pk>/", views.approve_article, name="approve-article"),
    path(
        "editor/articles/<int:pk>/edit/",
        views.EditorArticleUpdateView.as_view(),
        name="editor-article-edit",
    ),
    path(
        "editor/articles/<int:pk>/delete/",
        views.EditorArticleDeleteView.as_view(),
        name="editor-article-delete",
    ),
    # Subscription Management (for Readers)
    path(
        "subscribe/publisher/<int:pk>/",
        views.subscribe_publisher,
        name="subscribe-publisher",
    ),
    path(
        "unsubscribe/publisher/<int:pk>/",
        views.unsubscribe_publisher,
        name="unsubscribe-publisher",
    ),
    path(
        "subscribe/journalist/<int:pk>/",
        views.subscribe_journalist,
        name="subscribe-journalist",
    ),
    path(
        "unsubscribe/journalist/<int:pk>/",
        views.unsubscribe_journalist,
        name="unsubscribe-journalist",
    ),
]
