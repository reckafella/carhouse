from django.db import models
from django.utils.text import slugify

from app.models.car import Vehicle


class VehicleCategory(models.Model):
    """
    Categories for vehicles (e.g., SUV, Sedan, Truck)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vehicle Category"
        verbose_name_plural = "Vehicle Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class VehicleCategoryRelation(models.Model):
    """
    Many-to-many relationship between vehicles and categories
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,
                                related_name='category_relations')
    category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE,
                                 related_name='vehicle_relations')

    class Meta:
        unique_together = ('vehicle', 'category')
