import random as rand
import logging
import functools
import uuid6
from typing import Iterable, List
from pydantic import BaseModel
import socket

import pytest
from pipo_transmuter_spotify.config import settings
from tests import constants


class Helpers:
    def equal_models(m1: BaseModel, m2: BaseModel, attr_exclude: List[str]) -> bool:
        return (
            m1
            and m2
            and (
                m1.model_dump(exclude=attr_exclude)
                == m2.model_dump(exclude=attr_exclude)
            )
        )

    @staticmethod
    def equal_iterables(iter_1: Iterable, iter_2: Iterable):
        return functools.reduce(
            lambda x, y: x and y,
            map(lambda p, q: p == q, iter_1, iter_2),
            True,
        )

    @staticmethod
    def generate_uuid() -> str:
        return str(uuid6.uuid7())

    @staticmethod
    def generate_server_id(prefix: str, size: int) -> str:
        return prefix + str(uuid6.uuid7())[:size]

    @staticmethod
    def get_available_port() -> int:
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port


@pytest.fixture
def helpers():
    return Helpers


@pytest.fixture(scope="session", autouse=True)
def random():
    rand.seed(0)


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(
        FORCE_ENV_FOR_DYNACONF=constants.TEST_ENVIRONMENT,
    )
    logging.basicConfig(
        level=settings.log.level,
        format=settings.log.format,
        encoding=settings.log.encoding,
    )
