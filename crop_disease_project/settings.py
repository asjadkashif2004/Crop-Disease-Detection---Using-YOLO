"""
Django settings for crop_disease_project
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_local_config(name, default=''):
    """
    Reads local settings from environment variables first, then from .env.
    This keeps API keys out of browser code.
    """
    if os.environ.get(name):
        return os.environ[name]

    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        return default

    try:
        for line in env_file.read_text(encoding='utf-8-sig').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            if key.strip() == name:
                return value.strip().strip('"').strip("'")
    except OSError:
        return default

    return default

SECRET_KEY = 'django-insecure-fyp-crop-disease-detection-key-2025'

DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'backend',
    'frontend',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crop_disease_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'crop_disease_project.wsgi.application'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS — allow localhost frontend
CORS_ALLOW_ALL_ORIGINS = True

GROQ_API_KEY = get_local_config('GROQ_API_KEY')
GROQ_MODEL = get_local_config('GROQ_MODEL', 'llama-3.3-70b-versatile')

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}

# ─────────────────────────────────────────────────────────────────
# Trained model weights path
# ─────────────────────────────────────────────────────────────────
MODEL_WEIGHTS_PATH = str(
    BASE_DIR
    / 'Multicrop Disease Dataset'
    / 'runs'
    / 'detect'
    / 'fyp_crop_disease'
    / 'run1'
    / 'weights'
    / 'best.pt'
)