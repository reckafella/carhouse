from django.db import models


class VehicleFeature(models.Model):
    """
    Features for vehicles (e.g., Air Conditioning, Leather Seats)
    """
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Optional CSS class for icon")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
