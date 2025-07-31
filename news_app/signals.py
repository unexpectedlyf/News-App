from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article, User  # Import User model
from .utils import send_article_notification_email  # Import the email utility function
from django.conf import settings  # Import settings to check for Twitter keys


# This signal receiver will be triggered every time an Article object is saved.
@receiver(post_save, sender=Article)
def article_approved_notification(sender, instance, created, **kwargs):
    """
    Sends email notifications to subscribers when an article is approved.
    Also triggers a tweet if the article is newly approved and Twitter keys are configured.
    """

    if created:
        return

   
    if instance.is_approved:
        

        # --- Send emails to subscribers ---
        # Subscribers to the publisher (if article has a publisher)
        if instance.publisher:
            # Get all users subscribed to this publisher
            publisher_subscribers = instance.publisher.subscribers.all()
            for user in publisher_subscribers:
                send_article_notification_email(user.email, instance)
                print(
                    f"Sent email to publisher subscriber: {user.email} for article '{instance.title}'"
                )

        # Subscribers to the author (journalist)
        # The 'individual_subscribers' related_name is defined on the User model
        # This correctly fetches users who have subscribed to this journalist.
        if (
            instance.author and instance.author.is_journalist()
        ):  # Ensure author exists and is a journalist
            journalist_subscribers = instance.author.individual_subscribers.all()
            for user in journalist_subscribers:
                send_article_notification_email(user.email, instance)
                print(
                    f"Sent email to journalist subscriber: {user.email} for article '{instance.title}'"
                )

        # --- Trigger tweet  ---
        from .utils import tweet_article_approved  # Re-import to be explicit in signal

        # Only tweet if the article was newly approved in this save operation
        # (The `approve_article` view ensures this logic runs only once)
        if (
            hasattr(instance, "_previous_is_approved")
            and not instance._previous_is_approved
            and instance.is_approved
        ):
            tweet_article_approved(instance)
        elif not hasattr(instance, "_previous_is_approved") and instance.is_approved:
        
            pass  # We will rely on the view for tweeting for now, or refine this signal.
            
