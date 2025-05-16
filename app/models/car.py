from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.paginator import (
    EmptyPage, InvalidPage, PageNotAnInteger, Paginator
)
from cloudinary.models import CloudinaryField
from wagtail.models import Page
from wagtail.search import index
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField
from django.db.models import Q
from modelcluster.fields import ParentalKey
from django import forms


class VehicleIndexPage(RoutablePageMixin, Page):
    """
    Index page for vehicle listings with advanced filtering and sorting.
    """
    subpage_types = ['app.Vehicle']
    template = "app/cars/cars.html"
    max_count = 1

    intro_text = RichTextField(blank=True,
                               help_text="Optional introduction text\
                                to display at the top of the page")
    items_per_page = models.PositiveIntegerField(
        default=10, help_text="Number of vehicles to display per page")

    content_panels = Page.content_panels + [
        FieldPanel('intro_text'),
        FieldPanel('items_per_page'),
    ]

    def get_vehicle_queryset(self, request):
        """Get base queryset of vehicles with filters applied"""
        # Base queryset
        vehicles = Vehicle.objects.live().filter(published=True)

        # Apply filters from GET parameters
        filters = {}

        # Price range filter
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price:
            filters['price__gte'] = min_price
        if max_price:
            filters['price__lte'] = max_price

        # Year range filter
        min_year = request.GET.get('min_year')
        max_year = request.GET.get('max_year')
        if min_year:
            filters['year__gte'] = min_year
        if max_year:
            filters['year__lte'] = max_year

        # Mileage range filter
        min_mileage = request.GET.get('min_mileage')
        max_mileage = request.GET.get('max_mileage')
        if min_mileage:
            filters['mileage__gte'] = min_mileage
        if max_mileage:
            filters['mileage__lte'] = max_mileage

        # Exact match filters
        for key in ['transmission', 'fuel_type', 'color']:
            value = request.GET.get(key)
            if value:
                filters[key] = value

        # Search term
        search_term = request.GET.get('q')
        if search_term:
            vehicles = vehicles.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )

        # Apply all filters
        return vehicles.filter(**filters)

    def _apply_sorting(self, queryset, request):
        """Apply sorting to the queryset based on request parameters"""
        sort_param = request.GET.get('sort', 'date_desc')

        sort_mappings = {
            "date": "first_published_at",
            "title": "title",
            "price": "price",
            "mileage": "mileage",
            "year": "year",
            "transmission": "transmission",
            "color": "color",
            "fuel_type": "fuel_type"
        }

        if sort_param == "relevance":
            return queryset

        try:
            field, direction = sort_param.rsplit("_", 1)
            field_name = sort_mappings.get(field)

            if not field_name:
                return queryset

            if direction == "desc":
                field_name = f"-{field_name}"

            return queryset.order_by(field_name)
        except (ValueError, AttributeError):
            # Default sorting if parameter is invalid
            return queryset.order_by('-first_published_at')

    def get_context(self, request):
        context = super().get_context(request)

        # Get filtered queryset
        vehicles = self.get_vehicle_queryset(request)

        # Apply sorting
        vehicles = self._apply_sorting(vehicles, request)

        # Pagination
        paginator = Paginator(vehicles, self.items_per_page)
        page_number = request.GET.get('page')

        try:
            page_obj = paginator.get_page(page_number)
        except (InvalidPage, PageNotAnInteger, EmptyPage):
            page_obj = paginator.get_page(1)

        # Add to context
        context.update({
            'vehicles': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'total_vehicles': vehicles.count(),
            'current_filters': {k: v for k, v in request.GET.items()},
            # Get available choices for filters
            'transmission_choices': dict(settings.TRANSMISSION_CHOICES),
            'fuel_type_choices': dict(settings.FUEL_TYPE_CHOICES),
            'color_choices': dict(settings.COLOR_CHOICES),
        })

        return context

    @route(r'^category/(?P<category>[-\w]+)/$')
    def category_view(self, request, category):
        """View for filtering by vehicle category"""
        context = self.get_context(request)
        vehicles = Vehicle.objects.live().filter(
            published=True, categories__slug=category
        )
        context['vehicles'] = self._paginate_queryset(vehicles, request)
        context['category'] = category
        return self.render(request, template="app/cars/category.html",
                           context=context)

    @route(r'^search/$')
    def search_view(self, request):
        """Search view for vehicles"""
        context = self.get_context(request)
        return self.render(request, template="app/cars/search.html",
                           context=context)

    def _paginate_queryset(self, queryset, request):
        """Helper method to paginate a queryset"""
        paginator = Paginator(queryset, self.items_per_page)
        page_number = request.GET.get('page')

        try:
            return paginator.get_page(page_number)
        except (InvalidPage, PageNotAnInteger, EmptyPage):
            return paginator.get_page(1)


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
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE,
                                related_name='category_relations')
    category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE,
                                 related_name='vehicle_relations')

    class Meta:
        unique_together = ('vehicle', 'category')


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


