import logging

from flask_jwt_extended import create_access_token, create_refresh_token  # type: ignore
from werkzeug.security import (  # type: ignore
    check_password_hash,
    generate_password_hash,
)

from crib import exceptions, injection
from crib.domain.user import User

log = logging.getLogger(__name__)


class AuthService(injection.Component):
    user_repository = injection.Dependency()

    def register(self, username, password):
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")

        user = User(username=username, password=generate_password_hash(password))
        self.user_repository.add_user(user)

    def get_tokens(self, username, password):
        if not self._are_credentials_valid(username, password):
            return None

        return {
            "access_token": create_access_token(identity=username),
            "refresh_token": create_refresh_token(identity=username),
            "username": username,
        }

    def _are_credentials_valid(self, username, password):
        try:
            user = self.user_repository(username)
        except exceptions.EntityNotFound:
            return False

        if not check_password_hash(user["password"], password):
            return False

        return True