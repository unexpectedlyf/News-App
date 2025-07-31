# news_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
"""
This is the models.py file for the news_app Django application.
It defines the custom User model, Publisher, Article, and Newsletter models.
The User model includes roles for readers, editors, and journalists,
and allows readers to subscribe to publishers and journalists.
"""


class User(AbstractUser):
    """
    Custom User model to include roles and subscription/publication fields.
    """

    ROLE_CHOICES = (
        ("reader", "Reader"),
        ("editor", "Editor"),
        ("journalist", "Journalist"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="reader")

    # Fields for users who have the Reader role
    # A reader can subscribe to multiple publishers and multiple journalists
    subscribed_publishers = models.ManyToManyField(
        "Publisher",
        related_name="subscribers",
        blank=True,
        help_text="Publishers this reader is subscribed to.",
    )
    subscribed_journalists = models.ManyToManyField(
        "self",  # Self-referential ManyToMany field
        related_name="individual_subscribers",  # KEY PART
        blank=True,
        limit_choices_to={
            "role": "journalist"
        },  # Only allow subscriptions to journalists
        help_text="Journalists this reader is subscribed to.",
    )


    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

    # Helper methods to check user roles
    def is_reader(self):
        return self.role == "reader"

    def is_editor(self):
        return self.role == "editor"

    def is_journalist(self):
        return self.role == "journalist"


# Signal receiver to assign users to groups based on their role after saving
@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    if created:
        try:
            group, _ = Group.objects.get_or_create(name=instance.role.capitalize())
            instance.groups.add(group)
            print(f"User {instance.username} assigned to group: {group.name}")
        except Exception as e:
            print(f"Error assigning user {instance.username} to group: {e}")


class Publisher(models.Model):
    """
    Represents a news publisher.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to="publisher_logos/", blank=True, null=True
    )  # Optional logo
    editors = models.ManyToManyField(
        "User",
        related_name="editor_publishers",
        blank=True,
        limit_choices_to={"role": "editor"},
    )
    journalists = models.ManyToManyField(
        "User",
        related_name="journalist_publishers",
        blank=True,
        limit_choices_to={"role": "journalist"},
    )

    class Meta:
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Represents a news article.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    # An article can be published by a Publisher OR an individual Journalist
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,  # If publisher is deleted, articles remain but lose publisher link
        related_name="articles",
        null=True,
        blank=True,
        help_text="The publisher this article belongs to (optional).",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="published_articles",
        limit_choices_to={
            "role__in": ["journalist", "editor"]
        },  # Only journalists or editors can be authors
        help_text="The author of the article (must be a Journalist or Editor).",
    )
    published_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether the article has been approved by an editor for publishing.",
    )
    image = models.ImageField(
        upload_to="article_images/", blank=True, null=True
    )  # Optional article image

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-published_date"]  # Order by newest first

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    Represents a newsletter.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="newsletters",
        limit_choices_to={"role": "journalist"},
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletters"
        ordering = ["-published_date"]  # Order by newest first

    def __str__(self):
        return self.title
