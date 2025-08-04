from django import forms
from django.forms import inlineformset_factory
from django.conf import settings
from app.models.car import (
    Vehicle, VehicleFeature
)
from app.models.cars.category import (
    VehicleCategory
)
from app.models.cars.gallery_image import VehicleGalleryImage
from app.models.cars.review import VehicleReview
from cloudinary.forms import CloudinaryFileField


class VehicleForm(forms.ModelForm):
    """
    Django ModelForm for Vehicle creation and editing with proper validation
    """
    # Cloudinary image field for primary image
    primary_image = CloudinaryFileField(
        required=False,
        help_text="Upload the main image for this vehicle"
    )

    # Custom form fields for better user experience
    categories = forms.ModelMultipleChoiceField(
        queryset=VehicleCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select applicable categories"
    )

    features = forms.ModelMultipleChoiceField(
        queryset=VehicleFeature.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select available features"
    )

    class Meta:
        model = Vehicle
        fields = [
            'title', 'year', 'make', 'model', 'trim', 'price',
            'sale_price', 'mileage', 'vin', 'condition', 'engine',
            'color', 'interior_color', 'fuel_type', 'transmission',
            'doors', 'seats', 'description', 'features', 'categories',
            'published', 'featured', 'warranty_period'
        ]

        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1886',
                'max': '2030',
                'placeholder': 'e.g., 2022'
            }),
            'make': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Toyota'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Camry'
            }),
            'trim': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., LX, Sport (optional)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'e.g., 25000.00'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Discounted price (optional)'
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'e.g., 50000'
            }),
            'vin': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '17',
                'placeholder': 'Vehicle Identification Number'
            }),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'engine': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2.5L 4-Cylinder'
            }),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'interior_color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Black Leather'
            }),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'transmission': forms.Select(attrs={'class': 'form-control'}),
            'doors': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2',
                'max': '8',
                'placeholder': '4'
            }),
            'seats': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '12',
                'placeholder': '5'
            }),
            'warranty_period': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Warranty in months (optional)'
            }),
            'published': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}),
            'featured': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the current user as listed_by if creating new vehicle
        self.user = kwargs.pop('user', None)

        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['categories', 'features',
                                  'published', 'featured']:
                if not field.widget.attrs.get('class'):
                    field.widget.attrs['class'] = 'form-control'

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and (year < 1886 or year > 2030):
            raise forms.ValidationError("Year must be between 1886 and 2030.")
        return year

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price

    def clean_sale_price(self):
        sale_price = self.cleaned_data.get('sale_price')
        price = self.cleaned_data.get('price')

        if sale_price and price and sale_price >= price:
            raise forms.ValidationError(
                "Sale price must be less than the regular price.")
        return sale_price

    def clean_vin(self):
        vin = self.cleaned_data.get('vin')
        if vin and len(vin) not in [0, 17]:  # Allow empty or full VIN
            raise forms.ValidationError(
                "VIN must be exactly 17 characters long.")
        return vin

    def save(self, commit=True):
        vehicle = super().save(commit=False)

        # Set the user who listed the vehicle
        if self.user and not vehicle.listed_by:
            vehicle.listed_by = self.user

        # Generate title if not provided
        if not vehicle.title:
            title_parts = [str(vehicle.year), vehicle.make, vehicle.model]
            if vehicle.trim:
                title_parts.append(vehicle.trim)
            vehicle.title = ' '.join(title_parts)

        if commit:
            vehicle.save()
            self.save_m2m()  # Save many-to-many relationships

        return vehicle


class VehicleGalleryImageForm(forms.ModelForm):
    """
    Form for individual vehicle gallery images
    """
    image = CloudinaryFileField(
        help_text="Upload an image for the vehicle gallery"
    )

    class Meta:
        model = VehicleGalleryImage
        fields = ['image', 'caption', 'alt_text', 'sort_order']
        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image caption (optional)'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternative text for accessibility'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
        }


# Create formset for vehicle gallery images
VehicleGalleryImageFormSet = inlineformset_factory(
    Vehicle,
    VehicleGalleryImage,
    form=VehicleGalleryImageForm,
    fields=['image', 'caption', 'alt_text', 'sort_order'],
    extra=3,  # Number of empty forms to display
    can_delete=True,
    max_num=10,  # Maximum number of images
)


class VehicleReviewForm(forms.ModelForm):
    """
    Form to handle vehicle reviews
    """
    class Meta:
        model = VehicleReview
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Stars') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your review here...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.vehicle = kwargs.pop('vehicle', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        review = super().save(commit=False)
        if self.user:
            review.user = self.user
        if self.vehicle:
            review.vehicle = self.vehicle
        if commit:
            review.save()
        return review


class VehicleSearchForm(forms.Form):
    """
    Enhanced search form for vehicles with multiple filters
    """
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search vehicles...'
        }),
        label='Search'
    )

    make = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Make'
        })
    )

    model = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Model'
        })
    )

    min_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Year'
        })
    )

    max_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Year'
        })
    )

    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price'
        })
    )

    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price'
        })
    )

    min_mileage = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Mileage'
        })
    )

    max_mileage = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Mileage'
        })
    )

    transmission = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Transmission')] + list(
            settings.TRANSMISSION_CHOICES.items()),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    fuel_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Fuel Type')] + list(
            settings.FUEL_TYPE_CHOICES.items()),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    color = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Color')] + list(settings.COLOR_CHOICES.items()),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    condition = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Condition')] + Vehicle.CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    categories = forms.ModelMultipleChoiceField(
        queryset=VehicleCategory.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )


class VehicleCategoryForm(forms.ModelForm):
    """
    Form for managing vehicle categories
    """
    class Meta:
        model = VehicleCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Category description'
            }),
        }


class VehicleFeatureForm(forms.ModelForm):
    """
    Form for managing vehicle features
    """
    class Meta:
        model = VehicleFeature
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Feature name'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CSS icon class (optional)'
            }),
        }
