import re
from email import policy
from email.parser import Parser

import httpx
import pytest
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database import (
    ActivationTokenModel,
    UserModel,
    RefreshTokenModel,
    PasswordResetTokenModel,
)


USER_EMAIL = "test@mate.com"
INITIAL_PASSWORD = "StrongPassword123!"
NEW_PASSWORD = "NewSecurePassword123!"

ACTIVATION_URL = "http://127.0.0.1:8000/api/v1/accounts/activate/"
PASSWORD_RESET_URL = (
    "http://127.0.0.1:8000/api/v1/accounts/reset-password/complete/"
)


async def get_mailhog_messages(settings):
    """Отримує повідомлення з MailHog API."""
    mailhog_url = (
        f"http://{settings.EMAIL_HOST}:"
        f"{settings.MAILHOG_API_PORT}/api/v2/messages"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(mailhog_url)

    assert response.status_code == 200, (
        f"MailHog API returned {response.status_code}: {response.text}"
    )

    return response.json().get("items", [])


def get_header(message, header_name):
    """Безпечно отримує значення заголовка листа."""
    headers = message.get("Content", {}).get("Headers", {})
    values = headers.get(header_name, [])

    if isinstance(values, str):
        return values

    if values:
        return values[0]

    return None


def get_email_text(message):
    """
    Витягує звичайний текст із MIME-повідомлення MailHog.

    MailHog Content.Body може містити MIME-частину без зовнішніх
    multipart-заголовків, тому за потреби додаємо їх перед парсингом.
    """
    raw_body = message.get("Content", {}).get("Body", "")

    boundary_match = re.search(
        r"^--([^\r\n]+)",
        raw_body,
        flags=re.MULTILINE,
    )

    if boundary_match:
        boundary = boundary_match.group(1).strip()

        mime_body = (
            "MIME-Version: 1.0\n"
            f'Content-Type: multipart/mixed; boundary="{boundary}"\n'
            "\n"
            f"{raw_body}"
        )
    else:
        mime_body = raw_body

    parsed_message = Parser(policy=policy.default).parsestr(mime_body)

    text_parts = []

    if parsed_message.is_multipart():
        for part in parsed_message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    text_parts.append(part.get_content())
                except (KeyError, LookupError):
                    payload = part.get_payload(decode=True)
                    if payload:
                        text_parts.append(
                            payload.decode(
                                part.get_content_charset() or "utf-8",
                                errors="replace",
                            )
                        )
    else:
        try:
            text_parts.append(parsed_message.get_content())
        except (KeyError, LookupError):
            text_parts.append(raw_body)

    result = "\n".join(text_parts).strip()

    # Якщо MailHog повернув MIME-тіло без коректного зовнішнього
    # multipart-заголовка, не залишаємо MIME-розділювачі в результаті.
    if not result or result.startswith("--"):
        result = re.sub(
            r"(?m)^--[^\r\n]*\r?\n",
            "",
            raw_body,
        )
        result = re.sub(
            r"(?is)^Content-Type:.*?\r?\n"
            r"(?:MIME-Version:.*?\r?\n)?"
            r"(?:Content-Transfer-Encoding:.*?\r?\n)?"
            r"\r?\n",
            "",
            result,
        )
        result = re.sub(r"(?m)^--[^\r\n]*$", "", result)
        result = result.strip()

    return result


def find_email(messages, recipient, subject):
    """Знаходить останній лист за адресатом і темою."""
    matching_messages = [
        message
        for message in messages
        if recipient in (get_header(message, "To") or "")
        and get_header(message, "Subject") == subject
    ]

    if not matching_messages:
        return None

    # MailHog зазвичай повертає нові повідомлення першими.
    return matching_messages[0]


@pytest.mark.e2e
@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_registration(
    e2e_client,
    reset_db_once_for_e2e,
    settings,
    seed_user_groups,
    e2e_db_session,
):
    """
    Перевіряє:
    1. Реєстрацію користувача.
    2. Створення activation token.
    3. Надсилання листа через MailHog.
    4. Адресата, тему та текст листа.
    """
    user_data = {
        "email": USER_EMAIL,
        "password": INITIAL_PASSWORD,
    }

    response = await e2e_client.post(
        "/api/v1/accounts/register/",
        json=user_data,
    )

    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}: {response.text}"
    )

    response_data = response.json()
    assert response_data["email"] == USER_EMAIL

    # Перевіряємо, що користувач створений у базі.
    result = await e2e_db_session.execute(
        select(UserModel).where(UserModel.email == USER_EMAIL)
    )
    user = result.scalars().first()

    assert user is not None, "User was not created!"
    assert user.is_active is False

    # Перевіряємо activation token у базі.
    result = await e2e_db_session.execute(
        select(ActivationTokenModel)
        .where(ActivationTokenModel.user_id == user.id)
    )
    activation_token_record = result.scalars().first()

    assert activation_token_record is not None, (
        "Activation token was not created!"
    )

    activation_token = activation_token_record.token

    # Отримуємо лист із MailHog.
    messages = await get_mailhog_messages(settings)

    email = find_email(
        messages,
        USER_EMAIL,
        "Account Activation",
    )

    assert email is not None, "Activation email was not sent!"

    assert USER_EMAIL in (get_header(email, "To") or "")

    email_body = get_email_text(email)

    assert "activate" in email_body.lower()
    assert "following link" in email_body.lower()
    assert ACTIVATION_URL in email_body
    assert "use this token:" in email_body.lower()
    assert activation_token in email_body

    # Перевіряємо адресу електронної пошти.
    try:
        validate_email(USER_EMAIL)
    except EmailNotValidError as error:
        pytest.fail(f"Invalid email address: {error}")


