import os

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Ilovecs139'
    DEBUG = False
    TESTING = False
    ENV = 'production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///splitdb.sqlite'
    SQLALCHEMY_ECHO = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'Ihatecs139'


class DevelopmentConfig(Config):
    ENV = 'development'
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = True
    DEBUG = True


class TestingConfig(Config):
    SESSION_COOKIE_SECURE = False
    TESTING = True


class ProductionConfig(Config): 
    pass
