from django import forms
from app.models.models import ContactMessage


class ContactSellerForm(forms.Form):
    """
    Form for contacting vehicle sellers
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Phone (Optional)'
        })
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Your message...'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError("Please enter a valid email address.")
        return email

    def send_email(self, vehicle, seller_email):
        """
        Send email to the seller about the vehicle inquiry
        """
        # TODO: Implement actual email sending logic
        # This would typically use Django's email functionality
        subject = f"Inquiry about {vehicle.title}"
        message_body = f"""
        You have received a new inquiry about your vehicle listing:

        Vehicle: {vehicle.title}
        Price: ${vehicle.display_price}

        From: {self.cleaned_data['name']} ({self.cleaned_data['email']})
        Phone: {self.cleaned_data.get('phone', 'Not provided')}

        Message:
        {self.cleaned_data['message']}
        """

        # For now, just print the message (replace with actual email sending)
        print(f"Email would be sent to: {seller_email}")
        print(f"Subject: {subject}")
        print(f"Message: {message_body}")

        return True


class ContactMessageForm(forms.ModelForm):
    """
    General contact form for the website
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your Message'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError("Please enter a valid email address.")
        return email
