# news_app/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import tweepy  


def send_article_notification_email(recipient_email, article):
    """
    Sends an email notification about a new approved article.
    """
    subject = f"New Approved Article: {article.title}"
    html_message = render_to_string(
        "news_app/article_notification_email.html",
        {
            "article": article,
        },
    )
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Successfully sent article notification email to {recipient_email}")
    except Exception as e:
        print(f"Error sending article notification email to {recipient_email}: {e}")


def tweet_article_approved(article):
    """
    Tweets about a newly approved article if Twitter API keys are configured.
    """
    if not all(
        [
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET,
        ]
    ):
        print("Twitter API keys are not fully configured. Skipping tweet.")
        return

    try:
        auth = tweepy.OAuthHandler(
            settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET
        )
        auth.set_access_token(
            settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)

        article_url = (
            f"http://127.0.0.1:8000/articles/{article.pk}/"  # Adjust URL as needed
        )
        tweet_text = f"📰 New Article Approved! '{article.title}' by {article.author.username}. Read it here: {article_url}"

        # Truncate tweet_text if it exceeds Twitter's limit (280 characters for text, URLs are shortened)
        # This is a basic truncation, consider actual Twitter URL shortening length (23 chars)
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        media_path = None
        if article.image:
            # Construct absolute path to media file
            media_path = os.path.join(settings.MEDIA_ROOT, str(article.image))
            if not os.path.exists(media_path):
                print(
                    f"Warning: Article image not found at {media_path}. Tweeting without image."
                )
                media_path = None

        if media_path:
            media = api.media_upload(media_path)
            api.update_status(status=tweet_text, media_ids=[media.media_id])
            print(f"Tweeted with image: {tweet_text}")
        else:
            api.update_status(status=tweet_text)
            print(f"Tweeted: {tweet_text}")

    except tweepy.TweepyException as e:
        print(f"Error tweeting article '{article.title}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred while trying to tweet: {e}")
