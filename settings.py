import os

RECEIVER_EMAIL = 'CODE_SNIPPET_RECIEVER_EMAIL_ADDRESS'
SENDER_EMAIL = 'no-reply@gmail.com'
EMAIL_SUBJECT = 'Google Tag Manager Code Snippet'

# enable/disable sending javascript code snippet in email
SEND_CODE_SNIPPET_EMAIL = True

# SMTP server credentials
SMTP_EMAIL = ''  # example.gmail.com
SMTP_PASSWORD = ''  # ksj*)9900sdf
SMTP_HOST = ''  # smtp.gmail.com
SMTP_PORT = ''  # 587

# enable/disable error traceback
DUBUG = False

# secret key must be in /secrets/ folder. otherwise change directory here
# We are using service account to connect to google tag manager accounts.

# how to create google developer service account?. follow link
# https://developers.google.com/identity/protocols/OAuth2ServiceAccount#creatinganaccount

# where to get google developer project secret key for service account? follow link
# https://console.developers.google.com/permissions/serviceaccounts

# you need to copy your service account email address (ends with @sage-outrider-152712.iam.gserviceaccount.com) and add
# it as admin to your google tag manager account settings and google analytics account settings

# Where to add my service account email to google tag manager settings? Follow link
# https://support.google.com/tagmanager/answer/6107011?hl=en


# Where to add my service account email to google analytics settings? Follow link
# https://support.google.com/analytics/answer/6132368

# NOTE: Add service account email as admin to get access to all entities inside google tag manager account


GOOGLE_DEVELOPER_SECRET_KEY = os.path.join('secrets', 'google_developer_secret.json')


TIME_ZONE_COUNTRY_ID = 'US'
TIME_ZONE_ID = 'America/Los_Angeles'

# possible values: web, android, ios
GOOGLE_TAG_USAGE_CONTEXT = ['web']
