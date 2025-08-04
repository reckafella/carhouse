from django.conf import settings
from django.db import models
from app.models.car import Vehicle


class SavedVehicle(models.Model):
    """
    Saved/favorited vehicles for users.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='saved_vehicles')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,
                                related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vehicle')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.vehicle} saved by {self.user}"
