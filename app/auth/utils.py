import base64
import hashlib
import os
import secrets

from app.accounts.serializers import UserReadSerializer

from .serializers.token import TokenSerializer


def get_user_auth_data(user, request):
    return {
        "authentication": TokenSerializer(user).data,
        "user": UserReadSerializer(user, context={"request": request}).data,
    }


def generate_secure_code(length: int = 6) -> str:
    digits = "0123456789"
    code = "".join(secrets.choice(digits) for _ in range(length))
    return code


def generate_password_reset_token(length=64):
    # Ensure enough entropy for a 64-character output without padding
    random_bytes = os.urandom(48)  # Larger byte size to accommodate base64 encoding
    salt_bytes = os.urandom(16)

    iterations = 1000

    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", random_bytes, salt_bytes, iterations, dklen=32
    )

    # Convert hash to Base64 without padding
    base64_hash = base64.urlsafe_b64encode(hash_bytes).decode("utf-8").rstrip("=")

    # Ensure the token is exactly 64 characters long
    token = (base64_hash * ((length // len(base64_hash)) + 1))[:length]

    return token
