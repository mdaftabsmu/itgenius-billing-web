from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views import View

from .forms import SignUpForm


class SignUpView(View):
    """Register a new user and sign them in after successful signup.

    New self-registered users are intentionally not assigned an elevated
    billing role. An administrator can assign the appropriate role/group.
    """

    template_name = "accounts/signup.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, self.template_name, {"form": SignUpForm()})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")

        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")

        return render(request, self.template_name, {"form": form})


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
