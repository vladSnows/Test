import os

# App configuration
APP_TITLE = "DMSF Professional App"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")

# Authentication credentials
AUTH_USERS = {
    os.getenv("ADMIN_USER", "admin"): os.getenv("ADMIN_PASS", "admin123"),
    os.getenv("APP_USER", "user"): os.getenv("APP_PASS", "user123")
}

