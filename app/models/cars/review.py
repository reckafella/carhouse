from django.conf import settings
from django.db import models
from app.models.car import Vehicle


class VehicleReview(models.Model):
    """
    User reviews for vehicles.
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,
                                related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=255)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('vehicle', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} for {self.vehicle}"
