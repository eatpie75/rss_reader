import os.path

PROJECT_DIR=os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
	# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
	'default': {
		'ENGINE':	'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME':		'rss',                      # Or path to database file if using sqlite3.
		# The following settings are not used with sqlite3:
		'USER':		'django',
		'PASSWORD':	'ohsocool',
		'HOST':		'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
		'PORT':		'',                      # Set to empty string for default.
		'CONN_MAX_AGE':	600,
	}
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []
INTERNAL_IPS=('127.0.0.1',)

SESSION_COOKIE_NAME='rss_session'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	# 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'fpd4#g2#o!_u67@5#&a)a)rqma&pbe4m@+y*_i@h-ah4qc-*0e'

LOGIN_URL='/login/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django_jinja.loaders.AppLoader',
	'django_jinja.loaders.FileSystemLoader',
)

DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.html.j2'

MIDDLEWARE_CLASSES = (
	'django.middleware.gzip.GZipMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS=(
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.core.context_processors.tz",
	"django.contrib.messages.context_processors.messages",
	"viewer.context_processors.ajax_base",
)

ROOT_URLCONF = 'rssproject.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'rssproject.wsgi.application'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	# 'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	# Uncomment the next line to enable the admin:
	'django.contrib.admin',
	# Uncomment the next line to enable admin documentation:
	# 'django.contrib.admindocs',
	'south',
	'feeds',
	'viewer',
	'django_jinja',
)

DEFAULT_FEED_UPDATE_INTERVAL=60
DEFAULT_ARTICLE_PURGE_INTERVAL=30
PURGE_UNREAD=False

try:
	from settings_local import *
except ImportError:
	pass
