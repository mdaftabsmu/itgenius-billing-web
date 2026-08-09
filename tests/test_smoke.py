import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_login_url(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse("dashboard"))
    assert response.status_code in (302, 301)
