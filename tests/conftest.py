import inspect
import os
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import pytest_mock


os.environ["BOT_TOKEN"] = "00000000000000000"

if TYPE_CHECKING:
    # help PyCharm to infer mocker type for autocompletes, real fixture defined in pytest_mock
    @pytest.fixture
    def mocker() -> pytest_mock.MockerFixture:
        return pytest_mock.mocker()


def pytest_collection_modifyitems(session, config, items):
    """
    Mark coroutine functions https://github.com/pytest-dev/pytest-asyncio/issues/61
    """
    for item in items:
        if isinstance(item, pytest.Function) and inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


def pytest_make_parametrize_id(config, val):
    """
    Allow unicode in pytest parametrize
    https://automated-testing.info/t/pytest-krivo-otobrazhaet-kejsy-parametrizaczii-na-russkom/17908
    """
    return repr(val)


@pytest.fixture
def call():
    """
    Simple alias to mock.call
    """
    return mock.call


@pytest.fixture
def hokku_text():
    return "ы " * 17