@pytest.mark.e2e
@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_account_activation(
    e2e_client,
    e2e_db_session,
):
    """
    Перевіряє активацію облікового запису.

    Поточний activate_account endpoint не надсилає окремого
    листа-підтвердження, тому тест перевіряє HTTP-відповідь
    і фактичний стан користувача в базі.
    """
    stmt = (
        select(ActivationTokenModel)
        .join(UserModel)
        .where(UserModel.email == USER_EMAIL)
    )

    result = await e2e_db_session.execute(stmt)
    activation_token_record = result.scalars().first()

    assert activation_token_record is not None, (
        f"Activation token for {USER_EMAIL} not found!"
    )

    token_value = activation_token_record.token

    response = await e2e_client.post(
        "/api/v1/accounts/activate/",
        json={
            "email": USER_EMAIL,
            "token": token_value,
        },
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )

    response_data = response.json()

    assert response_data["message"] == (
        "User account activated successfully."
    )

    # Перевіряємо стан користувача в базі.
    result = await e2e_db_session.execute(
        select(UserModel).where(UserModel.email == USER_EMAIL)
    )
    activated_user = result.scalars().first()

    assert activated_user is not None
    assert activated_user.is_active is True

    # Після активації token має бути видалений.
    result = await e2e_db_session.execute(
        select(ActivationTokenModel)
        .where(ActivationTokenModel.user_id == activated_user.id)
    )
    deleted_token = result.scalars().first()

    assert deleted_token is None, (
        "Activation token was not deleted after activation!"
    )


@pytest.mark.e2e
@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_user_login(
    e2e_client,
    e2e_db_session,
):
    """Перевіряє вхід користувача та збереження refresh token."""
    user_data = {
        "email": USER_EMAIL,
        "password": INITIAL_PASSWORD,
    }

    response = await e2e_client.post(
        "/api/v1/accounts/login/",
        json=user_data,
    )

    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}: {response.text}"
    )

    response_data = response.json()

    assert "access_token" in response_data
    assert "refresh_token" in response_data

    refresh_token = response_data["refresh_token"]

    stmt = (
        select(RefreshTokenModel)
        .options(joinedload(RefreshTokenModel.user))
        .where(RefreshTokenModel.token == refresh_token)
    )

    result = await e2e_db_session.execute(stmt)
    stored_token = result.scalars().first()

    assert stored_token is not None, (
        "Refresh token was not stored in the database!"
    )

    assert stored_token.user.email == USER_EMAIL


