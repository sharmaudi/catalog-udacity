# Flask Debug flag.
DEBUG = True

# Default log level
LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

# Server name is required by Pytest .
SERVER_NAME = 'localhost:8000'

# Flask secret required for session related features.
# Should be overriden using instance properties
SECRET_KEY = 'ASecretStringGoesHere!!'

# Database properties. Override in Instance config.
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/database.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# OAuth config for various providers. Override in instance properties
OAUTH_CONFIG = {
    "GOOGLE": {
        "client_id": "google-client-id",
        "client_secret": "google-client-secret"
    },
    "FACEBOOK": {
        "client_id": "facebook-client-id",
        "client_secret": "facebook-client-secret"
    },
    "GITHUB": {
        "client_id": "github-client-id",
        "client_secret": "github-client-secret"
    }
}

# Disable this for production like environments
OAUTHLIB_INSECURE_TRANSPORT = "1"


# Disable redirect interception.
DEBUG_TB_INTERCEPT_REDIRECTS = False

# pagination
ITEMS_PER_PAGE = 6

# Important properties to override in instance config:
# SECRET_KEY
# OAUTH_CONFIG
# SQLALCHEMY_DATABASE_URI
