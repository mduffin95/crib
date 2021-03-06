"""
Simple user repository
"""
import abc
from typing import Any, Dict, Iterable, Type, TypeVar

import pymongo  # type: ignore

import crib
from crib import exceptions, plugins
from crib.domain import User

from . import mongo


class UserRepo(plugins.Plugin):
    @abc.abstractmethod
    def add_user(self, user: User) -> None:
        pass

    @abc.abstractmethod
    def get_user(self, username: str) -> User:
        pass

    @abc.abstractmethod
    def exists(self, username: str) -> bool:
        pass


class MemoryPropertyRepo(UserRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._storage: Dict[str, User] = {}

    def get_user(self, username: str) -> User:
        try:
            return self._storage[username]
        except KeyError:
            raise exceptions.EntityNotFound(username)

    def add_user(self, user: User) -> None:
        if user.username in self._storage:
            raise exceptions.DuplicateProperty(user)
        self._storage[user.username] = user

    def exists(self, username: str) -> bool:
        return username in self._storage


class MongoUserRepo(UserRepo, mongo.MongoRepo):
    @property
    def _users(self):
        return self.db.users

    def _to_user(self, data: Dict[str, Any]) -> User:
        data.pop("_id")
        return User.fromdict(data)

    def exists(self, username: str) -> bool:
        return bool(self._users.find_one({"username": username}))

    def get_user(self, username: str) -> User:
        data = self._users.find_one({"_id": username})
        if data is None:
            raise exceptions.EntityNotFound(username)
        user = self._to_user(data)
        return user

    def add_user(self, user: User) -> None:
        u = user.asdict()
        u["_id"] = user.username
        try:
            self._users.insert_one(u)
        except pymongo.errors.DuplicateKeyError:
            raise exceptions.DuplicateUser(u)


UR = TypeVar("UR", bound=UserRepo)
TUR = Type[UR]


@crib.hookimpl
def crib_add_user_repos() -> Iterable[TUR]:
    return [MemoryPropertyRepo, MongoUserRepo]
