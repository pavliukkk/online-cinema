import os

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import BaseAppSettings
from config.settings import TestingSettings, Settings
from database import get_db
from notifications import EmailSender, EmailSenderInterface
from repositories.accounts import UserRepository
from security.http import get_token
from security.interfaces import JWTAuthManagerInterface
from security.token_manager import JWTAuthManager
from storages import S3StorageClient, S3StorageInterface

load_dotenv()


def get_settings() -> BaseAppSettings:
    """
    Retrieve the application settings based on the current environment.

    This function reads the 'ENVIRONMENT' environment variable (defaulting to 'developing' if not set)
    and returns a corresponding settings instance. If the environment is 'testing', it returns an instance
    of TestingSettings; otherwise, it returns an instance of Settings.

    Returns:
        BaseAppSettings: The settings instance appropriate for the current environment.
    """
    environment = os.getenv("ENVIRONMENT", "developing")
    if environment == "testing":
        return TestingSettings()
    return Settings()


def get_jwt_auth_manager(settings: BaseAppSettings = Depends(get_settings)) -> JWTAuthManagerInterface:
    """
    Create and return a JWT authentication manager instance.

    This function uses the provided application settings to instantiate a JWTAuthManager, which implements
    the JWTAuthManagerInterface. The manager is configured with secret keys for access and refresh tokens
    as well as the JWT signing algorithm specified in the settings.

    Args:
        settings (BaseAppSettings, optional): The application settings instance.
        Defaults to the output of get_settings().

    Returns:
        JWTAuthManagerInterface: An instance of JWTAuthManager configured with
        the appropriate secret keys and algorithm.
    """
    return JWTAuthManager(
        secret_key_access=settings.SECRET_KEY_ACCESS,
        secret_key_refresh=settings.SECRET_KEY_REFRESH,
        algorithm=settings.JWT_SIGNING_ALGORITHM
    )


def get_user_repository(
        session: AsyncSession = Depends(get_db),
        JWTmanager: JWTAuthManager = Depends(get_jwt_auth_manager),
        token: str = Depends(get_token),
) -> UserRepository:
    return UserRepository(session=session, JWTmanager=JWTmanager, token=token)


def get_s3_storage_client() -> S3StorageInterface:
    endpoint_url = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    bucket_name = os.getenv("MINIO_STORAGE", "online-cinema-bucket")

    return S3StorageClient(
        endpoint_url=endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        bucket_name=bucket_name,
    )


def get_email_notificator() -> EmailSenderInterface:
    email_host = os.getenv("EMAIL_HOST", "localhost")
    email_port = int(os.getenv("EMAIL_PORT", 25))
    email_user = os.getenv("EMAIL_HOST_USER", "testuser")
    email_password = os.getenv("EMAIL_HOST_PASSWORD", "test_password")
    email_use_tls = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"
    return EmailSender(
        hostname=email_host,
        port=email_port,
        email=email_user,
        password=email_password,
        use_tls=email_use_tls,
    )
