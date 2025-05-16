from django import forms


class VehicleForm(forms.ModelForm):
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def validate(self):
        if not self.make or not self.model or not self.year:
            raise ValueError("All fields are required.")
        if not isinstance(self.year, int) or self.year < 1886:
            raise ValueError("Year must be a valid integer greater than 1886.")
        return True

    def save(self):
        if self.validate():
            # Simulate saving to a database
            _vehicle = f'{self.year} {self.make} {self.model}'
            print(f"Vehicle {_vehicle}) saved successfully.")


class VehicleGalleryImageFormSet(forms.ModelForm):
    def __init__(self, images):
        self.images = images

    def validate(self):
        if not self.images:
            raise ValueError("At least one image is required.")
        return True

    def save(self):
        if self.validate():
            # Simulate saving images to a database
            for image in self.images:
                print(f"Image {image} saved successfully.")


class VehicleReviewForm(forms.ModelForm):
    """form to handle vehicle review info"""
    pass


class VehicleRatingForm(forms.ModelForm):
    """form to handle vehicle rating info"""
    pass
