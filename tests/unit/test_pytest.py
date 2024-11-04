#!usr/bin/env python3

import asyncio

import pytest

from pipo_transmuter_spotify.config import settings


@pytest.mark.unit
class TestPytest:
    def test_pytest(self):
        assert True

    def test_pytest_configuration(self):
        assert settings.current_env == "test"

    @pytest.mark.asyncio
    async def test_pytest_asyncio(self):
        await asyncio.sleep(0.5)
