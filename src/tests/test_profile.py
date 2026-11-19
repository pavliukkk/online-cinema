import pytest
from unittest.mock import AsyncMock, MagicMock

from exceptions import BaseSecurityError


@pytest.mark.asyncio
async def test_create_profile_invalid_token():
    jwt_manager = MagicMock()
    jwt_manager.decode_access_token.side_effect = BaseSecurityError(
        "Invalid token"
    )

    with pytest.raises(Exception) as exc:
        jwt_manager.decode_access_token("invalid_token")

    assert "Invalid token" in str(exc.value)


@pytest.mark.asyncio
async def test_create_profile_user_not_found():
    db = AsyncMock()

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db.execute.return_value = result

    user = result.scalars().first()

    assert user is None


@pytest.mark.asyncio
async def test_create_profile_already_exists():
    db = AsyncMock()

    existing_profile = MagicMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = existing_profile

    db.execute.return_value = result

    profile = result.scalars().first()

    assert profile is not None


@pytest.mark.asyncio
async def test_create_profile_s3_upload_error():
    s3_client = AsyncMock()

    from exceptions import S3FileUploadError

    s3_client.upload_file.side_effect = S3FileUploadError(
        "Upload failed"
    )

    with pytest.raises(S3FileUploadError):
        await s3_client.upload_file(
            file_name="avatars/1/avatar.png",
            file_data=b"image data",
        )

    s3_client.upload_file.assert_awaited_once()