@pytest.mark.e2e
@pytest.mark.order(4)
@pytest.mark.asyncio
async def test_request_password_reset(
    e2e_client,
    e2e_db_session,
    settings,
):
    """
    Перевіряє запит на скидання пароля:
    1. Створення password reset token.
    2. Надсилання листа.
    3. Вміст листа та посилання.
    """
    response = await e2e_client.post(
        "/api/v1/accounts/password-reset/request/",
        json={"email": USER_EMAIL},
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )

    response_data = response.json()

    assert response_data["message"] == (
        "If you are registered, you will receive an email with instructions."
    )

    # Перевіряємо створення token у базі.
    stmt = (
        select(PasswordResetTokenModel)
        .join(UserModel)
        .where(UserModel.email == USER_EMAIL)
    )

    result = await e2e_db_session.execute(stmt)
    reset_token_record = result.scalars().first()

    assert reset_token_record is not None, (
        f"Password reset token for {USER_EMAIL} was not created!"
    )

    reset_token = reset_token_record.token

    # Перевіряємо лист у MailHog.
    messages = await get_mailhog_messages(settings)

    email = find_email(
        messages,
        USER_EMAIL,
        "Password Reset Request",
    )

    assert email is not None, "Password reset email was not sent!"

    assert USER_EMAIL in (get_header(email, "To") or "")

    email_body = get_email_text(email)

    assert "password reset" in email_body.lower()
    assert PASSWORD_RESET_URL in email_body
    assert reset_token in email_body


@pytest.mark.e2e
@pytest.mark.order(5)
@pytest.mark.asyncio
async def test_reset_password(
    e2e_client,
    e2e_db_session,
):
    """
    Перевіряє скидання пароля:
    1. Використання валідного token.
    2. Видалення token після використання.
    3. Оновлення пароля користувача.
    """
    stmt = (
        select(PasswordResetTokenModel)
        .join(UserModel)
        .where(UserModel.email == USER_EMAIL)
    )

    result = await e2e_db_session.execute(stmt)
    reset_token_record = result.scalars().first()

    assert reset_token_record is not None, (
        f"Password reset token for {USER_EMAIL} was not found!"
    )

    reset_token = reset_token_record.token
    reset_token_user_id = reset_token_record.user_id

    response = await e2e_client.post(
        "/api/v1/accounts/reset-password/complete/",
        json={
            "email": USER_EMAIL,
            "password": NEW_PASSWORD,
            "token": reset_token,
        },
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )

    response_data = response.json()

    assert response_data["message"] == "Password reset successfully."

    # Перевіряємо, що reset token видалений.
    stmt_deleted = select(PasswordResetTokenModel).where(
        PasswordResetTokenModel.user_id == reset_token_user_id
    )

    deleted_result = await e2e_db_session.execute(stmt_deleted)
    deleted_token = deleted_result.scalars().first()

    assert deleted_token is None, (
        "Password reset token was not deleted after use!"
    )

    # Повторно отримуємо користувача з бази.
    stmt_user = (
        select(UserModel)
        .where(UserModel.email == USER_EMAIL)
        .execution_options(populate_existing=True)
    )

    user_result = await e2e_db_session.execute(stmt_user)
    updated_user = user_result.scalars().first()

    assert updated_user is not None, (
        f"User with email {USER_EMAIL} not found!"
    )

    assert updated_user.verify_password(NEW_PASSWORD), (
        "Password was not updated successfully!"
    )


@pytest.mark.e2e
@pytest.mark.order(6)
@pytest.mark.asyncio
async def test_user_login_with_new_password(
    e2e_client,
    e2e_db_session,
):
    """Перевіряє вхід із новим паролем після його скидання."""
    user_data = {
        "email": USER_EMAIL,
        "password": NEW_PASSWORD,
    }

    response = await e2e_client.post(
        "/api/v1/accounts/login/",
        json=user_data,
    )

    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}: {response.text}"
    )

    response_data = response.json()

    assert "access_token" in response_data
    assert "refresh_token" in response_data

    refresh_token = response_data["refresh_token"]

    stmt = (
        select(RefreshTokenModel)
        .options(joinedload(RefreshTokenModel.user))
        .where(RefreshTokenModel.token == refresh_token)
    )

    result = await e2e_db_session.execute(stmt)
    stored_token = result.scalars().first()

    assert stored_token is not None, (
        "Refresh token was not stored in the database!"
    )

    assert stored_token.user.email == USER_EMAIL
