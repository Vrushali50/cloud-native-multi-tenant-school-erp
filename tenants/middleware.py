from django.shortcuts import render


class ActiveTenantMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        user = request.user

        allowed_paths = [
            "/logout/",
            "/admin/",
        ]

        for path in allowed_paths:

            if request.path.startswith(path):

                return self.get_response(request)

        if user.is_authenticated:

            is_product_owner = user.groups.filter(
                name="Product Owner"
            ).exists()

            if not is_product_owner and not user.is_superuser:

                tenant = getattr(
                    user,
                    "tenant",
                    None,
                )

                if tenant and hasattr(tenant, "is_active"):

                    if tenant.is_active is False:

                        return render(
                            request,
                            "accounts/school_inactive.html",
                        )

        response = self.get_response(request)

        return response