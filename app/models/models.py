from django.db import models
from django.urls import reverse_lazy as reverse


class SocialLinks(models.Model):
    website = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    twitter_x = models.URLField(max_length=200, blank=True, null=True)
    instagram = models.URLField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    youtube = models.URLField(max_length=200, blank=True, null=True)
    github = models.URLField(max_length=200, blank=True, null=True)
    tiktok = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Social Links: {self.website or ''}, {self.facebook or ''},\
            {self.twitter_x or ''}, {self.instagram or ''},\
                {self.linkedin or ''}, {self.youtube or ''},\
                    {self.github or ''}, {self.tiktok or ''}"

    class Meta:
        verbose_name = "Social Links"
        verbose_name_plural = "Social Links"
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_success_url(self):
        return reverse('app:contact')
