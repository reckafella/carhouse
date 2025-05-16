from django import forms


class ContactSellerForm(forms.ModelForm):
    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

    def validate(self):
        if not self.name or not self.email or not self.message:
            raise ValueError("All fields are required.")
        if "@" not in self.email:
            raise ValueError("Invalid email address.")
        return True

    def send_email(self):
        # Simulate sending an email
        print(f"Sending email to {self.email}...")
        print(f"Name: {self.name}")
        print(f"Message: {self.message}")
        print("Email sent successfully.")
        return True

    def save(self):
        # Simulate saving the form data to a database
        print("Saving form data to the database...")
        print(f"Name: {self.name}")
        print(f"Email: {self.email}")
        print(f"Message: {self.message}")
        print("Form data saved successfully.")
        return True

    def handle_success(self):
        # Simulate handling success
        print("Handling success...")
        print("Form submitted successfully.")
        return True

    def handle_error(self, error_message):
        # Simulate handling error
        print("Handling error...")
        print(f"Error: {error_message}")
        return False

    def get_context_data(self, **kwargs):
        context = {
            "page_title": "Contact Seller",
            "form_title": "Contact Seller",
            "submit_text": "Send Message",
            "data_loading_text": "Sending...",
            "extra_messages": [
                {
                    "text": "Need assistance?",
                    "link": "/help/",
                    "link_text": "Help Center",
                }
            ],
        }
        context.update(kwargs)
        return context
