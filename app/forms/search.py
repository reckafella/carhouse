from django import forms


class VehicleSearchForm(forms.ModelForm):
    def __init__(self, make=None, model=None, year=None):
        self.make = make
        self.model = model
        self.year = year

    def search(self):
        # Placeholder for search logic
        return f"Searching for {self.year} {self.make} {self.model}"
