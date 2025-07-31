from django.urls import path
from . import api_views

urlpatterns = [
    # Article API Endpoints
    path(
        "articles/", api_views.article_list_create_api, name="api-article-list-create"
    ),
    path("articles/<int:pk>/", api_views.article_detail_api, name="api-article-detail"),
    path(
        "publishers/<int:publisher_id>/articles/",
        api_views.publisher_articles_api,
        name="api-publisher-articles",
    ),
    path(
        "journalists/<int:journalist_id>/articles/",
        api_views.journalist_articles_api,
        name="api-journalist-articles",
    ),
    # Publisher API Endpoints
    path("publishers/", api_views.publisher_list_api, name="api-publisher-list"),
    path(
        "publishers/<int:pk>/",
        api_views.publisher_detail_api,
        name="api-publisher-detail",
    ),
    # Journalist API Endpoints
    path("journalists/", api_views.journalist_list_api, name="api-journalist-list"),
    path(
        "journalists/<int:pk>/",
        api_views.journalist_detail_api,
        name="api-journalist-detail",
    ),
    # Subscription API Endpoint (for Readers)
    path("subscribe/", api_views.subscribe_api, name="api-subscribe"),
]
