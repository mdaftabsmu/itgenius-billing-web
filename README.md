# ITGenius Billing Web

Production-oriented Django + MySQL web billing application migrated from `billingCosolebase`.

## Features
- Customer, category and product masters
- Inventory and low-stock tracking
- Quotations with GST, discount and PDF generation
- Invoices with GST, discount, balance tracking and PDF generation
- Payment recording with invoice balance validation
- Billing dashboard
- Sales and collection reports with CSV export
- Django authentication and role groups
- Audit logging
- REST API with OpenAPI/Swagger
- Rotating application/error logs
- Docker + MySQL Compose stack
- Pytest smoke tests and GitHub Actions CI

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate --run-syncdb
python manage.py createsuperuser
python manage.py setup_roles
python manage.py runserver
```

Open `/login/`, `/admin/`, `/`, `/reports/sales/`, `/reports/collections/`, and `/api/docs/`.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

For production, set a strong `DJANGO_SECRET_KEY`, real `DJANGO_ALLOWED_HOSTS`, database credentials, and `SECURE_SSL_REDIRECT=True` behind HTTPS.

## Roles

Run `python manage.py setup_roles` to create Administrator, Manager, Sales, Accountant and Viewer groups. Assign users to groups from Django Admin.

## Database migrations

The current bootstrap/CI flow uses `migrate --run-syncdb` so application tables without committed migration files are created. Before a controlled production rollout, generate and commit versioned migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing

```bash
pytest
```

## API

Swagger: `/api/docs/`
Schema: `/api/schema/`
Core endpoints: `/api/customers/`, `/api/products/`, `/api/invoices/`.
