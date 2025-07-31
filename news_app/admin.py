from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Publisher, Article

admin.site.register(Publisher)
admin.site.register(User) 


# Custom UserAdmin to display and manage the 'role' field and subscriptions
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("role", "subscribed_publishers", "subscribed_journalists")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")


# Custom ArticleAdmin to make 'is_approved' easily manageable
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "is_approved", "published_date")
    list_filter = (
        "is_approved",
        "publisher",
        "author__role",
    )  # Filter by approval status, publisher, author role
    search_fields = ("title", "content", "author__username", "publisher__name")
    actions = ["make_approved", "make_unapproved"]  # Custom actions

    def make_approved(self, request, queryset):
        # Update selected articles to approved
        updated = queryset.update(is_approved=True)
        self.message_user(
            request, f"{updated} articles successfully marked as approved."
        )

    make_approved.short_description = "Mark selected articles as approved"

    def make_unapproved(self, request, queryset):
        # Update selected articles to unapproved
        updated = queryset.update(is_approved=False)
        self.message_user(
            request, f"{updated} articles successfully marked as unapproved."
        )

    make_unapproved.short_description = "Mark selected articles as unapproved"
