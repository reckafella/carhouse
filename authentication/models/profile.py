from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy as reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils.functional import cached_property
# from django.utils.text import slugify
# from wagtail.fields import RichTextField


class Profile(models.Model):
    """
    Extended user profile for the car listing platform.
    Uses User reference.
    """
    ACCOUNT_TYPE_CHOICES = [
        ('buyer', 'Car Buyer'),
        ('seller', 'Car Seller'),
        ('dealer', 'Car Dealer'),
        ('admin', 'Admin'),
    ]

    # User relationship
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Basic profile information
    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='buyer',
        help_text="Type of account for this user"
    )

    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'.\
            Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex],
                                    max_length=17, blank=True)
    show_phone = models.BooleanField(default=False,
                                     help_text="Show phone number on listings")
    show_email = models.BooleanField(default=False,
                                     help_text="Show email on listings")

    # Location information
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Social media links
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    # Profile image
    profile_pic = CloudinaryField('image', null=True, blank=True)
    cloudinary_image_id = models.CharField(max_length=255,
                                           blank=True, null=True)
    cloudinary_image_url = models.URLField(blank=True, null=True)
    optimized_image_url = models.URLField(blank=True, null=True)

    # Dealer/seller specific fields
    company_name = models.CharField(max_length=200, blank=True, null=True)
    business_license = models.CharField(max_length=100, blank=True, null=True)
    is_verified_seller = models.BooleanField(default=False)

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)

    # Platform engagement
    listing_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1,
                                 null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            models.Index(fields=['account_type']),
            models.Index(fields=['is_verified_seller']),
        ]

    def __str__(self):
        if self.company_name and self.account_type in ['dealer', 'seller']:
            return f"{self.company_name} ({self.user.username})"
        return self.user.get_full_name() or self.user.username

    def save(self, *args, **kwargs):
        # Add any pre-save processing here
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the URL for this profile"""
        return reverse('profile_detail',
                       kwargs={'username': self.user.username})

    @property
    def display_name(self):
        """Return the appropriate display name based on account type"""
        if self.account_type == 'dealer' and self.company_name:
            return self.company_name
        return self.user.get_full_name() or self.user.username

    @property
    def profile_image(self):
        """Return the profile image or default placeholder"""
        if self.optimized_image_url:
            return self.optimized_image_url
        elif self.cloudinary_image_url:
            return self.cloudinary_image_url
        # Default placeholder
        return "/static/images/default-profile.png"

    @cached_property
    def active_listings_count(self):
        """Return count of active vehicle listings"""
        return self.user.vehicles.filter(published=True, sold=False).count()


class SellerReview(models.Model):
    """
    Reviews for sellers/dealers from buyers
    """
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews'
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('reviewer', 'seller')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review of {self.seller} by {self.reviewer}"


class SavedSearch(models.Model):
    """
    Saved searches for users to receive notifications
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )
    name = models.CharField(max_length=100)
    search_params = models.JSONField(help_text="Saved search parameters")
    notify = models.BooleanField(
        default=True, help_text="Send notifications for new matching vehicles"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_notified = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Saved Search"
        verbose_name_plural = "Saved Searches"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} by {self.user}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance when a new User is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure the Profile is saved when the User is saved"""
    # Create profile if it doesn't exist (for existing users)
    Profile.objects.get_or_create(user=instance)
    instance.profile.save()


@receiver(post_save, sender=SellerReview)
def update_seller_rating(sender, instance, **kwargs):
    """Update seller's average rating when a review is created or updated"""
    if instance.is_approved:
        seller = instance.seller
        approved_reviews = SellerReview.objects.filter(
            seller=seller,
            is_approved=True
        )

        # Calculate new rating average
        ratings_sum = sum(review.rating for review in approved_reviews)
        count = approved_reviews.count()

        if count > 0:
            # Update seller's profile
            seller.profile.rating = round(ratings_sum / count, 1)
            seller.profile.review_count = count
            seller.profile.save()
