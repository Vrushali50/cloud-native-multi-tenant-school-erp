from django.db import models


class Tenant(models.Model):
    class SubscriptionPlan(models.TextChoices):
        BASIC = "BASIC", "Basic"
        STANDARD = "STANDARD", "Standard"
        PREMIUM = "PREMIUM", "Premium"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        SUSPENDED = "SUSPENDED", "Suspended"

    school_name = models.CharField(max_length=150)

    subdomain = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Unique school identifier, for example: greenwood",
    )

    address = models.TextField(blank=True)

    contact_email = models.EmailField()

    contact_phone = models.CharField(
        max_length=20,
        blank=True,
    )

    subscription_plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.BASIC,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["school_name"]

    def __str__(self):
        return self.school_name