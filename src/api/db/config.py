from decouple import config as decouple_config

# Read settings from the environment or .env; session.py rejects an empty URL.
DATABASE_URL: str = str(decouple_config("DATABASE_URL", default=""))
# Use UTC unless a database connection timezone is explicitly configured.
DB_TIMEZONE: str = str(decouple_config("DB_TIMEZONE", default="UTC"))
