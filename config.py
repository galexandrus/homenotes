import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ADMINS = os.environ.get("HOMENOTES_ADMIN").split(", ")


class DevConfig(Config):
    DEBUG = True  # TODO: It's not working


class TestConfig(Config):
    pass


config_select = {
    "default": DevConfig,
    "dev": DevConfig,
    "test": TestConfig,
    "production": Config  # it will be overwritten by a file in the instance_path directory
}
