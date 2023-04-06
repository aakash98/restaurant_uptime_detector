import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('RESTAURANT_REPORTS_DB_NAME', 'restaurant_reports'),
        'USER': os.environ.get('RESTAURANT_REPORTS_DB_USERNAME', 'restaurant_reports'),
        'PASSWORD': os.environ.get('RESTAURANT_REPORTS_DB_PASSWORD', 'ANSBFJKSKLL!010i2oj'),
        'HOST': os.environ.get('RESTAURANT_REPORTS_DB_HOST', 'localhost'),
        'PORT': os.environ.get('RESTAURANT_REPORTS_DB_PORT', '3306'),
    }
}