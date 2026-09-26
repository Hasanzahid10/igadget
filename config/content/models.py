from django.db import models

class Banner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    image_file = models.ImageField(upload_to='i_gadgets/banners/', blank=True, null=True)
    primary_button_text = models.CharField(max_length=100, blank=True, null=True)
    primary_button_link = models.CharField(max_length=255, blank=True, null=True)
    secondary_button_text = models.CharField(max_length=100, blank=True, null=True)
    secondary_button_link = models.CharField(max_length=255, blank=True, null=True)
    badge_text = models.CharField(max_length=100, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', '-id']

    def __str__(self):
        return self.title


class PromoSection(models.Model):
    TYPE_CHOICES = (
        ('exclusive_offer', 'Exclusive Offer'),
        ('deal_of_day', 'Deal of the Day'),
        ('member_benefits', 'Member Benefits'),
    )

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    action_link = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"
