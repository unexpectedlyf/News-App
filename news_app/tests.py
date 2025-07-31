from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from news_app.models import Article, Publisher

User = get_user_model()  # Get the custom User model


class NewsAPITests(APITestCase):
    """
    Tests for the RESTful API endpoints in the news_app.
    """

    def setUp(self):
        """
        Set up test data and clients for all API tests.
        """
        self.client = APIClient()

        # Create test users with different roles
        self.reader_user = User.objects.create_user(
            username="testreader",
            email="reader@example.com",
            password="readerpassword",
            role="reader",
        )
        self.journalist_user = User.objects.create_user(
            username="testjournalist",
            email="journalist@example.com",
            password="journalistpassword",
            role="journalist",
        )
        self.editor_user = User.objects.create_user(
            username="testeditor",
            email="editor@example.com",
            password="editorpassword",
            role="editor",
            is_staff=True,
        )

        # Create test publishers
        self.publisher1 = Publisher.objects.create(
            name="Tech News Inc", description="Latest in tech"
        )
        self.publisher2 = Publisher.objects.create(
            name="World Affairs Daily", description="Global news"
        )

        # Create test articles
        self.article1 = Article.objects.create(
            title="AI Breakthrough",
            content="Scientists made a new AI breakthrough.",
            publisher=self.publisher1,
            author=self.journalist_user,
            is_approved=True,  # Approved article
        )
        self.article2 = Article.objects.create(
            title="Global Economy Report",
            content="Analysis of current economic trends.",
            publisher=self.publisher2,
            author=self.journalist_user,
            is_approved=True,  # Approved article
        )
        self.article3 = Article.objects.create(
            title="Unapproved Local News",
            content="Details about a local event.",
            publisher=self.publisher1,
            author=self.journalist_user,
            is_approved=False,  # Unapproved article
        )
        self.article4 = Article.objects.create(
            title="Editor Approved Article",
            content="An article approved by an editor.",
            publisher=self.publisher2,
            author=self.editor_user,  # Article by an editor
            is_approved=True,
        )

        # URLs for API endpoints
        self.article_list_url = reverse("api-article-list-create")
        self.publisher_list_url = reverse("api-publisher-list")
        self.journalist_list_url = reverse("api-journalist-list")
        self.subscribe_url = reverse("api-subscribe")

    # --- Authentication and Permission Tests ---

    def test_unauthenticated_access_to_api(self):
        """
        Ensure unauthenticated users cannot access any API endpoints.
        """
        response = self.client.get(self.article_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.publisher_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.journalist_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_access_allowed(self):
        """
        Ensure authenticated users can access general GET endpoints.
        """
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get(self.article_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.publisher_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.journalist_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Article API Tests ---

    def test_article_list_retrieval(self):
        """
        Test that only approved articles are returned in the general article list.
        """
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get(self.article_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect 3 approved articles (article1, article2, article4)
        self.assertEqual(len(response.data), 3)
        article_titles = [article["title"] for article in response.data]
        self.assertIn("AI Breakthrough", article_titles)
        self.assertIn("Global Economy Report", article_titles)
        self.assertIn("Editor Approved Article", article_titles)
        self.assertNotIn("Unapproved Local News", article_titles)

    def test_article_detail_retrieval_approved(self):
        """
        Test retrieving an approved article by its ID.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "AI Breakthrough")

    def test_article_detail_retrieval_unapproved_by_unauthorized(self):
        """
        Test that an unapproved article cannot be retrieved by a non-author/non-editor.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_article_detail_retrieval_unapproved_by_author(self):
        """
        Test that an unapproved article CAN be retrieved by its author.
        """
        self.client.force_authenticate(user=self.journalist_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Unapproved Local News")

    def test_article_detail_retrieval_unapproved_by_editor(self):
        """
        Test that an unapproved article CAN be retrieved by an editor.
        """
        self.client.force_authenticate(user=self.editor_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Unapproved Local News")

    def test_article_creation_by_journalist(self):
        """
        Test that a journalist can create an article via API.
        """
        self.client.force_authenticate(user=self.journalist_user)
        data = {
            "title": "New API Article",
            "content": "This article was created via the API.",
            "publisher": self.publisher1.pk,
            "image": None,  # No image for simplicity in test
        }
        response = self.client.post(self.article_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 5)  # 4 initial + 1 new
        new_article = Article.objects.get(title="New API Article")
        self.assertEqual(new_article.author, self.journalist_user)
        self.assertFalse(
            new_article.is_approved
        )  # New articles are not approved by default

    def test_article_creation_by_non_journalist(self):
        """
        Test that a non-journalist cannot create an article via API.
        """
        self.client.force_authenticate(user=self.reader_user)
        data = {
            "title": "Forbidden Article",
            "content": "Attempt to create an article as a reader.",
            "publisher": self.publisher1.pk,
        }
        response = self.client.post(self.article_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Article.objects.count(), 4)  # No new article created

    def test_article_update_by_author(self):
        """
        Test that an author can update their own article.
        """
        self.client.force_authenticate(user=self.journalist_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article1.pk})
        data = {"content": "Updated content for AI Breakthrough."}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.content, "Updated content for AI Breakthrough.")

    def test_article_update_by_editor(self):
        """
        Test that an editor can update any article.
        """
        self.client.force_authenticate(user=self.editor_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article1.pk})
        data = {"content": "Editor updated content."}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.content, "Editor updated content.")

    def test_article_update_by_unauthorized_user(self):
        """
        Test that a non-author/non-editor cannot update an article.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article1.pk})
        data = {"content": "Unauthorized update attempt."}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.article1.refresh_from_db()
        self.assertNotEqual(self.article1.content, "Unauthorized update attempt.")

    def test_article_delete_by_author(self):
        """
        Test that an author can delete their own article.
        """
        self.client.force_authenticate(user=self.journalist_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 3)  # 4 initial - 1 deleted

    def test_article_delete_by_editor(self):
        """
        Test that an editor can delete any article.
        """
        self.client.force_authenticate(user=self.editor_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 3)

    def test_article_delete_by_unauthorized_user(self):
        """
        Test that a non-author/non-editor cannot delete an article.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse("api-article-detail", kwargs={"pk": self.article1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Article.objects.count(), 4)  # Article not deleted

    # --- Publisher-Specific Article Retrieval Tests ---

    def test_publisher_articles_api(self):
        """
        Test retrieving approved articles for a specific publisher.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse(
            "api-publisher-articles", kwargs={"publisher_id": self.publisher1.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 1
        )  # Only article1 is approved for publisher1
        self.assertEqual(response.data[0]["title"], "AI Breakthrough")

        url = reverse(
            "api-publisher-articles", kwargs={"publisher_id": self.publisher2.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 2
        )  # article2, article4 are approved for publisher2
        article_titles = {article["title"] for article in response.data}
        self.assertIn("Global Economy Report", article_titles)
        self.assertIn("Editor Approved Article", article_titles)

    def test_publisher_articles_api_no_approved_articles(self):
        """
        Test retrieving articles for a publisher with no approved articles.
        """
        # Create a new publisher with an unapproved article
        publisher3 = Publisher.objects.create(
            name="New Publisher", description="New content"
        )
        Article.objects.create(
            title="Another Unapproved Article",
            content="Content here.",
            publisher=publisher3,
            author=self.journalist_user,
            is_approved=False,
        )

        self.client.force_authenticate(user=self.reader_user)
        url = reverse("api-publisher-articles", kwargs={"publisher_id": publisher3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return an empty list

    def test_publisher_articles_api_invalid_publisher_id(self):
        """
        Test retrieving articles for a non-existent publisher.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse(
            "api-publisher-articles", kwargs={"publisher_id": 9999}
        )  # Non-existent ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Journalist-Specific Article Retrieval Tests ---

    def test_journalist_articles_api(self):
        """
        Test retrieving approved articles for a specific journalist.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse(
            "api-journalist-articles", kwargs={"journalist_id": self.journalist_user.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # journalist_user authored article1, article2, article3. Only article1 and article2 are approved.
        self.assertEqual(len(response.data), 2)
        article_titles = {article["title"] for article in response.data}
        self.assertIn("AI Breakthrough", article_titles)
        self.assertIn("Global Economy Report", article_titles)
        self.assertNotIn("Unapproved Local News", article_titles)

    def test_journalist_articles_api_no_approved_articles(self):
        """
        Test retrieving articles for a journalist with no approved articles.
        """
        # Create a new journalist with only unapproved articles
        journalist2 = User.objects.create_user(
            username="journalist2",
            email="j2@example.com",
            password="j2password",
            role="journalist",
        )
        Article.objects.create(
            title="Draft by J2",
            content="Draft content.",
            author=journalist2,
            is_approved=False,
        )

        self.client.force_authenticate(user=self.reader_user)
        url = reverse(
            "api-journalist-articles", kwargs={"journalist_id": journalist2.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return an empty list

    def test_journalist_articles_api_invalid_journalist_id(self):
        """
        Test retrieving articles for a non-existent journalist.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse(
            "api-journalist-articles", kwargs={"journalist_id": 9999}
        )  # Non-existent ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_journalist_articles_api_non_journalist_user_id(self):
        """
        Test retrieving articles using a user ID that is not a journalist.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse(
            "api-journalist-articles", kwargs={"journalist_id": self.reader_user.pk}
        )  # Reader user ID
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )  # Should return 404 as it's not a journalist

    # --- Publisher API Tests ---

    def test_publisher_list_api(self):
        """
        Test retrieving the list of all publishers.
        """
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get(self.publisher_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # publisher1, publisher2
        publisher_names = [p["name"] for p in response.data]
        self.assertIn("Tech News Inc", publisher_names)
        self.assertIn("World Affairs Daily", publisher_names)

    def test_publisher_detail_api(self):
        """
        Test retrieving a single publisher's details.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse("api-publisher-detail", kwargs={"pk": self.publisher1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Tech News Inc")

    # --- Journalist API Tests ---

    def test_journalist_list_api(self):
        """
        Test retrieving the list of all journalists.
        """
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get(self.journalist_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect testjournalist and testeditor (if editor is also considered journalist for some reason, otherwise just journalist)
        # Based on models.py, only 'journalist' role is filtered.
        self.assertEqual(
            len(response.data), 1
        )  # Only self.journalist_user has role='journalist'
        self.assertEqual(response.data[0]["username"], "testjournalist")

    def test_journalist_detail_api(self):
        """
        Test retrieving a single journalist's details.
        """
        self.client.force_authenticate(user=self.reader_user)
        url = reverse("api-journalist-detail", kwargs={"pk": self.journalist_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testjournalist")

    # --- Subscription API Tests ---

    def test_subscribe_publisher_api(self):
        """
        Test that a reader can subscribe to a publisher via API.
        """
        self.client.force_authenticate(user=self.reader_user)
        data = {"type": "publisher", "id": self.publisher1.pk, "action": "subscribe"}
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reader_user.refresh_from_db()
        self.assertTrue(
            self.reader_user.subscribed_publishers.filter(
                pk=self.publisher1.pk
            ).exists()
        )

    def test_unsubscribe_publisher_api(self):
        """
        Test that a reader can unsubscribe from a publisher via API.
        """
        self.reader_user.subscribed_publishers.add(self.publisher1)  # Pre-subscribe
        self.client.force_authenticate(user=self.reader_user)
        data = {"type": "publisher", "id": self.publisher1.pk, "action": "unsubscribe"}
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reader_user.refresh_from_db()
        self.assertFalse(
            self.reader_user.subscribed_publishers.filter(
                pk=self.publisher1.pk
            ).exists()
        )

    def test_subscribe_journalist_api(self):
        """
        Test that a reader can subscribe to a journalist via API.
        """
        self.client.force_authenticate(user=self.reader_user)
        data = {
            "type": "journalist",
            "id": self.journalist_user.pk,
            "action": "subscribe",
        }
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reader_user.refresh_from_db()
        self.assertTrue(
            self.reader_user.subscribed_journalists.filter(
                pk=self.journalist_user.pk
            ).exists()
        )

    def test_unsubscribe_journalist_api(self):
        """
        Test that a reader can unsubscribe from a journalist via API.
        """
        self.reader_user.subscribed_journalists.add(
            self.journalist_user
        )  # Pre-subscribe
        self.client.force_authenticate(user=self.reader_user)
        data = {
            "type": "journalist",
            "id": self.journalist_user.pk,
            "action": "unsubscribe",
        }
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reader_user.refresh_from_db()
        self.assertFalse(
            self.reader_user.subscribed_journalists.filter(
                pk=self.journalist_user.pk
            ).exists()
        )

    def test_subscribe_api_invalid_type(self):
        """
        Test subscription API with an invalid type.
        """
        self.client.force_authenticate(user=self.reader_user)
        data = {"type": "invalid_type", "id": self.publisher1.pk, "action": "subscribe"}
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_api_non_reader_permission(self):
        """
        Test that a non-reader cannot use the subscription API.
        """
        self.client.force_authenticate(
            user=self.journalist_user
        )  # Journalist trying to subscribe
        data = {"type": "publisher", "id": self.publisher1.pk, "action": "subscribe"}
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
