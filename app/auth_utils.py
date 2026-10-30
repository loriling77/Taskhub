from functools import wraps

import jwt

from flask import request, jsonify, g

from app.jwt_utils import verify_access_token


def jwt_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Missing or invalid Authorization header"
            }), 401

        token = auth_header[len("Bearer "):].strip()

        if not token:
            return jsonify({
                "error": "Missing token"
            }), 401

        try:
            payload = verify_access_token(token)

            user_id = int(payload["sub"])

            if user_id <= 0:
                raise ValueError("Invalid user ID")

        except (jwt.InvalidTokenError, ValueError, KeyError):
            return jsonify({
                "error": "Invalid or expired token"
            }), 401

        g.current_user_id = user_id

        return func(*args, **kwargs)

    return wrapper