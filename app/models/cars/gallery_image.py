from django.db import models
from cloudinary.models import CloudinaryField
from wagtail.admin.panels import FieldPanel

from app.models.car import Vehicle


class VehicleGalleryImage(models.Model):
    """
    Gallery images for a vehicle with enhanced functionality.
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,
                                related_name='gallery_images')
    image = CloudinaryField('image', null=True, blank=True)
    cloudinary_image_id = models.CharField(max_length=255,
                                           blank=True, null=True)
    cloudinary_image_url = models.URLField(blank=True, null=True)
    optimized_image_url = models.URLField(blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True,
                                help_text="Alternative text for accessibility")
    sort_order = models.IntegerField(default=0)
    live = models.BooleanField(default=True)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
        FieldPanel('alt_text'),
        FieldPanel('sort_order'),
        FieldPanel('live'),
    ]

    class Meta:
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
        ordering = ["sort_order", "-id"]

    def __str__(self):
        """Return a string representation of the image"""
        if self.vehicle:
            return f"Image for {self.vehicle} - {self.caption}"
        # If vehicle is not linked, return a generic message
        return "Unlinked Image"
