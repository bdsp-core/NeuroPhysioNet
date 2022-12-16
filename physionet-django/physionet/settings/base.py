"""
Django settings for project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import fcntl
import logging.config
import os
import sys

from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

ENVIRONMENT = config('ENVIRONMENT', default='production')
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ENABLE_SSO = config('ENABLE_SSO', default=False, cast=bool)
SSO_REMOTE_USER_HEADER = config('SSO_REMOTE_USER_HEADER', default='HTTP_REMOTE_USER')
SSO_LOGIN_BUTTON_TEXT = config('SSO_LOGIN_BUTTON_TEXT', default='Login')


# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'ckeditor',
    # 'django_cron',
    'background_task',

    'user',
    'project',
    'console',
    'export',
    'notification',
    'search',
    'lightwave',
    'physionet',
    'django_sass',
]

if ENABLE_SSO:
    INSTALLED_APPS += ['sso']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'physionet.middleware.maintenance.SystemMaintenanceMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

CRON_CLASSES = [
    "physionet.cron.RemoveUnverifiedEmails",
    "physionet.cron.RemoveOutstandingInvites",
]

ROOT_URLCONF = 'physionet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'physionet.context_processors.access_policy',
                'physionet.context_processors.storage_type',
                'physionet.context_processors.platform_config',
                'sso.context_processors.sso_enabled',
            ],
        },
    },
]

WSGI_APPLICATION = 'physionet.wsgi.application'

# Session management

SESSION_COOKIE_SECURE = True

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'user.validators.ComplexityValidator',
    },
]

AUTHENTICATION_BACKENDS = ['user.backends.DualAuthModelBackend']

if ENABLE_SSO:
    AUTHENTICATION_BACKENDS += ['sso.auth.RemoteUserBackend']

AUTH_USER_MODEL = 'user.User'

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/projects/'

LOGOUT_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Django background tasks max attempts
MAX_ATTEMPTS = 5

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]
# Google Storge service account credentials
if config('GOOGLE_APPLICATION_CREDENTIALS', default=None):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
        BASE_DIR,
        config('GOOGLE_APPLICATION_CREDENTIALS'))

# Maintenance mode

# If true, disable all POSTs and other requests to make changes
SYSTEM_MAINTENANCE_NO_CHANGES = config('SYSTEM_MAINTENANCE_NO_CHANGES',
                                       cast=bool, default=False)
# If true, disable upload functions
SYSTEM_MAINTENANCE_NO_UPLOAD = config('SYSTEM_MAINTENANCE_NO_UPLOAD',
                                      cast=bool, default=False)
# HTML error message displayed during maintenance
SYSTEM_MAINTENANCE_MESSAGE = config('SYSTEM_MAINTENANCE_MESSAGE',
                                    default=None)

# Prevent new applications for credentialed access
PAUSE_CREDENTIALING = config('PAUSE_CREDENTIALING', cast=bool, default=False)
PAUSE_CREDENTIALING_MESSAGE = config('PAUSE_CREDENTIALING_MESSAGE',
                                     default=None)

GCP_DELEGATION_EMAIL = config('GCP_DELEGATION_EMAIL', default=False)

GCP_BUCKET_PREFIX = 'testing-delete.'
GCP_DOMAIN = config('GCP_DOMAIN', default='')

# Alternate hostname to be used in example download commands
BULK_DOWNLOAD_HOSTNAME = config('BULK_DOWNLOAD_HOSTNAME', default=None)

# Header tags for the AWS lambda function that grants access to S3 storage
AWS_HEADER_KEY = config('AWS_KEY', default=False)
AWS_HEADER_VALUE = config('AWS_VALUE', default=False)
AWS_HEADER_KEY2 = config('AWS_KEY2', default=False)
AWS_HEADER_VALUE2 = config('AWS_VALUE2', default=False)
AWS_CLOUD_FORMATION = config('AWS_CLOUD_FORMATION', default=False)

# Tags for the DataCite API used for DOI
DATACITE_API_URL = config('DATACITE_API_URL', default='https://api.test.datacite.org/dois')
DATACITE_PREFIX = config('DATACITE_PREFIX', default='')
DATACITE_USER = config('DATACITE_USER', default='')
DATACITE_PASS = config('DATACITE_PASS', default='')

# Tags for the ORCID API
ORCID_DOMAIN = config('ORCID_DOMAIN', default='https://sandbox.orcid.org')
ORCID_REDIRECT_URI = config('ORCID_REDIRECT_URI', default='http://127.0.0.1:8000/authorcid')
ORCID_AUTH_URL = config('ORCID_AUTH_URL', default='https://sandbox.orcid.org/oauth/authorize')
ORCID_TOKEN_URL = config('ORCID_TOKEN_URL', default='https://sandbox.orcid.org/oauth/token')
ORCID_CLIENT_ID = config('ORCID_CLIENT_ID', default=False)
ORCID_CLIENT_SECRET = config('ORCID_CLIENT_SECRET', default=False)
ORCID_SCOPE = config('ORCID_SCOPE', default=False)

# List of permitted HTML tags and attributes for rich text fields.
# The 'default' configuration permits all of the tags below.  Other
# configurations may be added that permit different sets of tags.

# Attributes that can be added to any HTML tag
_generic_attributes = ['lang', 'title']

# Inline/phrasing content
_inline_tags = {
    'a':      {'attributes': ['href']},
    'abbr':   True,
    'b':      True,
    'bdi':    True,
    'cite':   True,
    'code':   True,
    'dfn':    True,
    'em':     True,
    'i':      True,
    'kbd':    True,
    'q':      True,
    'rb':     True,
    'rp':     True,
    'rt':     True,
    'rtc':    True,
    'ruby':   True,
    's':      True,
    'samp':   True,
    'span':   True,
    'strong': True,
    'sub':    True,
    'sup':    True,
    'time':   True,
    'u':      True,
    'var':    True,
    'wbr':    True,
    'img':    {'attributes': ['alt', 'src', 'height', 'width']},
}
# Block/flow content
_block_tags = {
    # Paragraphs, lists, quotes, line breaks
    'blockquote': True,
    'br':         True,
    'dd':         True,
    'div':        True,
    'dl':         True,
    'dt':         True,
    'li':         {'attributes': ['value']},
    'ol':         {'attributes': ['start', 'type']},
    'p':          True,
    'pre':        True,
    'ul':         True,

    # Tables
    'caption':    True,
    'col':        {'attributes': ['span']},
    'colgroup':   {'attributes': ['span']},
    'table':      {'attributes': ['width']},
    'tbody':      True,
    'td':         {'attributes': ['colspan', 'headers', 'rowspan', 'style'],
                   'styles': ['text-align']},
    'tfoot':      True,
    'th':         {'attributes': ['abbr', 'colspan', 'headers', 'rowspan',
                                  'scope', 'sorted', 'style'],
                   'styles': ['text-align']},
    'thead':      True,
    'tr':         True,
}
# Math content (inline or block)
_math_tags = {
    'math':          {'attributes': ['alttext', 'display']},
    'annotation':    {'attributes': ['encoding']},
    'semantics':     True,

    'maligngroup':   {'attributes': ['groupalign']},
    'malignmark':    {'attributes': ['edge']},
    'menclose':      {'attributes': ['notation']},
    'merror':        True,
    'mfenced':       {'attributes': ['close', 'open', 'separators']},
    'mfrac':         {'attributes': [
        'bevelled', 'numalign', 'denomalign', 'linethickness']},
    'mi':            {'attributes': ['class', 'mathsize', 'mathvariant']},
    'mlabeledtr':    {'attributes': ['rowalign', 'columnalign', 'groupalign']},
    'mmultiscripts': True,
    'mn':            {'attributes': ['class', 'mathsize', 'mathvariant']},
    'mo':            {'attributes': [
        'class', 'accent', 'fence', 'form', 'largeop', 'linebreak',
        'linebreakmultchar', 'linebreakstyle', 'lspace', 'mathsize',
        'mathvariant', 'maxsize', 'minsize', 'movablelimits', 'rspace',
        'separator', 'stretchy', 'symmetric']},
    'mover':         {'attributes': ['accent', 'align']},
    'mpadded':       {'attributes': [
        'depth', 'height', 'lspace', 'voffset', 'width']},
    'mphantom':      True,
    'mprescripts':   True,
    'mroot':         True,
    'mrow':          {'attributes': ['class']},
    'ms':            {'attributes': ['lquote', 'rquote']},
    'mspace':        {'attributes': ['width', 'height', 'depth', 'linebreak']},
    'msqrt':         True,
    'mstyle':        {'attributes': [
        'decimalpoint', 'displaystyle', 'infixlinebreakstyle', 'mathsize',
        'mathvariant', 'scriptlevel', 'scriptsizemultiplier']},
    'msub':          True,
    'msubsup':       True,
    'msup':          True,
    'mtable':        {'attributes': [
        'align', 'alignmentscope', 'columnalign', 'columnlines',
        'columnspacing', 'columnwidth', 'displaystyle', 'equalcolumns',
        'equalrows', 'frame', 'groupalign', 'rowalign', 'rowlines',
        'rowspacing', 'side', 'width']},
    'mtd':           {'attributes': [
        'rowspan', 'columnspan', 'rowalign', 'columnalign', 'groupalign']},
    'mtext':         {'attributes': ['class', 'mathsize', 'mathvariant']},
    'mtr':           {'attributes': ['rowalign', 'columnalign', 'groupalign']},
    'munder':        {'attributes': ['accentunder', 'align']},
    'munderover':    {'attributes': ['accent', 'accentunder', 'align']},
    'none':          True,
}
# Classes used by MathJax (see toMathMLclass() in extensions/toMathML.js)
_math_classes = [
    'MJX-TeXAtom-ORD', 'MJX-TeXAtom-OP', 'MJX-TeXAtom-BIN', 'MJX-TeXAtom-REL',
    'MJX-TeXAtom-OPEN', 'MJX-TeXAtom-CLOSE', 'MJX-TeXAtom-PUNCT',
    'MJX-TeXAtom-INNER', 'MJX-TeXAtom-VCENTER',
    'MJX-fixedlimits', 'MJX-variant',
    'MJX-tex-caligraphic', 'MJX-tex-caligraphic-bold', 'MJX-tex-oldstyle',
    'MJX-tex-oldstyle-bold', 'MJX-tex-mathit',
]

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format'],
            ['Bold', 'Italic', 'Underline', 'Blockquote'],
            ['NumberedList', 'BulletedList'],
            ['InlineEquation', 'BlockEquation', 'CodeSnippet', 'Table'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
        ],
        'removeDialogTabs': 'link:advanced',
        'disableNativeSpellChecker': False,
        'width': '100%',
        'autosave': {'messageType': 'no'},

        # Show options "Heading 2" to "Heading 4" in the format menu,
        # but map these to <h3>, <h4>, <h5> tags
        'format_tags': 'p;h2;h3;h4',
        'format_h2': {'element': 'h3'},
        'format_h3': {'element': 'h4'},
        'format_h4': {'element': 'h5'},

        'extraPlugins': 'codesnippet,pnmathml,autosave',
        'allowedContent': {
            **_inline_tags,
            **_block_tags,
            **_math_tags,
            'h3': True,
            'h4': True,
            'h5': True,
            'h6': True,
            'img': {'attributes': ['src', 'alt', 'width', 'height']},
            '*': {'attributes': _generic_attributes,
                  'classes': _math_classes},
        },
        'mathJaxLib': ('/static/mathjax/MathJax.js'
                       '?config=TeX-AMS-MML_HTMLorMML-full'),
    }

}

# True if the program is invoked as 'manage.py test'
RUNNING_TEST_SUITE = (len(sys.argv) > 1 and sys.argv[1] == 'test')
JSON_LOGGING = config('JSON_LOGGING', default=False, cast=bool)

if RUNNING_TEST_SUITE:
    _logfile = open(os.path.join(BASE_DIR, 'test.log'), 'w')
elif JSON_LOGGING:
    _logfile = sys.stdout
else:
    _logfile = sys.stderr

if JSON_LOGGING:
    _formatter = 'json'
    _simple_formatter = _formatter
    _class = 'logging.StreamHandler'
    _verbose_class = _class
else:
    _formatter = 'console'
    _simple_formatter = 'simple'
    _class = 'logging.StreamHandler'
    _verbose_class = 'physionet.log.VerboseStreamHandler'

LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(asctime)-15s %(message)s',
        },
        'json': {
            'format': '%(created)s %(name)s %(levelname)s %(message)s %(sinfo)s',
            '()': 'physionet.log.UwsgiJsonFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': _class,
            'formatter': _formatter,
            'stream': _logfile,
        },
        'custom_logging': {
            'level': 'INFO',
            'class': _class,
            'formatter': _simple_formatter,
            'stream': _logfile,
        },
        'verbose_console': {
            'class': _verbose_class,
            'formatter': _formatter,
            'stream': _logfile,
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'physionet.log.SaferAdminEmailHandler',
        },
    },
    'loggers': {
        '': {
            'level': LOGLEVEL,
            'handlers': ['console'],
        },
        'user': {
            'level': 'INFO',
            'handlers': ['custom_logging'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['mail_admins'],
            'level': 'CRITICAL',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['verbose_console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'physionet.error': {
            'handlers': ['console', 'mail_admins', 'custom_logging'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

if config('SENTRY_DSN', default=None):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        sample_rate=config('SENTRY_SAMPLE_RATE', default=1.0, cast=float),
        traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.0, cast=float),
        send_default_pii=False
    )

# If this environment variable is set, acquire a shared lock on the
# named file.  The file descriptor is left open, but is
# non-inheritable (close-on-exec), so the lock will be inherited by
# forked child processes, but not by execed programs.
if os.getenv('PHYSIONET_LOCK_FILE'):
    _lockfd = os.open(os.getenv('PHYSIONET_LOCK_FILE'),
                      os.O_RDWR | os.O_CREAT, 0o660)
    # Note that Python has at least three different ways of locking
    # files.  We want fcntl.flock (i.e. flock(2)), which is tied to
    # the file desciptor and inherited by child processes.  In
    # contrast, fcntl.lockf uses fcntl(2) and os.lockf uses lockf(3),
    # both of which are tied to the PID.
    fcntl.flock(_lockfd, fcntl.LOCK_SH)
class StorageTypes:
    LOCAL = 'LOCAL'
    GCP = 'GCP'

STORAGE_TYPE = config('STORAGE_TYPE', default=StorageTypes.LOCAL)
GCP_STORAGE_BUCKET_NAME = config('GCP_MEDIA_BUCKET_NAME')
GCP_STATIC_BUCKET_NAME = config('GCP_STATIC_BUCKET_NAME')

if STORAGE_TYPE == StorageTypes.GCP:
    DEFAULT_FILE_STORAGE = 'physionet.storage.MediaStorage'
    STATICFILES_STORAGE = 'physionet.storage.StaticStorage'
    GCP_BUCKET_LOCATION = config('GCP_BUCKET_LOCATION')
    GS_PROJECT_ID = config('GCP_PROJECT_ID')

SITE_NAME = config('SITE_NAME')
STRAPLINE = config('STRAPLINE')
EMAIL_SIGNATURE = config('EMAIL_SIGNATURE')
FOOTER_MANAGED_BY = config('FOOTER_MANAGED_BY')
FOOTER_SUPPORTED_BY = config('FOOTER_SUPPORTED_BY')
FOOTER_ACCESSIBILITY_PAGE = config('FOOTER_ACCESSIBILITY_PAGE', default=None)

ENABLE_FILE_DOWNLOADS_OPTION = config('ENABLE_FILE_DOWNLOADS_OPTION', cast=bool, default=False)
COPY_FILES_TO_NEW_VERSION = config('COPY_FILES_TO_NEW_VERSION', cast=bool, default=True)

LOG_TIMEDELTA = config('LOG_TIMEDELTA', cast=int, default='10')

# Ticket system for user support
TICKET_SYSTEM_URL = config('TICKET_SYSTEM_URL', default=None)

#  Platform wide citation config
PLATFORM_WIDE_CITATION = {
    'APA': config('PLATFORM_WIDE_CITATION_APA', default=None),
    'MLA': config('PLATFORM_WIDE_CITATION_MLA', default=None),
    'CHICAGO': config('PLATFORM_WIDE_CITATION_CHICAGO', default=None),
    'HARVARD': config('PLATFORM_WIDE_CITATION_HARVARD', default=None),
    'VANCOUVER': config('PLATFORM_WIDE_CITATION_VANCOUVER', default=None),
}

SOURCE_CODE_REPOSITORY_LINK = config('SOURCE_CODE_REPOSITORY_LINK',
                                     default='https://github.com/MIT-LCP/physionet-build')

# User model configurable settings
MAX_ASSOCIATED_EMAILS = config('MAX_ASSOCIATED_EMAILS', cast=int, default=10)
