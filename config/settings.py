from pathlib import Path
import environ
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DJANGO_DEBUG=(bool, True), DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]))
environ.Env.read_env(BASE_DIR / ".env")
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-development-only")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")
INSTALLED_APPS = ["django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles", "rest_framework", "drf_spectacular", "django_filters", "apps.core", "apps.accounts", "apps.dashboard", "apps.customers", "apps.categories", "apps.products", "apps.quotations", "apps.invoices", "apps.payments", "apps.reports", "apps.audit", "apps.api"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware", "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware", "apps.audit.middleware.AuditMiddleware"]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages", "apps.dashboard.context_processors.sidebar"]}}]
DATABASES = {"default": {"ENGINE": "django.db.backends.mysql", "NAME": env("DB_NAME", default="itgenius_billing"), "USER": env("DB_USER", default="billing_user"), "PASSWORD": env("DB_PASSWORD", default=""), "HOST": env("DB_HOST", default="localhost"), "PORT": env("DB_PORT", default="3306"), "OPTIONS": {"charset": "utf8mb4"}}}
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"}, {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"}, {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"}, {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"}]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"
REST_FRAMEWORK = {"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema", "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"], "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"]}
SPECTACULAR_SETTINGS = {"TITLE": "ITGenius Billing API", "DESCRIPTION": "Web billing and invoicing API", "VERSION": "1.0.0"}
LOG_LEVEL = env("LOG_LEVEL", default="INFO")
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOGGING = {"version": 1, "disable_existing_loggers": False, "formatters": {"standard": {"format": "{asctime} | {levelname:<8} | {name} | {message}", "style": "{"}}, "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "standard"}, "application_file": {"class": "logging.handlers.RotatingFileHandler", "filename": LOG_DIR / "application.log", "maxBytes": 10485760, "backupCount": 5, "formatter": "standard"}, "error_file": {"class": "logging.handlers.RotatingFileHandler", "filename": LOG_DIR / "error.log", "maxBytes": 10485760, "backupCount": 5, "formatter": "standard", "level": "ERROR"}}, "loggers": {"django": {"handlers": ["console", "application_file", "error_file"], "level": LOG_LEVEL, "propagate": False}, "billing": {"handlers": ["console", "application_file", "error_file"], "level": LOG_LEVEL, "propagate": False}}}
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
if not DEBUG:
    SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
