# project/server/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""

    WTF_CSRF_ENABLED = True
    # Note we can use redis as a hostname because it is defined in docker-compose.yml
    REDIS_URL = "redis://redis:6379/0"
    QUEUES = ["default"]


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    WTF_CSRF_ENABLED = False


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
