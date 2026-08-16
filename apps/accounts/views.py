from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View


class LogoutView(View):
    """Log the current user out and redirect to the login page.

    GET is supported for compatibility with the existing navigation link,
    while POST remains supported for forms and future CSRF-safe logout flows.
    """

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")
