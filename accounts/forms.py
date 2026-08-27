from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from tenants.models import Tenant

from .models import User


class UserForm(UserCreationForm):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Select a role",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "tenant",
            "role",
            "is_active",
            "password1",
            "password2",
        )

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:
            self.fields["tenant"].queryset = Tenant.objects.all()
            self.fields["role"].queryset = Group.objects.all()

        else:
            self.fields["tenant"].queryset = Tenant.objects.filter(
                id=current_user.tenant_id
            )

            self.fields["tenant"].initial = current_user.tenant
            self.fields["tenant"].disabled = True

            self.fields["role"].queryset = Group.objects.exclude(
                name="Product Owner"
            )

    def save(self, commit=True):
        user = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            user.tenant = self.current_user.tenant

        if commit:
            user.save()

            selected_role = self.cleaned_data["role"]
            user.groups.set([selected_role])

        return user


class EditUserForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        empty_label="Select a role",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "tenant",
            "role",
            "is_active",
        )

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if self.instance.pk:
            self.fields["role"].initial = self.instance.groups.first()

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:
            self.fields["tenant"].queryset = Tenant.objects.all()
            self.fields["role"].queryset = Group.objects.all()

        else:
            self.fields["tenant"].queryset = Tenant.objects.filter(
                id=current_user.tenant_id
            )

            self.fields["tenant"].initial = current_user.tenant
            self.fields["tenant"].disabled = True

            self.fields["role"].queryset = Group.objects.exclude(
                name="Product Owner"
            )

    def save(self, commit=True):
        user = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            user.tenant = self.current_user.tenant

        if commit:
            user.save()

            selected_role = self.cleaned_data["role"]
            user.groups.set([selected_role])

        return user