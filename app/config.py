# pydantic - python library that validates data types at run time - not later
# clear error not cryptic
# base settings - base class we extend to define config schema
from pydantic_settings import BaseSettings

# our own settings class
class Settings(BaseSettings) :
    database_url: str # these fields are required
    redis_url: str
    secret_key: str
    # optional settings with defaults
    storage_path: str = "/tmp/frappe_stream/storage"
    cdn_backend: str = "local" 

    class Config:
        env_file = ".env" # read from .env file
        # without it pydantic reads from actual system variables - useful in production - docker,cloud deployments etc

# settings instance - runs when module is imported
settings = Settings()


# Singleton pattern -> one shared instance - created once - imported everywhere.
# here, one source of truth for configuration in entire application.