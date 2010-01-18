# Django settings for HQTest project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'      # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'hqtest'       # Or path to database file if using sqlite3.
DATABASE_USER = 'hqtest'       # Not used with sqlite3.
DATABASE_PASSWORD = 'hqtest'   # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# References the django_sites table (and app). In this project, the only use for
# sites is to set the domain name in the password reset email.
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

#
# Code that sets paths to apache, sites, and apps is centralized in a module located in Python's 
# site-packages directory. It's first called in the project's .wsgi file, and then again in a
# project's settings file. This is because the setings file is called standalone from manage.py,
# which needs to be able to find each app's model file(s). Since the apps don't necessarily live
# under the project dir, settings.py can't find all apps unless they're explicitly added to sys.path.
#
import django_path_setup
django_path_setup.set_path()

import os
from common_code.debug_client import console_msg as cm
site_path = os.path.dirname(__file__)
site_template_path = os.path.join(site_path, 'site_templates')

# Apache and Django's runserver mount at different points; check for that here and set
# _PROJECT_MOUNT_POINT accordingly.
#
# DEPENDING ON YOUR WEB SERVER AND OS, YOU WILL HAVE TO CHANGE THIS LOGIC
cwd = os.getcwd()
if 'HQTest' in cwd:
    cm("Running Django's development server")
    _PROJECT_MOUNT_POINT = '/'                    # Local variable name - not known to Django
else:
    cm("Running production web server")
    _PROJECT_MOUNT_POINT = '/HQTest/'             # Local variable name - not known to Django


# Multiple instances of Django running on this one virtual server;
# cookie have to be different on each mount point
SESSION_COOKIE_PATH = _PROJECT_MOUNT_POINT

# This is filled out by calling reverse('login') once the app is up and running.
# Done after all URLConfs are parsed - see HQTest.urls.py
LOGIN_URL = None
# Ditto - set after URLConfs are parsed
LOGIN_REDIRECT_URL = None
   
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# RL: not clear what this is for. Not passed to the template in the RequestContext
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
# RL: this is passed in RequestContext, but it's not clear that I'm using it correctly
MEDIA_URL = '/HQTest/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '37q^d5(k0#_g3w___%9ia+g9r3bm5iz#2%hl1a8^h@u%hya#!0*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (    
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'domain.middleware.DomainMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'HQTest.urls'

INTERNAL_IPS = ('127.0.0.1',)

# This adds the selected domain and count of user's possible domains to the RequestContext object.
# There should be some way to add to this variable dynamically, but all of the web references I've
# seen show it being set statically in settings.py. This is the "default" set, as given in the 1.1
# docs.

TEMPLATE_CONTEXT_PROCESSORS = ( "django.core.context_processors.auth",
                                "django.core.context_processors.debug",
                                "django.core.context_processors.i18n",
                                "django.core.context_processors.media" )
# Not found in 1.1 install:     "django.contrib.messages.context_processors.messages"
# Not used anymore - see file   "apps.domain.context_processors.domain" 


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    site_template_path,
)

# Holds fixtures of apps whos dir that we can't write to (such as django.contrib.auth)
FIXTURE_DIRS = ( os.path.join(site_path, 'fixtures'), )

#
# This is the default set of panels; listed here so they can be turned off later
#
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
#    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
#    'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
#    'HIDE_DJANGO_SQL': False,
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'debug_toolbar',
    'django_tables', # No dadtabase tables associated with this app - could be omitted here 
    'django_granular_permissions',
    'user_registration',  
    'domain',
    'address_book',
)

# For the registration app
ACCOUNT_ACTIVATION_DAYS = 7 # One week to confirm a registered user account

# Test address from which to send email - change in production
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'HQTestGMA'
EMAIL_HOST_PASSWORD = 'YOUR_PASSWORD_HERE'
EMAIL_USE_TLS = True

########################################################################################################
#
# Settings specific to our domain app (+ confidential settings for all apps included at the end)
#

# Not sure where this should live - this is just a temporary home
DOMAIN_MAX_REGISTRATION_REQUESTS_PER_DAY = 99
# Set after URLConfs are parsed
DOMAIN_SELECT_URL  = None 
# If a user tries to access domain admin pages but isn't a domain administrator, here's where he/she
# is redirected
DOMAIN_NOT_ADMIN_REDIRECT_PAGE_NAME = 'homepage'

# These email settings are specific to domain application - if these are present (defined, and not None),
# they're used, else the code attempts to produce a "sensible" default. If you don't know what you're 
# doing here, best to leave them undefined (or None)

#DOMAIN_EMAIL_FROM = None
#DOMAIN_EMAIL_RETURN_PATH = None

# After all other settings have been loaded, we'll bring in the site-specific confidential passwords.
# If this load fails, it simply means that we'll be using the bogus values listed above for some
# important things; can't send email with the above password, for example.

try:
    from settings_confidential import *
except:
    pass
