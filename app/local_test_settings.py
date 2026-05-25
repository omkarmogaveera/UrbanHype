from .settings import *
# Local test overrides to disable HTTPS enforcement for dev checks
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Redirect all outbound emails to the console instead of SMTP
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# No email verification needed — register and immediately log in
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = False
