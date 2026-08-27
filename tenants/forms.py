from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import Tenant

class TenantForm(forms.ModelForm):

    class Meta:
        model = Tenant
        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            field.widget.attrs.update(
                {
                    "class": "form-control",
                }
            )

    def save(self, commit=True):

        tenant = super().save(commit=False)

        if hasattr(tenant, "status") and hasattr(tenant, "is_active"):

            status_value = str(tenant.status).lower()

            if status_value in ["active", "activated"]:

                tenant.is_active = True

            elif status_value in ["inactive", "suspended", "deactivated", "disabled"]:

                tenant.is_active = False

        if commit:

            tenant.save()

        return tenant
class SchoolAdminCreationForm(forms.Form):

    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.filter(is_active=True),
        label="School",
    )

    username = forms.CharField(
        max_length=150,
    )

    first_name = forms.CharField(
        max_length=100,
    )

    last_name = forms.CharField(
        max_length=100,
    )

    email = forms.EmailField()

    phone = forms.CharField(
        max_length=20,
        required=False,
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            field.widget.attrs.update(
                {
                    "class": "form-control",
                }
            )

    def clean_username(self):

        username = self.cleaned_data.get("username")

        User = get_user_model()

        if User.objects.filter(username=username).exists():

            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):

        email = self.cleaned_data.get("email")

        User = get_user_model()

        if User.objects.filter(email=email).exists():

            raise forms.ValidationError(
                "This email is already used."
            )

        return email

    def clean(self):

        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data

    def save(self):

        User = get_user_model()

        tenant = self.cleaned_data["tenant"]

        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        user.tenant = tenant

        if hasattr(user, "phone"):
            user.phone = self.cleaned_data.get("phone", "")

        user.save()

        school_admin_group, created = Group.objects.get_or_create(
            name="School Admin"
        )

        user.groups.add(
            school_admin_group
        )

        return user