class Vehicle(Page):
    """
    A model representing a vehicle (car) with enhanced features.
    """
    parent_page_types = ['app.VehicleIndexPage']

    TRANSMISSION_CHOICES = settings.TRANSMISSION_CHOICES
    FUEL_TYPE_CHOICES = settings.FUEL_TYPE_CHOICES
    COLOR_CHOICES = settings.COLOR_CHOICES
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('certified', 'Certified Pre-Owned'),
    ]

    # Basic Fields
    year = models.PositiveIntegerField(help_text="Year of manufacture")
    make = models.CharField(max_length=100,
                            help_text="Car manufacturer (e.g., Toyota, Ford)")
    model = models.CharField(max_length=100,
                             help_text="Car model (e.g., Camry, F-150)")
    trim = models.CharField(max_length=100, blank=True,
                            help_text="Model trim (e.g., LX, Sport)")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2,
                                     null=True, blank=True,
                                     help_text="Optional discounted price")

    # Vehicle Details
    mileage = models.PositiveIntegerField()
    vin = models.CharField(max_length=17, blank=True,
                           help_text="Vehicle Identification Number")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES,
                                 default='used')
    engine = models.CharField(max_length=100, blank=True,
                              help_text="Engine specifications")
    color = models.CharField(max_length=50, choices=COLOR_CHOICES)
    interior_color = models.CharField(max_length=50, blank=True)
    fuel_type = models.CharField(max_length=50,
                                 choices=FUEL_TYPE_CHOICES)
    transmission = models.CharField(max_length=50,
                                    choices=TRANSMISSION_CHOICES)
    doors = models.PositiveSmallIntegerField(default=4)
    seats = models.PositiveSmallIntegerField(default=5)

    # Additional Info
    description = RichTextField(blank=True)
    features = models.ManyToManyField(VehicleFeature, blank=True,
                                      related_name="vehicles")
    categories = models.ManyToManyField(
        VehicleCategory,
        through=VehicleCategoryRelation,
        blank=True,
        related_name="vehicles"
    )

    # State
    published = models.BooleanField(default=True)
    featured = models.BooleanField(
        default=False, help_text="Feature this vehicle in prominent areas")
    sold = models.BooleanField(default=False)
    warranty_period = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Warranty period in months"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Listing User
    listed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # Changed from CASCADE for data integrity
        related_name='vehicles',
        null=True,  # Allow null temporarily to fix existing data
    )

    # Cloudinary primary image
    cloudinary_image_id = models.CharField(max_length=255, blank=True,
                                           null=True)
    cloudinary_image_url = models.URLField(blank=True, null=True)
    optimized_image_url = models.URLField(blank=True, null=True)

    # Search fields
    search_fields = Page.search_fields + [
        index.SearchField('make'),
        index.SearchField('model'),
        index.SearchField('description'),
    ]

    # Editor panels
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('make'),
            FieldPanel('model'),
            FieldPanel('trim'),
            FieldPanel('year'),
            FieldPanel('condition'),
        ], heading="Basic Information"),

        MultiFieldPanel([
            FieldPanel('price'),
            FieldPanel('sale_price'),
        ], heading="Pricing"),

        MultiFieldPanel([
            FieldPanel('mileage'),
            FieldPanel('engine'),
            FieldPanel('fuel_type'),
            FieldPanel('transmission'),
            FieldPanel('color'),
            FieldPanel('interior_color'),
            FieldPanel('doors'),
            FieldPanel('seats'),
            FieldPanel('vin'),
        ], heading="Vehicle Details"),

        FieldPanel('description'),
        FieldPanel('features', widget=forms.CheckboxSelectMultiple),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),

        MultiFieldPanel([
            FieldPanel('cloudinary_image_id', read_only=True),
            FieldPanel('cloudinary_image_url', read_only=True),
            FieldPanel('optimized_image_url', read_only=True),
        ], heading="Primary Image"),

        InlinePanel('gallery_images', label="Gallery Images"),

        MultiFieldPanel([
            FieldPanel('published'),
            FieldPanel('featured'),
            FieldPanel('sold'),
            FieldPanel('warranty_period'),
            FieldPanel('listed_by'),
        ], heading="Listing Details"),
    ]

    # Make slug from title
    def save(self, *args, **kwargs):
        if not self.slug:
            # Create a slug from make, model, and year for better SEO
            base_slug = f"{self.year}-{self.make}-{self.model}"
            if self.trim:
                base_slug += f"-{self.trim}"
            self.slug = slugify(base_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.year} {self.make} {self.model} {self.trim}".strip()

    @property
    def display_price(self):
        """Return sale_price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.price

    @property
    def has_discount(self):
        """Check if vehicle has a discounted price"""
        return self.sale_price is not None and self.sale_price < self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage if applicable"""
        if not self.has_discount:
            return 0
        return int(((self.price - self.sale_price) / self.price) * 100)

    @property
    def primary_image(self):
        """Return the primary image for the vehicle"""
        if self.optimized_image_url:
            return self.optimized_image_url
        elif self.cloudinary_image_url:
            return self.cloudinary_image_url
        # Return first gallery image if no primary image
        gallery = self.gallery_images.filter(live=True).first()
        if gallery and gallery.optimized_image_url:
            return gallery.optimized_image_url
        # Default placeholder
        return "/static/images/placeholder-car.jpg"

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['make']),
            models.Index(fields=['model']),
            models.Index(fields=['year']),
            models.Index(fields=['price']),
            models.Index(fields=['sold']),
            models.Index(fields=['published']),
            models.Index(fields=['featured']),
        ]


class VehicleGalleryImage(models.Model):
    """
    Gallery images for a vehicle with enhanced functionality.
    """
    vehicle = ParentalKey(Vehicle, on_delete=models.CASCADE,
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


# Optional models for enhanced functionality

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
