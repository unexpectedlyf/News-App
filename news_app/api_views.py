from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated  # For authenticated users
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q  # Used for complex queries

from .models import Article, Publisher, User  # Import all needed models
from .serializers import ArticleSerializer, PublisherSerializer, JournalistSerializer

# from .utils import tweet_article_approved, send_article_notification_email


# --- Publisher API Views ---
@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Requires authentication to view publishers
def publisher_list_api(request):
    """
    API endpoint to list all publishers.
    Accessible by any authenticated user.
    """
    publishers = Publisher.objects.all()
    serializer = PublisherSerializer(publishers, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes(
    [IsAuthenticated]
)  # Requires authentication to view publisher details
def publisher_detail_api(request, pk):
    """
    API endpoint to retrieve details of a single publisher.
    Accessible by any authenticated user.
    """
    publisher = get_object_or_404(Publisher, pk=pk)
    serializer = PublisherSerializer(publisher)
    return Response(serializer.data)


# --- Journalist API Views ---
@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Requires authentication to view journalists
def journalist_list_api(request):
    """
    API endpoint to list all journalists (users with role='journalist').
    Accessible by any authenticated user.
    """
    journalists = User.objects.filter(role="journalist")
    serializer = JournalistSerializer(journalists, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes(
    [IsAuthenticated]
)  # Requires authentication to view journalist details
def journalist_detail_api(request, pk):
    """
    API endpoint to retrieve details of a single journalist.
    Accessible by any authenticated user.
    """
    journalist = get_object_or_404(User, pk=pk, role="journalist")
    serializer = JournalistSerializer(journalist)
    return Response(serializer.data)


# --- Article API Views ---


@api_view(["GET", "POST"])
@permission_classes(
    [IsAuthenticated]
)  # Authenticated users can view, Journalists can create
def article_list_create_api(request):
    """
    API endpoint to list approved articles (for all authenticated users)
    or create a new article (for authenticated journalists).
    """
    if request.method == "GET":
        # API clients (readers, etc.) can only retrieve APPROVED articles
        articles = Article.objects.filter(is_approved=True).order_by("-published_date")
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        # Only users with the 'journalist' role can create articles via API
        if not request.user.is_journalist():
            return Response(
                {
                    "detail": "Permission denied. Only journalists can create articles via API."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Pass request.user to the serializer context if you need it for custom validation
        # The author will be set by the view based on the authenticated user.
        serializer = ArticleSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            # Set the author of the article to the currently authenticated journalist
            # New articles are not approved by default; an editor must approve them.
            article = serializer.save(author=request.user, is_approved=False)

            # Email notifications and tweeting will be handled by Django signals
            # when the article's `is_approved` status changes to True by an editor.

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes(
    [IsAuthenticated]
)  # Authenticated users can view. Editors/Journalists can manage.
def article_detail_api(request, pk):
    """
    API endpoint to retrieve, update, or delete a specific article.
    GET: Accessible if approved, or if user is the author/editor.
    PUT/DELETE: Only by the author or an editor.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.method == "GET":
        # Allow viewing if:
        # 1. The article is approved (for any authenticated user)
        # 2. The current user is the author of the article
        # 3. The current user is an editor
        if not article.is_approved and not (
            request.user == article.author or request.user.is_editor()
        ):
            return Response(
                {
                    "detail": "Permission denied. Article not approved or you are not authorized to view unapproved articles."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    elif request.method == "PUT":
        # Only the author or an editor can update an article
        if not (request.user == article.author or request.user.is_editor()):
            return Response(
                {
                    "detail": "Permission denied. You are not the author or an editor of this article."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prevent non-editors from changing 'is_approved' status via API
        if "is_approved" in request.data and not request.user.is_editor():
            return Response(
                {
                    "detail": "Only editors can change the approval status of an article via API."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ArticleSerializer(
            article, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            # Ensure the author cannot be changed via API update
            if (
                "author" in request.data
                and int(request.data["author"]) != article.author.id
            ):
                return Response(
                    {"detail": "Author cannot be changed via API update."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        # Only the author or an editor can delete an article
        if not (request.user == article.author or request.user.is_editor()):
            return Response(
                {
                    "detail": "Permission denied. You are not the author or an editor of this article."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def publisher_articles_api(request, publisher_id):
    """
    API endpoint to retrieve approved articles for a specific publisher.
    Accessible by any authenticated user.
    """
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    # Only return approved articles for API clients
    articles = Article.objects.filter(publisher=publisher, is_approved=True).order_by(
        "-published_date"
    )
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def journalist_articles_api(request, journalist_id):
    """
    API endpoint to retrieve approved articles for a specific journalist.
    Accessible by any authenticated user.
    """
    journalist = get_object_or_404(User, pk=journalist_id, role="journalist")
    # Only return approved articles for API clients
    articles = Article.objects.filter(author=journalist, is_approved=True).order_by(
        "-published_date"
    )
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)


# API endpoint for a client to subscribe/unsubscribe (optional, but good for API)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def subscribe_api(request):
    """
    API endpoint for a reader to subscribe/unsubscribe to a publisher or journalist.
    Requires 'type' ('publisher' or 'journalist') and 'id' of the target,
    and 'action' ('subscribe' or 'unsubscribe') in the request body.
    """
    # Only users with the 'reader' role can manage subscriptions via API
    if not request.user.is_reader():
        return Response(
            {
                "detail": "Permission denied. Only readers can manage subscriptions via API."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    subscription_type = request.data.get("type")
    target_id = request.data.get("id")
    action = request.data.get("action", "subscribe")  # Default action is 'subscribe'

    if not subscription_type or not target_id:
        return Response(
            {
                "detail": 'Missing "type" (publisher/journalist) or "id" in request body.'
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        target_id = int(target_id)
    except ValueError:
        return Response(
            {"detail": "ID must be an integer."}, status=status.HTTP_400_BAD_REQUEST
        )

    if subscription_type == "publisher":
        target_obj = get_object_or_404(Publisher, pk=target_id)
        if action == "subscribe":
            if request.user.subscribed_publishers.filter(pk=target_id).exists():
                return Response(
                    {"detail": f"Already subscribed to {target_obj.name}."},
                    status=status.HTTP_409_CONFLICT,
                )
            request.user.subscribed_publishers.add(target_obj)
            return Response(
                {"detail": f"Successfully subscribed to {target_obj.name}."},
                status=status.HTTP_200_OK,
            )
        elif action == "unsubscribe":
            if not request.user.subscribed_publishers.filter(pk=target_id).exists():
                return Response(
                    {"detail": f"Not subscribed to {target_obj.name}."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            request.user.subscribed_publishers.remove(target_obj)
            return Response(
                {"detail": f"Successfully unsubscribed from {target_obj.name}."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": 'Invalid action. Must be "subscribe" or "unsubscribe".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    elif subscription_type == "journalist":
        target_obj = get_object_or_404(
            User, pk=target_id, role="journalist"
        )  # Ensure it's a journalist user
        if action == "subscribe":
            if request.user.subscribed_journalists.filter(pk=target_id).exists():
                return Response(
                    {"detail": f"Already subscribed to {target_obj.username}."},
                    status=status.HTTP_409_CONFLICT,
                )
            request.user.subscribed_journalists.add(target_obj)
            return Response(
                {"detail": f"Successfully subscribed to {target_obj.username}."},
                status=status.HTTP_200_OK,
            )
        elif action == "unsubscribe":
            if not request.user.subscribed_journalists.filter(pk=target_id).exists():
                return Response(
                    {"detail": f"Not subscribed to {target_obj.username}."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            request.user.subscribed_journalists.remove(target_obj)
            return Response(
                {"detail": f"Successfully unsubscribed from {target_obj.username}."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": 'Invalid action. Must be "subscribe" or "unsubscribe".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    else:
        return Response(
            {
                "detail": 'Invalid subscription type. Must be "publisher" or "journalist".'
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
