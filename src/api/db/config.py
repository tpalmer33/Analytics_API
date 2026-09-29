from decouple import config as decouple_config

DATABASE_URL: str = str(decouple_config("DATABASE_URL", default=""))
