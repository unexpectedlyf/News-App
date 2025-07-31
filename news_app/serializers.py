from rest_framework import serializers
from .models import Article, Publisher, User  # Import User to the import list


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for the Publisher model.
    Converts Publisher instances to JSON and vice-versa.
    """

    class Meta:
        model = Publisher
        fields = "__all__"  # Include all fields from the Publisher model
        read_only_fields = ["id"]  # The ID field is ussually auto-generated and read-only


class JournalistSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, specifically for Journalists.
    Exposes only relevant fields for API clients.
    """

    class Meta:
        model = User  # 'User' is now defined due to the import
        fields = [
            "id",
            "username",
            "email",
        ]  # Only expose ID, username, and email for journalists
        read_only_fields = [
            "id",
            "username",
            "email",
        ]  # These fields are read-only via the API


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model.
    Includes related fields for better readability in API responses.
    """

    # Custom read-only fields to display names/usernames instead of just foreign key IDs
    publisher_name = serializers.CharField(source="publisher.name", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "published_date",
            "is_approved",
            "publisher",
            "publisher_name",  # Include both publisher ID and its name
            "author",
            "author_username",  # Include both author ID and its username
            "image",  # Include the image field
        ]
        read_only_fields = [
            "id",
            "published_date",
            "is_approved",  
            "publisher_name",
            "author_username",  
        ]
