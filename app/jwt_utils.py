import os
import jwt

from datetime import datetime, timedelta, timezone


def create_access_token(user_id):
    secret_key = os.environ["JWT_SECRET_KEY"]

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(hours=1)
    }

    token = jwt.encode(
        payload,
        secret_key,
        algorithm="HS256"
    )

    return token

def verify_access_token(token):
    secret_key = os.environ["JWT_SECRET_KEY"]

    payload = jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
        options={"require": ["sub", "iat", "exp"]}
    )

    return payload