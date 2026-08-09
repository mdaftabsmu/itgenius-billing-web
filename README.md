# ITGenius Billing Web

Production-oriented Django + MySQL billing application migrated from `billingCosolebase`.

## 1. Features

- Customer, category and product masters
- Inventory and low-stock tracking
- Quotations with GST, discount and PDF generation
- Invoices with GST, discount, payment tracking and PDF generation
- Payment recording with invoice balance validation
- Billing dashboard
- Sales and collection reports with CSV export
- Django authentication and role groups
- Audit logging
- REST API with OpenAPI/Swagger
- Structured/rotating application and error logs
- Docker + MySQL Compose stack
- Pytest test suite and GitHub Actions CI
- Company configuration for invoice/quotation documents

## 2. Architecture

```text
Browser
  |
  v
Django Web Application
  |-- Authentication / RBAC
  |-- Dashboard
  |-- Customer / Category / Product
  |-- Inventory
  |-- Quotation + PDF
  |-- Invoice + PDF
  |-- Payments
  |-- Reports
  |-- Audit Log
  `-- REST API / OpenAPI
  |
  v
MySQL
```

## 3. Requirements

- Python 3.11+
- MySQL 8+
- pip
- Git
- Optional: Docker and Docker Compose

## 4. Local installation

```bash
git clone https://github.com/mdaftabsmu/itgenius-billing-web.git
cd itgenius-billing-web
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## 5. Environment configuration

Set the values in `.env` for your environment. At minimum configure:

```text
DJANGO_SECRET_KEY=<strong-random-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=itgenius_billing
DB_USER=<mysql-user>
DB_PASSWORD=<mysql-password>
DB_HOST=127.0.0.1
DB_PORT=3306
```

Never commit production secrets or passwords.

## 6. Database setup

Create the MySQL database and user, then run:

```bash
python manage.py makemigrations --check
python manage.py migrate
python manage.py check
```

Create an administrator:

```bash
python manage.py createsuperuser
python manage.py setup_roles
```

If `makemigrations --check` reports changes, generate the migration files and commit them before deployment:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 7. Run locally

```bash
python manage.py runserver
```

Important URLs:

- `/login/` — application login
- `/` — dashboard
- `/admin/` — Django administration
- `/reports/sales/` — sales report
- `/reports/collections/` — collection report
- `/api/docs/` — Swagger/OpenAPI UI
- `/api/schema/` — OpenAPI schema

## 8. Business workflow

```text
Customer
   -> Product / Inventory
   -> Quotation
   -> Quotation PDF
   -> Invoice
   -> Invoice PDF
   -> Payment
   -> Outstanding balance
   -> Sales / Collection reports
```

Invoice/payment totals are calculated server-side. A payment must not exceed the invoice balance due.

## 9. Roles

`python manage.py setup_roles` creates:

- Administrator — full administration
- Manager — operational management
- Sales — customer/quotation/sales operations
- Accountant — invoices, payments and financial reports
- Viewer — read-only access

Assign users to groups from Django Admin and verify permissions before production use.

## 10. PDF documents

Quotation and invoice PDF generation uses ReportLab. Company configuration is used for document identity/contact information.

Before production rollout, verify:

- company name/address/contact
- GST number
- invoice/quotation numbering
- customer details
- GST and discount calculations
- page layout and currency formatting
- terms and notes

## 11. Reports

The application provides sales and collection reporting. Verify date filters, totals, outstanding balances and CSV exports against known invoices/payments before production rollout.

## 12. Logging and audit

Application logging uses the `billing` logger. Configure log rotation and retain logs according to your operational policy.

Audit records should be reviewed for authentication, billing and payment activities. Do not log passwords, access tokens, card data or other secrets.

## 13. Testing

Run the complete local validation before deployment:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
pytest
```

For a clean test environment, use a dedicated MySQL test database and test credentials. Do not run destructive test commands against production data.

## 14. Docker

```bash
cp .env.example .env
docker compose up --build
```

Check the application and database health before exposing the stack publicly. Persist MySQL data using the configured Docker volume.

For production, use:

- `DJANGO_DEBUG=False`
- strong `DJANGO_SECRET_KEY`
- real `DJANGO_ALLOWED_HOSTS`
- dedicated MySQL credentials
- HTTPS
- `SECURE_SSL_REDIRECT=True` when HTTPS is correctly terminated
- secure cookie settings
- backups and monitoring

## 15. Production deployment checklist

- [ ] Configure production `.env` outside source control
- [ ] Run `python manage.py check --deploy`
- [ ] Run `python manage.py makemigrations --check`
- [ ] Run `python manage.py migrate`
- [ ] Create/verify administrator
- [ ] Configure role groups
- [ ] Configure company information
- [ ] Verify invoice and quotation PDFs
- [ ] Verify GST calculations
- [ ] Verify payment/balance calculations
- [ ] Verify sales/collection reports
- [ ] Verify audit logging
- [ ] Run `pytest`
- [ ] Configure static/media storage
- [ ] Configure HTTPS/reverse proxy
- [ ] Configure database backups
- [ ] Configure log retention/monitoring
- [ ] Verify Docker health checks if using Docker
- [ ] Perform a complete customer → quotation → invoice → payment workflow

## 16. Troubleshooting

### MySQL connection error

Check `DB_HOST`, `DB_PORT`, username, password and that MySQL is listening on port `3306`. Do not put the port into the hostname.

### Missing migrations

Run:

```bash
python manage.py makemigrations
python manage.py migrate
```

Do not use `--run-syncdb` as a substitute for version-controlled migrations in a controlled production deployment.

### Static files

For production, collect static assets with:

```bash
python manage.py collectstatic --noinput
```

### PDF errors

Verify ReportLab is installed from `requirements.txt` and verify company/customer/product data is populated correctly.

## 17. Security notes

- Never commit `.env` or production credentials.
- Use HTTPS in production.
- Use strong, unique Django and database secrets.
- Keep dependencies updated.
- Restrict Django Admin access.
- Apply least-privilege role permissions.
- Do not log passwords, tokens or payment-card data.
- Back up MySQL regularly and test restoration.

## 18. Project repository

GitHub: https://github.com/mdaftabsmu/itgenius-billing-web

## 19. Status

The repository contains the core billing modules, migrations, tests, reporting, audit, REST API, Docker/CI and deployment documentation. **Before declaring a production deployment successful, run the complete validation commands in sections 6 and 13 against the target MySQL environment and resolve any environment-specific failures.**
