import os


class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = '19eaaf43ee62588d6746b00f'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///basic_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///production_database.db'
